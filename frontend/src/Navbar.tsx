import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

interface NavbarProps {
  setCurrentPage: (page: "Home" | "Explore" | "MastoRadar" | "Live" | "Login") => void;
  loggedIn: boolean;
  userId: string | null;
  userName: string | null;
  handleLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({
  setCurrentPage,
  loggedIn,
  userId,
  userName,
  handleLogout,
}: {
  setCurrentPage: (page: "Home" | "Explore" | "MastoRadar" | "Live" | "Login") => void;
  loggedIn: boolean;
  userId: string | null;
  userName: string | null;
  handleLogout: () => void; }) => {
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
        <div className="nav-item login-status">
        {loggedIn ? (
          <div className="user-info">
            <button className="logout-button" onClick={handleLogout}>
              Log Out
            </button>
            <p className="user-name">{userName ? `Logged in as: ${userName}` : "Loading..."}</p>
          </div>
        ) : (
          <Link to="/login" onClick={() => setCurrentPage("Login")}>
            <button className="login-button">Log In</button>
          </Link>
        )}
      </div>
      </ul>
    </nav>
  );
};

export default Navbar;