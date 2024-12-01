import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
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
  const [currentPage, setCurrentPage] = useState<"Home" | "Explore" | "MastoRadar" | "Live" | "Login">('Home');

  useEffect(() => {
    if (currentPage === 'Home') {
      console.log('Fetching Home');
      fetcher('/getHomeTimeline');
    } else if (currentPage === 'Explore') {
      console.log('Fetching Explore');
      //No direct API endpint for Explore, so we fetch the Public Timeline instead
      fetcher('/getPublicTimeline');
    } else if (currentPage === 'MastoRadar') {
      fetcher('/getRecommendedTimeline');
      //TODO: Implement Recommender System
    } else if (currentPage === 'Live') {
      console.log('Fetching Live Feed (.social)');
      fetcher('/getLocalTimeline');
    } else if (currentPage === 'Login') {
      login('/login');
    }
  }, [maxPages, currentPage]);

  const fetcher = async (endpoint: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        headers: {
          'Access-Control-Allow-Origin': '*',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (endpoint == '/login') {
        console.log("Redirecting to authorization page...");
        const authUrl = await response.text();
        console.log(authUrl);
        window.location.href = authUrl;
      } else {
      const resdata: Post[] = await response.json();
      setData(resdata);
      }

    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  const fetchMorePages = () => {
    setMaxPages(maxPages + 10); // Increment by 10 each time "Show More" is clicked
  };

  const selectImage = (imageUrl: string) => setSelectedImage(imageUrl);

  const login = async (endpoint: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        headers: {
          'Access-Control-Allow-Origin': '*',
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


  return (
    <Router>
      <div className="app-container">
        <div className="feed-container">
          <Routes>
            <Route path="/" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} title="🏠Home"/>} />
            <Route path="/explore" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} title="🔍Explore"/>} />
            <Route path="/recommended" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} title="📡Recommended"/>} />
            <Route path="/live" element={<Feed data={data} selectImage={selectImage} selectedImage={selectedImage} setSelectedImage={setSelectedImage} fetchMorePages={fetchMorePages} title="📺Live"/>} />
            <Route path="login" element={<div>Log In</div>} />
          </Routes>
        </div>
        <Navbar setCurrentPage={setCurrentPage}/>
      </div>
    </Router>
  );
}

const Feed = ({ data, selectImage, selectedImage, setSelectedImage, fetchMorePages, title }: { data: Post[], selectImage: (imageUrl: string) => void, selectedImage: (string | null), setSelectedImage: (imageUrl: string | null) => void, fetchMorePages: () => void, title: string }) => (
  <div className="max-w-2xl mx-auto py-5 px-4 text-white rounded-lg border border-gray-800 shadow-lg">
    <h1 className="text-3xl font-bold text-center mb-6 text-white">{title}</h1>
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
          //TODO: add interraction elements
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
  </div>
);

export default App;