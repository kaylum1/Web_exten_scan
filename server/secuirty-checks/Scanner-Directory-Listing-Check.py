import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# List of common directories to test for directory listing vulnerabilities
common_directories = [
    "/",
    "/uploads/",
    "/images/",
    "/files/",
    "/backup/",
    "/.git/",
    "/.env/",
    "/logs/",
]

# Directory listing checker function
def check_directory_listing(url):
    results = []
    for directory in common_directories:
        try:
            # Construct the full URL for the directory
            url_with_directory = f"{url.rstrip('/')}{directory}"
            response = requests.get(url_with_directory, timeout=10)

            # Check if the response indicates a directory listing
            if response.status_code == 200 and (
                "Index of" in response.text or
                "<title>Index of" in response.text or
                "Directory listing" in response.text
            ):
                results.append({"directory": directory, "status": "vulnerable"})
            else:
                results.append({"directory": directory, "status": "not vulnerable"})
        except requests.RequestException as e:
            print(f"Error checking directory listing for {url}: {e}")
            return {"error": "Failed to check directory listing"}
    
    return results

# Fetch URLs that haven't been checked for directory listing
async def get_urls_for_directory_check():
    return await collection.find({"directory_listing_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with directory listing check results
async def update_directory_result(url_entry, directory_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "directory_listing_check": directory_result,
                    "last_scanned_directory": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated directory listing result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating directory listing result: {e}")

# Main scanning function
async def scan_and_update_directories():
    urls = await get_urls_for_directory_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for directory listing: {url}")

        # Perform directory listing check
        directory_result = check_directory_listing(url)

        # Update MongoDB with the results
        await update_directory_result(url_entry, directory_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_directories())
