import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Security headers checker function
def check_security_headers(url):
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        required_headers = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "X-Content-Type-Options"
        ]

        results = {header: "present" if header in headers else "missing" for header in required_headers}
        return results
    except requests.RequestException as e:
        print(f"Error checking headers for {url}: {e}")
        return {"error": "Failed to fetch headers"}

# Fetch URLs that haven't been checked for security headers
async def get_urls_for_header_check():
    return await collection.find({"security_headers_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with security headers check results
async def update_headers_result(url_entry, headers_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "security_headers_check": headers_result,
                    "last_scanned_headers": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated security headers result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating security headers result: {e}")

# Main scanning function
async def scan_and_update_headers():
    urls = await get_urls_for_header_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for security headers: {url}")

        # Perform Security Headers check
        headers_result = check_security_headers(url)

        # Update MongoDB with the results
        await update_headers_result(url_entry, headers_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_headers())
