import "./navbar.css";

function Navbar() {
  return (
    <div className="navbar">
      <div className="navbar-logo">
        <img src="/src/assets/radar.svg" alt="Logo" />
      </div>  
      <a href="/">
        <span className="icon">🏠</span> Home
      </a>
      <a href="/explore">
        <span className="icon">🔍</span> Explore
      </a>
      <a href="/recommended">
        <span className="icon">📡</span> MastoRadar
      </a>
      <a href="/live">
        <span className="icon">🌐</span> Live Feeds
      </a>
      <a href="/favorites">
        <span className="icon">⭐</span> Favorites
      </a>
      <a href="/settings">
        <span className="icon">⚙️</span> Preferences
      </a>
    </div>
  );
}

export default Navbar;