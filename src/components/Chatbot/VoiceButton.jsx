import React, { useState, useEffect } from 'react';
import { FaMicrophone, FaStop } from 'react-icons/fa';
import axios from 'axios';

const VoiceButton = ({ onResult, language, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);

  useEffect(() => {
    if (!navigator.mediaDevices) {
      console.warn("MediaDevices API not supported");
      return;
    }

    const setupRecorder = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            setAudioChunks(prev => [...prev, e.data]);
          }
        };
        
        setMediaRecorder(recorder);
      } catch (err) {
        console.error("Error accessing microphone:", err);
      }
    };

    setupRecorder();

    return () => {
      if (mediaRecorder) {
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = () => {
    if (mediaRecorder && !isRecording) {
      setAudioChunks([]);
      mediaRecorder.start();
      setIsRecording(true);
    }
  };

  const stopRecording = async () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      
      // Process audio
      if (audioChunks.length > 0) {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
      }
    }
  };

  const sendAudioToServer = async (blob) => {
    try {
      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');
      
      const response = await axios.post(
        'http://localhost:8000/api/audio/input', 
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      onResult(response.data.text);
    } catch (error) {
      console.error("Audio processing error:", error);
    }
  };

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled || !mediaRecorder}
      className={`p-2 mx-2 rounded-full ${
        isRecording ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-800'
      }`}
    >
      {isRecording ? <FaStop /> : <FaMicrophone />}
    </button>
  );
};

export default VoiceButton;