// Function to log URL to the server and store the response locally
function logUrlToServer(url) {
  const normalizedUrl = new URL(url).origin; // Normalize to base URL
  console.log(`Sending URL to server: ${normalizedUrl}`); // Log the URL being sent

  fetch('http://localhost:8000/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: normalizedUrl })
  })
    .then(response => response.json())
    .then(data => {
      chrome.storage.local.set({ [normalizedUrl]: data }, () => {
        console.log(`Data for ${normalizedUrl} saved locally.`);
      });
    })
    .catch(error => console.error('Error logging URL:', error));
}

// Listen for tab updates and call logUrlToServer when a tab is fully loaded
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    logUrlToServer(tab.url);
  }
});

// Handle messages from popup script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchData' && request.url) {
    const normalizedUrl = new URL(request.url).origin; // Normalize to base URL

    console.log(`Attempting to retrieve data for normalized URL: ${normalizedUrl}`);

    chrome.storage.local.get([normalizedUrl], (result) => {
      if (result[normalizedUrl]) {
        console.log(`Data found for URL: ${normalizedUrl}`);
        sendResponse({ success: true, data: result[normalizedUrl] });
      } else {
        console.log(`No data found for URL: ${normalizedUrl}`);
        sendResponse({ success: false, data: null });
      }
    });

    return true; // Keeps the message channel open for asynchronous response
  }

  if (request.action === 'getFullDatabase') {
    console.log('Received request to get the full database from MongoDB');

    // Fetch the full database from the backend
    fetch('http://localhost:8000/getAllLogs', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => response.json())
      .then(data => {
        console.log('Full database retrieved:', data);
        sendResponse({ success: true, data: data });
      })
      .catch(error => {
        console.error('Error retrieving full database:', error);
        sendResponse({ success: false, error: 'Failed to retrieve database' });
      });

    return true; // Keeps the message channel open for asynchronous response
  }

  if (request.action === 'getFullDatabaseWithInfo') {
    console.log('Received request to get the detailed database from MongoDB');

    // Fetch the detailed database from the backend
    fetch('http://localhost:8000/getAllLogsAndInfo', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(response => response.json())
      .then(data => {
        console.log('Detailed database retrieved:', data);
        sendResponse({ success: true, data: data });
      })
      .catch(error => {
        console.error('Error retrieving detailed database:', error);
        sendResponse({ success: false, error: 'Failed to retrieve detailed database' });
      });

    return true; // Keeps the message channel open for asynchronous response
  }

  if (request.action === 'runScan') {
    console.log('Received request to run web scan');
  
    // Fetch to trigger Python scripts on the backend server (port updated to 8000)
    fetch('http://localhost:8000/run-scan')
      .then(response => response.json())
      .then(data => {
        console.log('Scan result:', data);
        sendResponse({ result: "scan sucesfull" });
      })
      .catch(error => {
        console.error('Error running scan:', error);
        sendResponse({ result: 'Error running scan.' });
      });
  
    return true; // Keeps the message channel open for async response
  }

  // Handle invalid requests
  console.warn('Invalid action received:', request.action);
  sendResponse({ success: false, message: 'Invalid action' });
});
