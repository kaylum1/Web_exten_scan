// popup.js
document.addEventListener('DOMContentLoaded', async () => {
    // Get the current tab's URL
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const url = new URL(tabs[0].url).origin; // Get the base URL
  
      try {
        // Send a request to your backend to get the stored data
        const response = await fetch(`http://localhost:3000/get-url-info?url=${url}`);
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
  