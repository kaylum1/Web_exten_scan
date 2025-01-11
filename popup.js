// popup.js

// Backend server URL
const backendUrl = 'http://localhost:3000/get-url-info';

// if using render use the below backend
//const backendUrl = 'https://your-render-service.onrender.com/get-url-info';


document.addEventListener('DOMContentLoaded', async () => {
  // Get the current tab's URL
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const url = new URL(tabs[0].url).origin; // Get the base URL (origin only)

    try {
      // Send a GET request to the backend with the URL as a query parameter
      const response = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
      const data = await response.json();

      // Display the data in the popup
      document.getElementById('webpage-name').innerText = `Name: ${data.name}`;
      document.getElementById('webpage-url').innerText = `URL: ${data.url}`;
      document.getElementById('webpage-status').innerText = `Secure: ${data.isSecure ? 'Yes' : 'No'}`;
    } catch (error) {
      console.error('Error fetching URL info:', error);
      document.getElementById('error-message').innerText = 'Error fetching URL info';
    }
  });
});

  