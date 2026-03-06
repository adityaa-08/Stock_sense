import React from 'react';
import './Navbar.css';

export default function Navbar({ page, setPage }) {
  return (
    <nav className="navbar">
      <div className="logo">Stock<span>Sense</span></div>
      <ul>
        <li>
          <a
            href="#"
            className={page === 'home' ? 'active' : ''}
            onClick={e => { e.preventDefault(); setPage('home'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          >Home</a>
        </li>
        <li>
          <a
            href="#"
            className={page === 'analysis' ? 'active' : ''}
            onClick={e => { e.preventDefault(); setPage('analysis'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          >Analyse</a>
        </li>
        <li>
          <a
            href="#"
            className="nav-cta"
            onClick={e => { e.preventDefault(); setPage('analysis'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          >Get Started</a>
        </li>
      </ul>
    </nav>
  );
}
