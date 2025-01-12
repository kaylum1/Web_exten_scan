import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Helper function to normalize URLs
def normalize_url(url):
    parsed_url = urlparse(url)
    normalized = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return normalized.rstrip('/')

# HTTPS checker function
def check_https(url):
    if url.startswith("https://"):
        return "Https is secure"
    else:
        return "Site uses insecure HTTP"

# Fetch unscanned URLs from MongoDB
async def get_unscanned_urls():
    return await collection.find({"https_checker": {"$exists": False}}).to_list(length=100)

# Update MongoDB with HTTPS check results
async def update_https_result(url_entry, https_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "https_checker": https_result,
                    "last_scanned": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated HTTPS result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating HTTPS result: {e}")

# Main scanning function
async def scan_and_update_urls():
    urls = await get_unscanned_urls()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL: {url}")

        # Perform HTTPS check
        https_result = check_https(url)

        # Update MongoDB with the result
        await update_https_result(url_entry, https_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_urls())
