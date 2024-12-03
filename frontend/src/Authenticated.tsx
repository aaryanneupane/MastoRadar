import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Authenticated = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Parse the access token from the URL
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    console.log("Params:", params);

    if (accessToken) {
      // Store the access token in localStorage
      localStorage.setItem("access_token", accessToken);

      // Redirect to the main page
      navigate("/");  
    } else {
      console.error("Access token not found in URL");
    }
  }, [navigate]);

  return <div>Processing authentication...</div>;
};

export default Authenticated;