chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
      fetch('http://localhost:3000/log-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: changeInfo.url })
      })
      .then(response => console.log('URL logged:', changeInfo.url))
      .catch(error => console.error('Error logging URL:', error));
    }
  });
  