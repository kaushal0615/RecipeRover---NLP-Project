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
    
    setMessages(currentMessages => [...currentMessages, { text: userInput, sender: 'user' }]);
    setInputText('');
  
    try {
      const response = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
        message: userInput,
        sender: 'user',
      });
  
      // Process each message received from the bot
      let recipeMessages = [];
      let hasRecipes = false;
  
      response.data.forEach((botMessage) => {
        if (botMessage.custom) {
          // Check if recipes are present in the custom message
          if (botMessage.custom.recipes && botMessage.custom.recipes.length > 0) {
            hasRecipes = true;
            // Accumulate the recipes
            botMessage.custom.recipes.forEach((recipe) => {
              recipeMessages.push({
                text: (
                  <>
                    <p><strong>Recipe:</strong> {recipe.name}</p>
                    <p><strong>Ingredients:</strong> {Array.isArray(recipe.ingredients) ? recipe.ingredients.join(", ") : recipe.ingredients}</p>
                    <p><strong>Instructions:</strong> {recipe.instructions}</p>
                  </>
                ),
                sender: 'bot'
              });
            });
          }
        } else {
          // Handle regular text responses
          setMessages(currentMessages => [...currentMessages, {
            text: botMessage.text,
            sender: 'bot'
          }]);
        }
      });
  
      // If there are recipes, prepend the introductory text and append all to the messages
      if (hasRecipes) {
        setMessages(currentMessages => [
          ...currentMessages,
          { text: <p>Here are some recipes you might like:</p>, sender: 'bot' },
          ...recipeMessages
        ]);
      }
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


