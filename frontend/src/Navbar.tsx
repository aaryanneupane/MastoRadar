import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

interface NavbarProps {
  setCurrentPage: (page: "Home" | "Explore" | "MastoRadar" | "Live" | "Login") => void;
}

const Navbar: React.FC<NavbarProps> = ({ setCurrentPage }) => {
  return (
    <nav className="navbar">
      <Link className="navbar-logo" to="/">
          <img src="src/assets/radar.svg" alt="Logo" />
        </Link>
      <ul className="navbar-links">
        <li><Link to="/" onClick={() => setCurrentPage("Home")}><span className="icon">🏠</span> Home</Link></li>
        <li><Link to="/explore" onClick={() => setCurrentPage("Explore")}><span className="icon">🔍</span> Explore</Link></li>
        <li><Link to="/recommended" onClick={() => setCurrentPage("MastoRadar")}><span className="icon">📡</span> MastoRadar</Link></li>
        <li><Link to="/live" onClick={() => setCurrentPage("Live")}><span className="icon">📺</span> Live Feed</Link></li>
        <li><Link to="/login" onClick={() => setCurrentPage("Login")}><span className="icon">🔒</span> Log In</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;