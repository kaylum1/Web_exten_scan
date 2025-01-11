// popup.js

// Backend server URL (change to your deployed backend URL if necessary)
const backendUrl = 'http://localhost:3000/get-url-info';

document.addEventListener('DOMContentLoaded', async () => {
  // Get the current tab's URL
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const url = new URL(tabs[0].url).origin; // Get the base URL (origin only)
    console.log('Current tab URL:', url); // Debug log

    try {
      // Send a GET request to the backend to fetch stored URL info
      const response = await fetch(`${backendUrl}?url=${encodeURIComponent(url)}`);
      console.log('Response status:', response.status); // Debug log

      if (!response.ok) throw new Error('Failed to fetch URL info');

      const data = await response.json();
      console.log('Fetched data:', data); // Debug log

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

  