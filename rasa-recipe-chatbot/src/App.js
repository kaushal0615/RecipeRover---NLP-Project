// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  const sendMessage = async (e) => {
    e.preventDefault();
    const userInput = inputText;
  
    // Update the messages state to include the user's message
    setMessages(currentMessages => [...currentMessages, { text: userInput, sender: 'user' }]);
    setInputText('');
  
    try {
      const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
        message: userInput,
        sender: 'user',
      });
  
      // Flatten all bot messages into a single array
      let newMessages = response.data.reduce((acc, botMessage) => {
        // Handle regular text responses and recipe messages uniformly
        return [...acc, {
          text: botMessage.text || '',
          sender: 'bot'
        }];
      }, []);
  
      // Update state with all new messages at once
      setMessages(currentMessages => [...currentMessages, ...newMessages]);
  
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };
  
  
  
  

  return (
    <div className="App">
      <h1>Chat with Our Recipe Chat Bot</h1>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender}>
            {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type a message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;


