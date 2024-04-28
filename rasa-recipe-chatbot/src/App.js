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
    setMessages(messages => [...messages, { text: userInput, sender: 'user' }]);
    setInputText('');

    try {
      const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
        message: userInput,
        sender: 'user',
      });

      response.data.forEach((botMessage) => {
        if (botMessage.custom) {
          // Process custom structured data for recipes
          botMessage.custom.recipes.forEach((recipe) => {
            setMessages(messages => [...messages,{
              text: (
                <>
                  <p>Here are some recipes you might like:</p>
                  <p><strong>Recipe:</strong> {recipe.name}</p>
                  <p><strong>Instructions:</strong> {recipe.instructions}</p>
                </>
              ),
              sender: 'bot'
            }]);
          });
        } else {
          // Handle regular text responses
          setMessages(messages => [...messages, {
            text: botMessage.text,
            sender: 'bot'
          }]);
        }
      });
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


