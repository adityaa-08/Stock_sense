export const BASE_URL = 'http://localhost:8000';

// ── Fetch OHLCV history (returns full candle data, respects period)
export async function fetchStockHistory(symbol, period = '3mo') {
  try {
    const res = await fetch(`${BASE_URL}/stock-history/${symbol}?period=${period}`);
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) return null;
    return data; // [{time, open, high, low, close}, ...]
  } catch (e) {
    console.error('fetchStockHistory error:', e);
    return null;
  }
}

// ── Fetch news — tries stock-specific first, falls back to related search
export async function fetchStockNews(symbol) {
  try {
    const res = await fetch(`${BASE_URL}/stock-news/${symbol}`);
    const data = await res.json();
    if (Array.isArray(data) && data.length > 0) return data;

    // Fallback: search by company name keyword using Yahoo Finance search
    const searchRes = await fetch(`${BASE_URL}/search-stock?q=${encodeURIComponent(symbol)}`);
    const searchData = await searchRes.json();
    const name = searchData?.[0]?.name || symbol;

    // Try fetching news with the company name instead
    const fallbackRes = await fetch(`${BASE_URL}/stock-news/${encodeURIComponent(name.split(' ')[0])}`);
    const fallbackData = await fallbackRes.json();
    return Array.isArray(fallbackData) ? fallbackData : [];
  } catch (e) {
    console.error('fetchStockNews error:', e);
    return [];
  }
}

export async function fetchPortfolioPredict(symbols) {
  const res = await fetch(`${BASE_URL}/portfolio-predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols }),
  });
  return res.json();
}

export async function searchStock(q) {
  try {
    const res = await fetch(`${BASE_URL}/search-stock?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (e) {
    return [];
  }
}

// ── Static UI data
export const tickerItems = [
  { sym:'AAPL', price:'189.42', chg:'▲ 1.2%', up:true },
  { sym:'TSLA', price:'248.75', chg:'▼ 0.8%', up:false },
  { sym:'MSFT', price:'421.30', chg:'▲ 0.5%', up:true },
  { sym:'AMZN', price:'195.60', chg:'▲ 2.1%', up:true },
  { sym:'NVDA', price:'875.20', chg:'▲ 3.4%', up:true },
  { sym:'GOOGL',price:'165.80', chg:'▼ 0.3%', up:false },
  { sym:'META', price:'512.40', chg:'▲ 1.7%', up:true },
  { sym:'NFLX', price:'632.15', chg:'▼ 1.1%', up:false },
];

export const quickPicks = ['AAPL','TSLA','MSFT','NVDA','AMZN','INFY.NS','RELIANCE.NS','TCS.NS'];

export function currencySymbol(sym) {
  return sym && sym.includes('.NS') ? '₹' : '$';
}
