import requests
import datetime
import hashlib
import re
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Broken authentication and session management checker function
def check_broken_authentication(url):
    results = {
        "weak_session_id": "not checked",
        "cookies_secure": "not checked",
        "cookies_http_only": "not checked"
    }
    
    try:
        response = requests.get(url, timeout=10)
        cookies = response.cookies

        # Check for Secure and HttpOnly attributes in cookies
        secure_missing = []
        http_only_missing = []
        for cookie in cookies:
            if not cookie.secure:
                secure_missing.append(cookie.name)
            if "HttpOnly" not in cookie._rest:
                http_only_missing.append(cookie.name)

        results["cookies_secure"] = "missing" if secure_missing else "present"
        results["cookies_http_only"] = "missing" if http_only_missing else "present"

        # Check for weak session identifiers (e.g., predictable or short length)
        session_id_pattern = re.compile(r"(PHPSESSID|JSESSIONID|ASPSESSIONID)=(\w+)")
        session_match = session_id_pattern.search(response.headers.get("Set-Cookie", ""))
        if session_match:
            session_id = session_match.group(2)
            if len(session_id) < 16:  # Weak if session ID length is too short
                results["weak_session_id"] = "weak (too short)"
            elif re.match(r"^\d+$", session_id):
                results["weak_session_id"] = "weak (numeric)"
            else:
                results["weak_session_id"] = "strong"
        else:
            results["weak_session_id"] = "not found"

    except requests.RequestException as e:
        print(f"Error checking broken authentication for {url}: {e}")
        return {"error": "Failed to check authentication"}

    return results

# Fetch URLs that haven't been checked for broken authentication
async def get_urls_for_auth_check():
    return await collection.find({"auth_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with broken authentication check results
async def update_auth_result(url_entry, auth_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "auth_check": auth_result,
                    "last_scanned_auth": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated authentication check result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating authentication check result: {e}")

# Main scanning function
async def scan_and_update_auth():
    urls = await get_urls_for_auth_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for broken authentication: {url}")

        # Perform broken authentication and session management check
        auth_result = check_broken_authentication(url)

        # Update MongoDB with the results
        await update_auth_result(url_entry, auth_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_auth())



