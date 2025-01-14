import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from urllib.parse import urlencode

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# List of common XSS payloads
xss_payloads = [
    "<script>alert(1)</script>",
    "'\"><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>"
]

# XSS vulnerability checker function
def check_xss_vulnerability(url):
    results = []
    for payload in xss_payloads:
        try:
            # Construct the URL with the XSS payload as a query parameter
            params = {"test": payload}
            url_with_payload = f"{url}?{urlencode(params)}"
            response = requests.get(url_with_payload, timeout=10)

            # Check if the payload is reflected in the response
            if payload in response.text:
                results.append({"payload": payload, "status": "vulnerable"})
            else:
                results.append({"payload": payload, "status": "not vulnerable"})
        except requests.RequestException as e:
            print(f"Error checking XSS for {url}: {e}")
            return {"error": "Failed to check XSS"}
    
    return results

# Fetch URLs that haven't been checked for XSS
async def get_urls_for_xss_check():
    return await collection.find({"xss_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with XSS check results
async def update_xss_result(url_entry, xss_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "xss_check": xss_result,
                    "last_scanned_xss": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated XSS result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating XSS result: {e}")

# Main scanning function
async def scan_and_update_xss():
    urls = await get_urls_for_xss_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for XSS: {url}")

        # Perform XSS check
        xss_result = check_xss_vulnerability(url)

        # Update MongoDB with the results
        await update_xss_result(url_entry, xss_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_xss())
