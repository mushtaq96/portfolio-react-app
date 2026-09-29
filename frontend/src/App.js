// src/App.js
import { useEffect, useState, useRef } from 'react';
import About from "./components/About";
import Contact from "./components/Contact";
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Skills from "./components/Skills";
import Work from "./components/Work";
import Experience from "./components/Experience";
import ChatWindow from "./components/Chatbot/ChatWindow";
import BgAudio from './assets/music/intro-theme18-faster.mp3';
import { FaRobot, FaVolumeMute, FaVolumeUp } from 'react-icons/fa';

function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [musicOn, setMusicOn] = useState(false); // Default OFF — no autoplay, no modal.
  const audioRef = useRef(null);

  // User-initiated toggle. Music never plays until the visitor asks for it.
  const toggleMusic = () => {
    if (!audioRef.current) {
      const audio = new Audio(BgAudio);
      audio.volume = 0.2;
      audio.loop = true;
      audioRef.current = audio;
    }

    if (musicOn) {
      audioRef.current.pause();
      setMusicOn(false);
    } else {
      audioRef.current.play()
        .then(() => setMusicOn(true))
        .catch((error) => console.error("Could not play audio:", error));
    }
  };

  // Cleanup on unmount.
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Listen for the custom event to open the chatbot from the Home component.
  useEffect(() => {
    const handleOpenChatbot = () => setShowChatbot(true);
    window.addEventListener('openChatbot', handleOpenChatbot);
    return () => window.removeEventListener('openChatbot', handleOpenChatbot);
  }, []);

  return (
    <div className="App">
      <Navbar />
      <div className="sm:pt-20 md:pt-0 lg:pt-0">
        <Home showChatbot={showChatbot} />
        <About />
        <Experience />
        <Skills />
        <Work />
        <Contact />
      </div>

      {/* Background-music toggle — off by default, bottom-left so it never
          collides with the chatbot controls on the bottom-right. */}
      <button
        onClick={toggleMusic}
        className="fixed bottom-4 left-4 bg-gray-700 hover:bg-gray-600 text-white p-3 rounded-full shadow-lg z-40"
        aria-label={musicOn ? 'Turn background music off' : 'Turn background music on'}
        title={musicOn ? 'Music: on' : 'Music: off'}
      >
        {musicOn ? <FaVolumeUp className="text-xl" /> : <FaVolumeMute className="text-xl" />}
      </button>

      {/* Chatbot toggle button */}
      <button
        onClick={() => setShowChatbot(!showChatbot)}
        className="fixed bottom-4 right-4 bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg z-40 flex items-center transition-all duration-300 transform hover:scale-105 group"
        aria-label={showChatbot ? 'Close Recruiter Assistant' : 'Open Recruiter Assistant'}
      >
        <div className="relative">
          {showChatbot ? (
            <span className="text-xl">✕</span>
          ) : (
            <>
              <FaRobot className="text-xl" />
              <span className="absolute hidden group-hover:block group-focus:block bg-black bg-opacity-70 text-white text-xs rounded py-1 px-2 whitespace-nowrap -top-10 left-1/2 transform -translate-x-1/2 z-50">
                Ask my AI!
              </span>
            </>
          )}
        </div>
      </button>

      {showChatbot && <ChatWindow onClose={() => setShowChatbot(false)} />}
    </div>
  );
}

export default App;
