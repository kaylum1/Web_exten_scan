chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
      console.log(`Sending URL to server: ${tab.url}`);  // Log the URL being sent

      fetch('http://localhost:8000/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: tab.url })
      })
      .then(response => response.json())
      .then(data => console.log('Response from server:', data))
      .catch(error => console.error('Error logging URL:', error));  // Log any errors
  }
});

