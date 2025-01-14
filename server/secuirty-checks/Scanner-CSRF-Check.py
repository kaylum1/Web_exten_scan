import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import asyncio

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# CSRF checker function
def check_csrf_protection(url):
    results = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all forms in the page
        forms = soup.find_all('form')

        for form in forms:
            csrf_token_present = False

            # Check for common CSRF token input fields
            for input_field in form.find_all('input'):
                if input_field.get('name') in ['csrf_token', '_csrf', '__RequestVerificationToken']:
                    csrf_token_present = True
                    break

            form_info = {
                "action": form.get('action', 'missing'),
                "csrf_token": "present" if csrf_token_present else "missing"
            }
            results.append(form_info)

    except requests.RequestException as e:
        print(f"Error checking CSRF for {url}: {e}")
        return {"error": "Failed to check CSRF"}

    return results

# Fetch URLs that haven't been checked for CSRF protection
async def get_urls_for_csrf_check():
    return await collection.find({"csrf_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with CSRF check results
async def update_csrf_result(url_entry, csrf_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "csrf_check": csrf_result,
                    "last_scanned_csrf": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated CSRF result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating CSRF result: {e}")

# Main scanning function
async def scan_and_update_csrf():
    urls = await get_urls_for_csrf_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for CSRF protection: {url}")

        # Perform CSRF check
        csrf_result = check_csrf_protection(url)

        # Update MongoDB with the results
        await update_csrf_result(url_entry, csrf_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_csrf())
