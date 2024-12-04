import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";


interface AuthenticatedProps {
  setCurrentPage: (page: "Home" | "Explore" | "MastoRadar" | "Recommended Ultra" | "Live" | "Login") => void;
}

const Authenticated: React.FC<AuthenticatedProps> = ({ setCurrentPage }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      console.log("Access token already stored, redirecting to Home...");
      setCurrentPage("Home");
      return;
    }
    
    // Parse the access token from the URL
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    console.log("Params:", params);

    if (accessToken) {
      // Store the access token in localStorage
      localStorage.setItem("access_token", accessToken);

      // Redirect to the main page
      console.log("Redirecting now...");
      setCurrentPage("Home");
    } else {
      console.error("Access token not found in URL");
    }
  }, [navigate]);

  return <div>Processing authentication...</div>;
};

export default Authenticated;