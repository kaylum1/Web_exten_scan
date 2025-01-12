// popup.js

// Backend server URL (change to your deployed backend URL if necessary)
const backendUrl = 'http://localhost:3000/get-url-info';

// popup.js
document.addEventListener('DOMContentLoaded', async () => {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const url = new URL(tabs[0].url).origin; // Get the base URL
  
      try {
        // Send a request to your backend to log the URL
        const response = await fetch('http://localhost:3000/log-url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url }),
        });
  
        const data = await response.json();
  
        // Display the logged data in the popup
        document.getElementById('webpage-name').innerText = `Name: ${data.name}`;
        document.getElementById('webpage-url').innerText = `URL: ${data.url}`;
        document.getElementById('webpage-status').innerText = `Secure: ${data.isSecure ? 'Yes' : 'No'}`;
      } catch (error) {
        console.error('Error fetching URL info:', error);
        document.getElementById('error-message').innerText = 'Error logging URL';
      }
    });
  });
  
  