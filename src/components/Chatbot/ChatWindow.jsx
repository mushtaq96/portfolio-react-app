// src/components/Chatbot/ChatWindow.jsx
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
// import VoiceButton from './VoiceButton'; // Assuming VoiceButton is not integrated yet

// --- 1. Use Environment Variable for API Base URL ---
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const ChatWindow = ({ onClose }) => { // Accept onClose prop for communication
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // --- 2. Improved Error Handling & Fallback Responses ---
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    setIsLoading(true);
    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, { // Use API_BASE_URL
        message: input,
        history: messages,
        language
      });
      setMessages(prev => [...prev, { 
        text: response.data.response, 
        sender: 'bot',
        context: response.data.context 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      let fallbackResponse = "Sorry, I'm having trouble connecting right now. Please try again later or reach out via email."; // Default fallback

      // --- Specific Error Messages ---
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        fallbackResponse = "The request took too long. Please check your connection or try again.";
      } else if (!error.response) {
        // Network error (e.g., backend down)
        fallbackResponse = "The AI assistant seems to be offline at the moment. You can email me directly at mushtaq96smb@gmail.com!";
        
        // --- Graceful Degradation Example ---
        // Provide contextually relevant fallback for common questions if backend is down
        const lowerInput = input.toLowerCase();
        if (lowerInput.includes('experience') || lowerInput.includes('work')) {
             fallbackResponse = "I have experience in Full-Stack Development (React, Node.js, Python) and AI/ML (Deep Learning, NLP). Check out my 'Work' section for project details!";
        } else if (lowerInput.includes('contact') || lowerInput.includes('email')) {
             fallbackResponse = "You can reach me directly at mushtaq96smb@gmail.com!";
        } else if (lowerInput.includes('skills') || lowerInput.includes('tech')) {
             fallbackResponse = "My skills include React, Python, Node.js, AI/ML, Docker, and Kubernetes. See my 'Skills' section for a full list!";
        }
        // --- End Graceful Degradation ---
      }
      // Add more specific error checks if needed

      setMessages(prev => [...prev, { 
        text: fallbackResponse, 
        sender: 'bot-error' // You might style this differently if desired
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // --- 3. Add Close Button to Top Bar ---
    <div className="fixed bottom-8 right-8 w-96 bg-[#0a192f] border border-red-600 rounded-lg shadow-lg flex flex-col h-[500px] z-50">
      {/* Top Bar with Close Button */}
      <div className="p-4 border-b border-red-600 flex justify-between items-center">
        <h3 className="text-gray-300 font-bold">Recruiter Assistant</h3>
        <div className="flex items-center space-x-2"> {/* Wrapper for items */}
          <button 
            onClick={() => setLanguage(lang => lang === 'en' ? 'de' : 'en')}
            className="text-xs text-gray-300 hover:text-red-500"
            aria-label="Toggle language"
          >
            {language === 'en' ? 'DE' : 'EN'}
          </button>
          {/* --- Close Button --- */}
          <button
            onClick={onClose} // Use the onClose prop
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
          <div key={i} className={`p-3 rounded-lg ${
            msg.sender === 'user' ? 'bg-blue-900 ml-auto' : 
            msg.sender === 'bot-error' ? 'bg-red-900' : 'bg-gray-800' // Style bot-error
          }`}>
            <p>{msg.text}</p>
          </div>
        ))}
        {isLoading && <div className="p-3 bg-gray-800 rounded-lg">Thinking...</div>}
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
        <button
          onClick={handleSend}
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