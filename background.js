// background.js
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const url = new URL(tab.url);

    // Send URL to the backend
    fetch('http://localhost:3000/log-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url.href }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('URL logged:', data);
      })
      .catch((error) => {
        console.error('Error logging URL:', error);
      });
  }
});
