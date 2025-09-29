// src/App.js
import { useEffect, useState, useRef } from 'react';
import About from "./components/About";
import Contact from "./components/Contact";
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Skills from "./components/Skills";
import Work from "./components/Work";
import ChatWindow from "./components/Chatbot/ChatWindow";
import MusicConsentModal from "./components/MusicConsentModal"; // Import the new component
import BgAudio from './assets/music/intro-theme18-faster.mp3';
import { FaRobot } from 'react-icons/fa';

function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [audioPlayed, setAudioPlayed] = useState(false); // Tracks if we've attempted to play or user declined
  const audioRef = useRef(null); // To hold the audio instance

  // Handle the user accepting music
  const handleAcceptMusic = () => {
    console.log("User accepted background music.");

    // Create and play the audio. The button click counts as user interaction.
    const audio = new Audio(BgAudio);
    audio.volume = 0.2;
    audio.loop = true;
    audioRef.current = audio; // Store reference

    audio.play()
      .then(() => {
        console.log("Background music started playing.");
        setAudioPlayed(true); // Mark as successfully played
      })
      .catch((error) => {
        console.error("Failed to play audio even after user click:", error);
        // Even if it fails, mark as played to prevent re-prompting/trying
        setAudioPlayed(true);
      });
  };

  // Handle the user declining music
  const handleDeclineMusic = () => {
    console.log("User declined background music.");
    setAudioPlayed(true); // Mark as handled (don't ask again)
  };

  // Cleanup on unmount (e.g., if user navigates away quickly)
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

// Listen for the custom event to open the chatbot from Home component
  useEffect(() => {
    const handleOpenChatbot = () => setShowChatbot(true);
    window.addEventListener('openChatbot', handleOpenChatbot);
    return () => window.removeEventListener('openChatbot', handleOpenChatbot);
}, []);

  return (
    <div className="App">
      <Navbar />
      {/* Render the custom modal */}
      <MusicConsentModal
        isOpen={!audioPlayed} // Show if we haven't played or been declined
        onAccept={handleAcceptMusic}
        onDecline={handleDeclineMusic}
      />
      <div className="sm:pt-20 md:pt-0 lg:pt-0">
        <Home />
        <About />
        <Skills />
        <Work />
        <Contact />
      </div>

      {/* Chatbot toggle button */}
<button
  onClick={() => setShowChatbot(!showChatbot)}
  className="fixed bottom-4 right-4 bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg z-40 flex items-center transition-all duration-300 transform hover:scale-105 group" // Added group, transition, transform, hover:scale
  aria-label={showChatbot ? 'Close Recruiter Assistant' : 'Open Recruiter Assistant'}
>
  <div className="relative">
    {showChatbot ? (
      <span className="text-xl">✕</span>
    ) : (
      <>
        <FaRobot className="text-xl" />
        {/* Tooltip/Label - hidden by default, shown on hover/focus */}
        <span className="absolute hidden group-hover:block group-focus:block bg-black bg-opacity-70 text-white text-xs rounded py-1 px-2 whitespace-nowrap -top-10 left-1/2 transform -translate-x-1/2 z-50">
          Ask my AI!
        </span>
      </>
    )}
  </div>
</button>

      {showChatbot && <ChatWindow onClose={() => setShowChatbot(false)}/>}
    </div>
  );
}

export default App;