import { useEffect, useState } from 'react';
import About from "./components/About";
import Contact from "./components/Contact";
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Skills from "./components/Skills";
import Work from "./components/Work";
import ChatWindow from "./components/Chatbot/ChatWindow";
import BgAudio from './assets/music/intro-theme18-faster.mp3';

function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [audioPlayed, setAudioPlayed] = useState(false);

  useEffect(() => {
    if (!audioPlayed){
      const audio = new Audio(BgAudio);
      audio.volume = 0.2;
      audio.loop = true;
      

      // Try to play immediately
      audio.play()
      .then(() => {
        setAudioPlayed(true);
      })
      .catch((error => {
        console.log('Audio play error:', error);
        // If autoplay fails, wait for user interaction
        const handleUserInteraction = () => {
          audio.play().then(() => {
            setAudioPlayed(true);
            document.removeEventListener('click', handleUserInteraction);
            document.removeEventListener('keydown', handleUserInteraction);
          });
        };
        document.addEventListener('click', handleUserInteraction);
        document.addEventListener('keydown', handleUserInteraction);
      }));
    }
  }, [audioPlayed]);

  return (
    <div className="App">
      <Navbar />
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
        className="fixed bottom-4 right-4 bg-red-600 text-white p-3 rounded-full shadow-lg z-40"
      >
        {showChatbot ? '✕' : '💬'}
      </button>
      
      {showChatbot && <ChatWindow />}
    </div>
  );
}

export default App;