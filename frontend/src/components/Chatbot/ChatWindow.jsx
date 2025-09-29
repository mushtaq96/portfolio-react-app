// src/components/Chatbot/ChatWindow.jsx``

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import VoiceButton from './VoiceButton';
import {FaFlagUsa, FaFlag} from 'react-icons/fa'; 
import { FaRobot } from 'react-icons/fa'; 

const getApiBaseUrl = () => {
  // Check environment variable first
  if (process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }
  
  // In production, use Render backend URL (update this after deployment)
  if (process.env.NODE_ENV === 'production') {
    return 'https://portfolio-react-app-ed20.onrender.com'; // Update after deployment
  }
  
  // Default to localhost for development
  return 'http://localhost:8000';
};

// --- 1. Use Environment Variable for API Base URL ---
const API_BASE_URL = getApiBaseUrl();

const ChatWindow = ({ onClose }) => { // Accept onClose prop for communication
  const [messages, setMessages] = useState([
    {
      text: "Hi, I'm Mushtaq's AI assistant. Ask me about his skills, experience, or projects!",
      sender: 'bot-welcome'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // --- 2. Improved Error Handling & Fallback Responses ---
  const handleSend = async (messageText = null) => { // Accept optional message text
    // Use provided text (e.g., from voice) or the input state
    const textToSend = messageText !== null ? messageText : input;

    if (!textToSend.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage = { text: textToSend, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);

    // Clear the input field only if the message came from the input field
    if (messageText === null) {
      setInput('');
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, { 
        message: textToSend,
        history: messages,
        language
      });
      setMessages(prev => [...prev, {
        text: response.data.response,
        sender: 'bot',
        context: response.data.context
      }]);

      // --- Add Text-to-Speech ---
      if (response.data.response && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.data.response);
        utterance.lang = language === 'de' ? 'de-DE' : 'en-US';
        utterance.volume = 1;
        utterance.rate = 1;
        utterance.pitch = 1;
        // Optional: Try to find a specific voice
        const voices = window.speechSynthesis.getVoices();
        const desiredVoice = voices.find(voice => voice.lang === utterance.lang);
        if (desiredVoice) {
          utterance.voice = desiredVoice;
        }
        window.speechSynthesis.speak(utterance);
      }
      // --- End Text-to-Speech ---
    } catch (error) {
      console.error('Chat error:', error);
      let fallbackResponse = "Sorry, I'm having trouble connecting right now. Please try again later or reach out via email.";

      // --- Specific Error Messages ---
      if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {
        fallbackResponse = "The request took too long. Please check your connection or try again.";
      } else if (!error.response) {
        // Network error (e.g., backend down)
        fallbackResponse = "The AI assistant seems to be offline at the moment. You can email me directly at mushtaq96smb@gmail.com!";

        // --- Graceful Degradation Example ---
        const lowerInput = textToSend.toLowerCase();
        if (lowerInput.includes('experience') || lowerInput.includes('work')) {
          fallbackResponse = "I have experience in Full-Stack Development (React, Node.js, Python) and AI/ML (Deep Learning, NLP). Check out my 'Work' section for project details!";
        } else if (lowerInput.includes('contact') || lowerInput.includes('email')) {
          fallbackResponse = "You can reach me directly at mushtaq96smb@gmail.com!";
        } else if (lowerInput.includes('skills') || lowerInput.includes('tech')) {
          fallbackResponse = "My skills include React, Python, Node.js, AI/ML, Docker, and Kubernetes. See my 'Skills' section for a full list!";
        }
        // --- End Graceful Degradation ---
      }

      setMessages(prev => [...prev, {
        text: fallbackResponse,
        sender: 'bot-error'
      }]);

      // Add TTS for fallback:
      if (fallbackResponse && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(fallbackResponse);
        utterance.lang = language === 'de' ? 'de-DE' : 'en-US';
        window.speechSynthesis.speak(utterance);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for voice input result
  const handleVoiceResult = (transcript) => {
    setInput(transcript); // Update the input field visually
    handleSend(transcript); // Immediately send the transcribed text
  };

  return (
    // --- 3. Add Close Button to Top Bar ---
    <div className="fixed bottom-8 right-8 w-96 bg-[#0a192f] border border-red-600 rounded-lg shadow-lg flex flex-col h-[500px] z-50">
      {/* Top Bar with Close Button */}
      <div className="p-4 border-b border-red-600 flex justify-between items-center">
    <div className="flex items-center">
        <FaRobot className="text-red-500 mr-2" />
        <h3 className="text-gray-300 font-bold">My AI Spokesperson</h3>
    </div>
    <div className="flex items-center space-x-2">
        <div className="flex items-center space-x-1">
            <span className="text-xs text-gray-400">Lang:</span>
            <button
            onClick={() => setLanguage(lang => lang === 'en' ? 'de' : 'en')}
            aria-label={`Currently ${language === 'en' ? 'English' : 'German'}. Click to switch language.`}
            title={`Switch to ${language === 'en' ? 'German (DE)' : 'English (EN)'}`}
            className="flex items-center text-xs text-gray-300 hover:text-red-500 px-2 py-1 rounded hover:bg-gray-700 transition-colors duration-200"
            >
            {language === 'en' ? (
                <>
                <FaFlagUsa className="mr-1" /> EN
                </>
            ) : (
                <>
                <FaFlag className="mr-1" /> DE
                </>
            )}
            </button>
        </div>
        <button
            onClick={onClose}
            className="text-gray-400 hover:text-white focus:outline-none"
            aria-label="Close chat"
        >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
        </button>
    </div>
 </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg ${
              msg.sender === 'user' ? 'bg-blue-900 text-white' :
              msg.sender === 'bot-error' ? 'bg-red-900 text-white' :
              msg.sender === 'bot-welcome' ? 'bg-gray-700 border-red-500 text-gray-300' : // Style for welcome message
              'bg-gray-800 text-gray-300'
            }`}
          >
            <p>{msg.text}</p>
            {/* Optional: Display context for debugging/testing
            {msg.context && msg.context.length > 0 && (
              <details className="mt-2 text-xs text-gray-400">
                <summary>Context</summary>
                <ul>
                  {msg.context.map((ctx, idx) => <li key={idx}>{ctx}</li>)}
                </ul>
              </details>
            )}
            */}
          </div>
        ))}
        {isLoading && <div className="p-3 bg-gray-800 text-white rounded-lg">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t border-red-600 flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 bg-[#ccd6f6] text-gray-800 rounded-l px-4 py-2 focus:outline-none"
          placeholder="Ask about my experience..."
          disabled={isLoading}
        />
        {/* Pass the new handler and other props to VoiceButton */}
        <VoiceButton
          onResult={handleVoiceResult} // Use the new handler
          language={language}
          disabled={isLoading}
        />
        <button
          onClick={() => handleSend()} // Pass input state explicitly or just call handleSend()
          disabled={isLoading}
          className="bg-red-600 text-white px-4 py-2 rounded-r hover:bg-red-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;