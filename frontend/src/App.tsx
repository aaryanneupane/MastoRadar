import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './App.css';
import Authenticated from './Authenticated';
import ImageViewer from './ImageViewer';
import Navbar from './Navbar';

interface Post {
  account: {
    display_name: string;
    username: string;
    avatar: string;
    url: string;
  };
  content: string;
  media_attachments: {
    url: string;
    description: string;
  }[];
}

function App() {
  const [data, setData] = useState<Post[]>([]);
  const [maxPages, setMaxPages] = useState(10);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<"Home" | "Explore" | "MastoRadar" | "Live" | "Login" | "Authenticated">('Home');
  const [loggedIn, setLoggedIn] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    console.log("currently logged in:", loggedIn);
    const token = localStorage.getItem("access_token");
    if (token) {
      setLoggedIn(true);
      fetchUser(token).then(({ user_id, username }) => {
        setUserId(user_id);
        setUserName(username);
      });      
      
      console.log("User is logged in with token:", token);
    } else {
      console.log("No access token found, user is not logged in");
      setLoggedIn(false); 
    }

    if (currentPage === 'Home') {
      navigate('/');
      if (loggedIn) {
        console.log('Fetching Home');
        fetcher('/getHomeTimeline');
      }
    } else if (currentPage === 'Explore') {
      console.log('Fetching Explore');
      navigate('/explore');
      fetcher('/getExploreTimeline');
    } else if (currentPage === 'MastoRadar') {
      navigate('/recommended');
      if (loggedIn) {
        console.log('Fetching MastoRadar');
        fetcher('/getRecommendedTimeline');
      }
    } else if (currentPage === 'Live') {
      console.log('Fetching Live Feed (.social)');
      navigate('/live');
      fetcher('/getLocalTimeline');
    } else if (currentPage === 'Login') {
      login();
    }
  }, [maxPages, currentPage]);

  

  const fetcher = async (endpoint: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const resdata: Post[] = await response.json();
      setData(resdata);

    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  const fetchMorePages = () => {
    setMaxPages(maxPages + 10); // Increment by 10 each time "Show More" is clicked
  };

  const selectImage = (imageUrl: string) => setSelectedImage(imageUrl);

  const login = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/login`, {
        method: "GET",
        headers: {
        "Content-Type": "application/json", // Standard header for GET requests
      },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log("Redirecting to authorization page...");
      const authUrl = await response.text();
      const cleanedAuthUrl = authUrl.replace(/^"|"$/g, '');
      window.location.href = cleanedAuthUrl; // Redirect the user to the authorization URL

    } catch (error) {
      console.error("Error sending to authorization page:", error);
    }
  };

  const fetchUser = async (token: String) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/getuser?access_token=${token}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error("Error fetching user:", error);
    }
  }

  const handleLogout = async () => {
    try {
      // Send a POST request to the backend logout endpoint
      const response = await fetch("http://127.0.0.1:8000/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      if (response.ok) {
        console.log("Backend logout successful");
      } else {
        console.error("Failed to log out on backend");
      }
    } catch (error) {
      console.error("Error logging out:", error);
    }
    localStorage.removeItem("access_token"); // Remove token from storage
    setLoggedIn(false);
    setUserId(null);
    setUserName(null);
    setCurrentPage('Explore');
  };

  
  return (
      <div className="app-container">
        <div className="feed-container">
          <Routes>
            <Route path="/" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} loggedIn={loggedIn} title="🏠Home"/>} />
            <Route path="/explore" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} loggedIn={loggedIn} title="🔍Explore"/>} />
            <Route path="/recommended" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} loggedIn={loggedIn} title="📡Recommended"/>} />
            <Route path="/live" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} loggedIn={loggedIn} title="📺Live"/>} />
            <Route path="/login" element={<div>Redirecting to Mastodon...</div>} />
            <Route path="/authenticated" element={<div><Authenticated/></div>} /> 
          </Routes>
        </div>
        <Navbar
        setCurrentPage={setCurrentPage}
        loggedIn={loggedIn}
        userId={userId}
        userName={userName}
        handleLogout={handleLogout}
        />
      </div>
  );
}

const Feed = ({
  data,
  selectImage,
  selectedImage,
  setSelectedImage,
  fetchMorePages,
  title,
  loggedIn,
}: {
  data: Post[];
  selectImage: (imageUrl: string) => void;
  selectedImage: string | null;
  setSelectedImage: (imageUrl: string | null) => void;
  fetchMorePages: () => void;
  title: string;
  loggedIn: boolean;
}) => {
  // Determine if the tab requires login
  const requiresLogin = title === "📡Recommended" || title === "🏠Home";
  const isDisabled = requiresLogin && !loggedIn;

  return (
    <div
      className={`max-w-2xl mx-auto py-5 px-4 rounded-lg border shadow-lg ${
        isDisabled
          ? "text-gray-500 border-gray-500 opacity-50 pointer-events-none"
          : "text-white border-gray-800"
      }`}
    >
      {/* Title */}
      <h1 className="text-3xl font-bold text-center mb-6">
        {isDisabled ? `${title} (Please log in)` : title}
      </h1>

      {/* Content */}
      {isDisabled ? (
        <p className="text-center mt-4">Please log in to view this content.</p>
      ) : (
        <>
          {data.map((post, index) => (
            <div
              key={index}
              className="post bg-gray-800 p-6 rounded-md border border-gray-700 shadow-sm mb-6 transition-all"
            >
              <div className="flex items-center mb-4">
                <img
                  className="h-12 w-12 rounded-full mr-3 border border-gray-600"
                  src={post.account.avatar}
                  alt={post.account.display_name}
                />
                <div className="flex flex-col">
                  <h2 className="text-lg font-bold">{post.account.display_name}</h2>
                  <p className="text-sm text-gray-400">@{post.account.username}</p>
                </div>
              </div>
              <div dangerouslySetInnerHTML={{ __html: post.content }} />
              {post.media_attachments.map((media, idx) => (
                <img
                  key={idx}
                  src={media.url}
                  alt={media.description}
                  className="mt-4 rounded-md"
                  onClick={() => selectImage(media.url)}
                />
              ))}
            </div>
          ))}
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded-lg mt-6 hover:bg-blue-600 transition-colors font-semibold"
            onClick={fetchMorePages}
          >
            Show More
          </button>
          {selectedImage && (
            <ImageViewer imageUrl={selectedImage} onClose={() => setSelectedImage(null)} />
          )}
        </>
      )}
    </div>  

  );
};


export default App;