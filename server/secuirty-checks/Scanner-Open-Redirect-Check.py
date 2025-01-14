import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlencode
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# List of common open redirect payloads
redirect_payloads = [
    "https://evil.com",
    "//evil.com",
    "/\\evil.com",
    "////evil.com",
    "https://evil.com#",
]

# Open redirect checker function
def check_open_redirect(url):
    results = []
    for payload in redirect_payloads:
        try:
            # Construct the URL with the redirect payload as a query parameter
            params = {"redirect": payload}
            url_with_payload = f"{url}?{urlencode(params)}"
            response = requests.get(url_with_payload, timeout=10, allow_redirects=False)

            # Check if the response contains a redirection to the payload
            if response.status_code in [301, 302, 303, 307, 308] and 'Location' in response.headers:
                location_header = response.headers['Location']
                if payload in location_header:
                    results.append({"payload": payload, "status": "vulnerable"})
                else:
                    results.append({"payload": payload, "status": "not vulnerable"})
            else:
                results.append({"payload": payload, "status": "not vulnerable"})
        except requests.RequestException as e:
            print(f"Error checking open redirect for {url}: {e}")
            return {"error": "Failed to check open redirect"}
    
    return results

# Fetch URLs that haven't been checked for open redirects
async def get_urls_for_redirect_check():
    return await collection.find({"redirect_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with open redirect check results
async def update_redirect_result(url_entry, redirect_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "redirect_check": redirect_result,
                    "last_scanned_redirect": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated open redirect result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating open redirect result: {e}")

# Main scanning function
async def scan_and_update_redirects():
    urls = await get_urls_for_redirect_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for open redirects: {url}")

        # Perform Open Redirect check
        redirect_result = check_open_redirect(url)

        # Update MongoDB with the results
        await update_redirect_result(url_entry, redirect_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_redirects())
