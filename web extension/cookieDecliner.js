//======================================================================================
  //COOKIE DECLINER step 3:
//======================================================================================


/*

// Comprehensive list of selectors for "Decline" or "Reject" buttons in cookie banners
const declineButtonSelectors = [
    // Specific ID for Currys cookie banner
    '#onetrust-reject-all-handler',
  
    // General selectors by text content (case-insensitive matching)
    'button:contains("Allow required cookies only")',
    'button:contains("Reject")',
    'button:contains("Decline")',
    'button:contains("Deny")',
    'button:contains("Essential only")',
    'button:contains("Only necessary")',
  
    // General selectors by ID (case-insensitive matching)
    '[id*="reject"]',
    '[id*="decline"]',
    '[id*="deny"]',
  
    // General selectors by class (case-insensitive matching)
    '[class*="reject"]',
    '[class*="decline"]',
    '[class*="deny"]',
    '[class*="essential"]',
  
    // General selectors by aria-label
    '[aria-label*="reject"]',
    '[aria-label*="decline"]',
    '[aria-label*="deny"]'
  ];
  
  // Function to check for the cookie banner and click the "Decline" button
function checkAndDeclineCookies() {
    for (const selector of declineButtonSelectors) {
      const button = document.querySelector(selector);
      if (button) {
        console.log('Declining cookies by clicking:', selector);
        button.click();
        return; // Stop further checks once the button is clicked
      }
    }
  }
  
  // Continuously check for the cookie banner every 500ms
  const intervalId = setInterval(() => {
    checkAndDeclineCookies();
  }, 500);
  
  // Stop checking after 10 seconds to avoid running indefinitely
  setTimeout(() => {
    clearInterval(intervalId);
  }, 10000);
  */

// List of common selectors for "Decline" or "Reject" buttons
const declineButtonSelectors = [
  '#onetrust-reject-all-handler',
  'button:contains("Reject")',
  'button:contains("Decline")',
  'button:contains("Deny")',
  '[id*="reject"]',
  '[id*="decline"]',
  '[id*="deny"]',
  '[class*="reject"]',
  '[class*="decline"]',
  '[class*="deny"]',
  '[aria-label*="reject"]',
  '[aria-label*="decline"]',
  '[aria-label*="deny"]'
];

// Function to click "Decline" button
function declineCookies() {
  for (const selector of declineButtonSelectors) {
    const button = document.querySelector(selector);
    if (button) {
      console.log("Cookie banner detected, declining cookies.");
      button.click();
      return; // Stop once a button is clicked
    }
  }
}

// Run the function immediately and periodically for delayed banners
declineCookies();
const interval = setInterval(declineCookies, 1000);

// Stop after 10 seconds to prevent unnecessary executions
setTimeout(() => clearInterval(interval), 10000);