// Function to normalize a URL
function normalizeUrl(url) {
    const parsedUrl = new URL(url);
    return `${parsedUrl.protocol}//${parsedUrl.hostname}`.toLowerCase().replace(/\/$/, ''); // Remove trailing slash and convert to lowercase
  }
  
  // Handle button click to fetch and display database info for the current URL
  document.getElementById('print-database-button').addEventListener('click', () => {
    console.log('Button clicked! Retrieving current tab URL.');
  
    // Get the current tab's URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length === 0) {
        console.error('No active tab found.');
        document.getElementById('output').textContent = 'No active tab found.';
        return;
      }
  
      const currentTabUrl = normalizeUrl(tabs[0].url); // Normalize the current tab's URL
      console.log(`Normalized current tab URL: ${currentTabUrl}`);
  
      // Send a message to the background script to fetch the full database
      chrome.runtime.sendMessage({ action: 'getFullDatabase' }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('Error communicating with background script:', chrome.runtime.lastError.message);
          document.getElementById('output').textContent = 'Error communicating with background script.';
          return;
        }
  
        console.log('Full database response:', JSON.stringify(response, null, 2)); // Log the full response
  
        // Extract logs array from response
        const logs = response.data && response.data.logs ? response.data.logs : []; // Safely extract logs array
  
        if (logs.length === 0) {
          console.error('Logs array is empty or missing.');
          document.getElementById('output').textContent = 'No logs found in the database.';
          return;
        }
  
        // Find the matching URL in the logs
        const matchingEntry = logs.find(entry => {
          const normalizedEntryUrl = normalizeUrl(entry.url);
          console.log(
            `Comparing:\nDatabase URL: "${normalizedEntryUrl}"\nCurrent Tab URL: "${currentTabUrl}"\nCharacter Codes:`,
            [...normalizedEntryUrl].map(c => c.charCodeAt(0)),
            [...currentTabUrl].map(c => c.charCodeAt(0))
          );
          return normalizedEntryUrl === currentTabUrl;
        });
  
        if (matchingEntry) {
          console.log(`Matching URL found: ${matchingEntry.url}`);
          console.log(`Timestamp: ${new Date(matchingEntry.timestamp).toLocaleString()}`);
  
          // Display the information in the output div
          document.getElementById('output').innerHTML = `
            <strong>URL Info:</strong><br>
            URL: ${matchingEntry.url}<br>
            Timestamp: ${new Date(matchingEntry.timestamp).toLocaleString()}
          `;
        } else {
          console.log(`No matching URL found for: ${currentTabUrl}`);
          document.getElementById('output').textContent = `No matching URL found for: ${currentTabUrl}`;
        }
      });
    });
  });
  
  
  
  


/*
document.getElementById('print-database-button').addEventListener('click', () => {
    console.log('Button clicked! Sending request to get the full database.');
  
    // Send a message to the background script to get the full database
    chrome.runtime.sendMessage({ action: 'getFullDatabase' }, (response) => {
      if (response && response.success) {
        console.log('Full database response received:', response.data);
  
        // Display the full database content in the output div
        const outputElement = document.getElementById('output');
        outputElement.textContent = JSON.stringify(response.data, null, 2);
      } else {
        console.log('Failed to retrieve full database:', response.error);
        const outputElement = document.getElementById('output');
        outputElement.textContent = 'Failed to retrieve full database.';
      }
    });
  });
*/

  
  
  