import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Cookie security checker function
def check_cookie_security(url):
    results = []
    try:
        response = requests.get(url, timeout=10)
        cookies = response.cookies

        for cookie in cookies:
            cookie_info = {
                "name": cookie.name,
                "secure": "present" if cookie.secure else "missing",
                "http_only": "present" if "HttpOnly" in cookie._rest else "missing",
                "same_site": cookie._rest.get("SameSite", "missing")
            }
            results.append(cookie_info)

    except requests.RequestException as e:
        print(f"Error checking cookies for {url}: {e}")
        return {"error": "Failed to check cookies"}

    return results


# Fetch URLs that haven't been checked for cookie security
async def get_urls_for_cookie_check():
    return await collection.find({"cookie_security_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with cookie security check results
async def update_cookie_result(url_entry, cookie_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "cookie_security_check": cookie_result,
                    "last_scanned_cookie": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated cookie security result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating cookie security result: {e}")

# Main scanning function
async def scan_and_update_cookies():
    urls = await get_urls_for_cookie_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for cookie security: {url}")

        # Perform cookie security check
        cookie_result = check_cookie_security(url)

        # Update MongoDB with the results
        await update_cookie_result(url_entry, cookie_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_cookies())
