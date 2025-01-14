import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from urllib.parse import urljoin

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# List of common sensitive files to check
sensitive_files = [
    ".env",
    ".git/config",
    "backup.zip",
    "database.sql",
    "id_rsa",
    "credentials.json",
    "config.yml",
    ".htpasswd"
]

# Sensitive data exposure checker function
def check_sensitive_data_exposure(url):
    results = []
    try:
        for file in sensitive_files:
            file_url = urljoin(url, file)
            response = requests.get(file_url, timeout=10)

            if response.status_code == 200 and len(response.content) > 0:
                results.append({"file": file, "status": "exposed"})
            else:
                results.append({"file": file, "status": "not exposed"})

    except requests.RequestException as e:
        print(f"Error checking sensitive data for {url}: {e}")
        return {"error": "Failed to check sensitive data"}

    return results

# Fetch URLs that haven't been checked for sensitive data exposure
async def get_urls_for_sensitive_data_check():
    return await collection.find({"sensitive_data_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with sensitive data check results
async def update_sensitive_data_result(url_entry, sensitive_data_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "sensitive_data_check": sensitive_data_result,
                    "last_scanned_sensitive_data": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated sensitive data exposure result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating sensitive data exposure result: {e}")

# Main scanning function
async def scan_and_update_sensitive_data():
    urls = await get_urls_for_sensitive_data_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for sensitive data exposure: {url}")

        # Perform sensitive data exposure check
        sensitive_data_result = check_sensitive_data_exposure(url)

        # Update MongoDB with the results
        await update_sensitive_data_result(url_entry, sensitive_data_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_sensitive_data())
