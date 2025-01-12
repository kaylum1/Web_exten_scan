chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
      // Send the URL to the server
      fetch('http://localhost:8000/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: tab.url })
      })
      .then(response => response.json())
      .then(data => console.log('URL logged:', data))
      .catch(error => console.error('Error logging URL:', error));
  }
});
