import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import VoiceButton from './VoiceButton';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    setIsLoading(true);
    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
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
      setMessages(prev => [...prev, { 
        text: "Sorry, I couldn't process your request.", 
        sender: 'bot-error' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-8 right-8 w-96 bg-[#0a192f] border border-red-600 rounded-lg shadow-lg flex flex-col h-[500px] z-50">
      <div className="p-4 border-b border-red-600 flex justify-between items-center">
        <h3 className="text-gray-300 font-bold">Recruiter Assistant</h3>
        <div className="flex space-x-2">
          <button 
            onClick={() => setLanguage(lang => lang === 'en' ? 'de' : 'en')}
            className="text-xs text-gray-300 hover:text-red-500"
          >
            {language === 'en' ? 'DE' : 'EN'}
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`p-3 rounded-lg ${
            msg.sender === 'user' ? 'bg-blue-900 ml-auto' : 
            msg.sender === 'bot-error' ? 'bg-red-900' : 'bg-gray-800'
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