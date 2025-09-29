// src/components/Chatbot/VoiceButton.jsx
import React, { useState, useEffect } from 'react';
import { FaMicrophone, FaStop } from 'react-icons/fa';

const VoiceButton = ({ onResult, language, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    // 1. Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Web Speech API (SpeechRecognition) is not supported in this browser.");
      // Optionally disable the button or show a message in the UI
      return;
    }

    // 2. Initialize the SpeechRecognition object
    const recognitionInstance = new SpeechRecognition();
    
    // Configure recognition settings
    recognitionInstance.continuous = false; // Stop recognition after first result
    recognitionInstance.interimResults = false; // We only want final results
    // Language will be set dynamically just before starting
    
    // 3. Set up event handlers
    recognitionInstance.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("STT Transcript:", transcript);
      // 4. Pass the result to the parent component (ChatWindow)
      if (onResult) {
        onResult(transcript);
      }
      setIsRecording(false); // Automatically stop recording state
    };

    recognitionInstance.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      // Handle specific errors if needed (e.g., 'no-speech', 'audio-capture')
      setIsRecording(false);
    };

    recognitionInstance.onend = () => {
      console.log("Speech recognition ended.");
      // Ensure button state is updated if it ends unexpectedly
      if (isRecording) {
        setIsRecording(false);
      }
    };

    // 5. Store the recognition instance in component state
    setRecognition(recognitionInstance);

    // 6. Cleanup function (runs on component unmount)
    return () => {
      console.log("Cleaning up SpeechRecognition...");
      if (recognitionInstance) {
        recognitionInstance.stop(); // Ensure it's stopped
      }
    };
  }, []); // Empty dependency array: run only once on mount

  // Update language if it changes (e.g., from ChatWindow)
  useEffect(() => {
    if (recognition) {
      recognition.lang = language === 'de' ? 'de-DE' : 'en-US';
    }
  }, [language, recognition]);

  const toggleRecording = () => {
    if (!recognition || disabled) return;

    if (isRecording) {
      // 7a. Stop recording if it's currently active
      console.log("Stopping recording...");
      recognition.stop();
      // Note: The `onend` handler will set isRecording to false
    } else {
      // 7b. Start recording if it's currently inactive
      try {
        // Ensure the correct language is set before starting
        recognition.lang = language === 'de' ? 'de-DE' : 'en-US';
        recognition.start();
        setIsRecording(true);
        console.log("Starting recording...");
      } catch (err) {
        console.error("Error starting speech recognition:", err);
        setIsRecording(false);
      }
    }
  };

  return (
    <button
      onClick={toggleRecording}
      disabled={disabled || !recognition} // Disable if no recognition support or parent says so
      className={`p-2 mx-2 rounded-full ${
        isRecording 
          ? 'animate-pulse bg-red-600 text-white' // Visual feedback for recording
          : 'bg-gray-200 text-gray-800 hover:bg-gray-300' 
      } transition-colors duration-200`}
      aria-label={isRecording ? "Stop recording" : "Start voice recording"}
    >
      {isRecording ? <FaStop /> : <FaMicrophone />}
    </button>
  );
};

export default VoiceButton;