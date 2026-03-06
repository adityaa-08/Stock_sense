import React, { useState, useRef } from 'react';
import PriceChart from '../components/PriceChart';
import {
  fetchPortfolioPredict,
  fetchStockHistory,
  fetchStockNews,
  quickPicks,
  currencySymbol,
} from '../data/stockData';
import './AnalysisPage.css';

const LOADING_STEPS = [
  'Fetching market data...',
  'Running LSTM prediction model...',
  'Analysing sentiment...',
  'Computing portfolio allocation...',
  'Building dashboard...',
];

const PERIODS = [
  { label: '1 Month',  value: '1mo' },
  { label: '3 Months', value: '3mo' },
  { label: '6 Months', value: '6mo' },
  { label: '1 Year',   value: '1y'  },
];

export default function AnalysisPage() {
  const [ticker, setTicker]   = useState('');
  const [period, setPeriod]   = useState('3mo');
  const [loading, setLoading] = useState(false);
  const [loadText, setLoadText] = useState('');
  const [result, setResult]   = useState(null);
  const [candles, setCandles] = useState(null);
  const [news, setNews]       = useState([]);
  const [error, setError]     = useState(null);
  const timerRef              = useRef(null);
  const lastSym               = useRef('');

  async function runAnalysis(sym, per) {
    const raw = (sym || ticker).trim().toUpperCase();
    if (!raw) return;
    const usePeriod = per || period;
    setTicker(raw);
    lastSym.current = raw;
    setResult(null);
    setError(null);
    setLoading(true);

    let si = 0;
    setLoadText(LOADING_STEPS[0]);
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      si++;
      setLoadText(LOADING_STEPS[Math.min(si, LOADING_STEPS.length - 1)]);
    }, 600);

    try {
      const [predictData, candleData, newsData] = await Promise.all([
        fetchPortfolioPredict([raw]),
        fetchStockHistory(raw, usePeriod),
        fetchStockNews(raw),
      ]);

      clearInterval(timerRef.current);

      if (predictData.error) {
        setError(predictData.error);
        setLoading(false);
        return;
      }

      const asset = predictData.portfolio_allocation?.[0];
      if (!asset) {
        setError('No data returned for this symbol.');
        setLoading(false);
        return;
      }

      setCandles(candleData);
      setNews(newsData);
      setResult({ sym: raw, ...asset });
    } catch (e) {
      clearInterval(timerRef.current);
      setError('Cannot connect to backend. Make sure the Python server is running on port 8000.');
    }

    setLoading(false);
  }

  // When period changes and a stock is already loaded, refetch chart only
  async function handlePeriodChange(newPeriod) {
    setPeriod(newPeriod);
    if (!lastSym.current) return;
    const data = await fetchStockHistory(lastSym.current, newPeriod);
    setCandles(data);
  }

  const cur      = result ? currencySymbol(result.sym) : '$';
  const isUp     = result && result.predicted_price >= result.current_price;
  const sentScore = result ? Math.round(((result.news_sentiment_avg + 1) / 2) * 100) : 0;
  const priceDiff = result
    ? ((result.predicted_price - result.current_price) / result.current_price * 100).toFixed(2)
    : 0;

  const indicators = result ? [
    { k: 'Predicted Change',     v: `${priceDiff > 0 ? '+' : ''}${priceDiff}%`,       pct: Math.min(Math.abs(priceDiff) * 10, 100) },
    { k: 'News Sentiment Avg',   v: result.news_sentiment_avg?.toFixed(4),             pct: Math.round(((result.news_sentiment_avg + 1) / 2) * 100) },
    { k: 'Sentiment Volatility', v: result.news_sentiment_volatility?.toFixed(4),      pct: Math.min(result.news_sentiment_volatility * 100, 100) },
    { k: 'Trend Score',          v: result.trend_score?.toFixed(4),                    pct: Math.round(((result.trend_score + 1) / 2) * 100) },
    { k: 'Portfolio Weight',     v: `${(result.allocation_weight * 100).toFixed(1)}%`, pct: Math.round(result.allocation_weight * 100) },
  ] : [];

  const stats = result?.company_stats || {};

  return (
    <div className="analysis-page">
      <div className="analysis-header">
        <div className="section-label">Analysis Dashboard</div>
        <h1>Stock Analysis</h1>
        <p>Powered by LSTM predictions, DQN portfolio allocation &amp; live sentiment analysis.</p>
      </div>

      {/* Search */}
      <div className="search-row">
        <div className="search-box">
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            type="text"
            placeholder="e.g. AAPL, TSLA, INFY.NS"
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && runAnalysis()}
            maxLength={15}
          />
        </div>
        <select
          className="filter-sel"
          value={period}
          onChange={e => handlePeriodChange(e.target.value)}
        >
          {PERIODS.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        <button className="btn-analyse" onClick={() => runAnalysis()}>Analyse →</button>
      </div>

      {/* Quick picks */}
      <div className="quick-label">QUICK PICKS</div>
      <div className="quick-picks">
        {quickPicks.map(sym => (
          <span key={sym} className="quick-chip" onClick={() => runAnalysis(sym)}>
            {sym.replace('.NS', '')}
          </span>
        ))}
      </div>

      {/* Error */}
      {error && <div className="error-box">⚠ {error}</div>}

      {/* Loading */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
          <div className="loading-text">{loadText}</div>
        </div>
      )}

      {/* Dashboard */}
      {result && !loading && (
        <div className="dashboard">

          {/* Overview */}
          <div className="card full">
            <div className="card-title">Overview</div>
            <div className="overview-row">
              <div>
                <div className="stock-name">{result.sym}</div>
                <div className="stock-full">
                  {stats.sector || stats.industry || result.sym}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="price-big">{cur}{result.current_price?.toLocaleString()}</div>
                <div className={`price-change ${isUp ? 'up' : 'dn'}`}>
                  Predicted: {cur}{result.predicted_price?.toFixed(2)}
                  {' '}({priceDiff > 0 ? '+' : ''}{priceDiff}%)
                </div>
              </div>
            </div>
            <div className="overview-stats">
              <div className="ov-stat">
                <div className="lbl">Market Cap</div>
                <div className="v">{stats.market_cap ? `${cur}${(stats.market_cap/1e9).toFixed(1)}B` : 'N/A'}</div>
              </div>
              <div className="ov-stat">
                <div className="lbl">P/E Ratio</div>
                <div className="v">{stats.pe_ratio ? Number(stats.pe_ratio).toFixed(1)+'x' : 'N/A'}</div>
              </div>
              <div className="ov-stat">
                <div className="lbl">52W High</div>
                <div className="v">{stats['52_week_high'] ? `${cur}${stats['52_week_high']}` : 'N/A'}</div>
              </div>
              <div className="ov-stat">
                <div className="lbl">52W Low</div>
                <div className="v">{stats['52_week_low'] ? `${cur}${stats['52_week_low']}` : 'N/A'}</div>
              </div>
            </div>
          </div>

          {/* Candlestick Chart */}
          <div className="card">
            <div className="card-title" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span>Candlestick Chart</span>
              <div style={{display:'flex',gap:'0.5rem'}}>
                {PERIODS.map(p => (
                  <span
                    key={p.value}
                    className={`period-btn ${period === p.value ? 'active' : ''}`}
                    onClick={() => handlePeriodChange(p.value)}
                  >{p.label.split(' ')[0]}{p.label.includes('Month') ? 'M' : 'Y'}</span>
                ))}
              </div>
            </div>
            {candles && candles.length > 0
              ? <PriceChart candles={candles} />
              : <div className="no-data">No chart data available</div>
            }
            <div style={{display:'flex',gap:'1.5rem',marginTop:'0.8rem'}}>
              <span style={{fontFamily:'DM Mono,monospace',fontSize:'0.72rem',color:'var(--up)'}}>▮ Bullish</span>
              <span style={{fontFamily:'DM Mono,monospace',fontSize:'0.72rem',color:'var(--down)'}}>▮ Bearish</span>
            </div>
          </div>

          {/* Sentiment */}
          <div className="card">
            <div className="card-title">Market Sentiment</div>
            <div className="sentiment-gauge">
              <div className="gauge-wrap">
                <svg viewBox="0 0 160 90" className="gauge-svg">
                  <defs>
                    <linearGradient id="gauge-grad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#ff4757"/>
                      <stop offset="50%" stopColor="#ffa502"/>
                      <stop offset="100%" stopColor="#00d4aa"/>
                    </linearGradient>
                  </defs>
                  <path d="M 15 85 A 65 65 0 0 1 145 85" fill="none" stroke="#1a2d42" strokeWidth="10" strokeLinecap="round"/>
                  <path d="M 15 85 A 65 65 0 0 1 145 85" fill="none" stroke="url(#gauge-grad)" strokeWidth="10" strokeLinecap="round" opacity="0.4"/>
                  <line
                    x1="80" y1="85"
                    x2={80 + 55 * Math.cos(Math.PI - (sentScore / 100) * Math.PI)}
                    y2={85 - 55 * Math.sin((sentScore / 100) * Math.PI)}
                    stroke="#e8f0f7" strokeWidth="2.5" strokeLinecap="round"
                  />
                  <circle cx="80" cy="85" r="5" fill="#e8f0f7"/>
                </svg>
              </div>
              <div className="sentiment-val" style={{ color: sentScore >= 60 ? 'var(--up)' : sentScore >= 40 ? 'var(--text)' : 'var(--down)' }}>
                {sentScore}/100
              </div>
              <div className="sentiment-label">
                {sentScore >= 60 ? 'Bullish Sentiment' : sentScore >= 40 ? 'Neutral Sentiment' : 'Bearish Sentiment'}
              </div>
            </div>
          </div>

          {/* Prediction */}
          <div className="card">
            <div className="card-title">LSTM + DQN Prediction</div>
            <div className="prediction-row">
              <div className={`pred-box ${isUp ? 'bull' : 'bear'}`}>
                <div className="pred-dir">{isUp ? '🐂' : '🐻'}</div>
                <div className="pred-pct">{cur}{result.predicted_price?.toFixed(2)}</div>
                <div className="pred-lbl">Predicted Price</div>
              </div>
              <div className="pred-box" style={{borderColor:'rgba(255,165,0,0.3)',background:'rgba(255,165,0,0.05)'}}>
                <div className="pred-dir">⚖️</div>
                <div className="pred-pct">{(result.allocation_weight * 100).toFixed(1)}%</div>
                <div className="pred-lbl">Portfolio Weight</div>
              </div>
            </div>
            <div style={{marginTop:'0.8rem'}}>
              <div style={{display:'flex',justifyContent:'space-between',marginBottom:'0.4rem'}}>
                <span className="conf-label">Trend Score</span>
                <span className="conf-val-text">{result.trend_score?.toFixed(3)}</span>
              </div>
              <div className="confidence-bar">
                <div className="confidence-fill" style={{width:`${Math.round(((result.trend_score+1)/2)*100)}%`}}/>
              </div>
            </div>
            <div className="signal-box">
              <div className="signal-lbl">DECISION</div>
              <div className="signal-val" style={{
                color: result.decision==='BUY' ? 'var(--up)' : result.decision==='SELL' ? 'var(--down)' : 'var(--text)'
              }}>
                {result.decision}
              </div>
            </div>
          </div>

          {/* Indicators */}
          <div className="card">
            <div className="card-title">Analysis Metrics</div>
            <div className="metrics-list">
              {indicators.map((m, i) => (
                <div key={i}>
                  <div className="metric-row">
                    <span className="mk">{m.k}</span>
                    <span className="mv">{m.v}</span>
                  </div>
                  <div className="metric-bar-wrap">
                    <div className="metric-bar-fill" style={{width:`${Math.max(0,Math.min(100,m.pct))}%`}}/>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* News */}
          <div className="card full">
            <div className="card-title">
              Latest News
              {news.length === 0 && <span style={{color:'var(--muted)',fontWeight:400,marginLeft:'0.5rem'}}>(showing related results)</span>}
            </div>
            {news.length > 0 ? (
              <div className="news-list">
                {news.map((n, i) => (
                  <a className="news-item" key={i} href={n.url} target="_blank" rel="noopener noreferrer">
                    <div className="news-dot pos"/>
                    <div>
                      <div className="news-text">{n.title}</div>
                      <div className="news-meta">{n.source} · Live</div>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <div className="no-data">No news found for this symbol.</div>
            )}
          </div>

        </div>
      )}

      <footer className="analysis-footer">
        <div className="logo-footer">Stock<span>Sense</span></div>
        <p>Powered by LSTM · DQN · Sentiment Analysis · FastAPI</p>
        <p>Not financial advice.</p>
      </footer>
    </div>
  );
}
