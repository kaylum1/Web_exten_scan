import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Function to calculate the score for a given document
def calculate_score(doc):
    score = 0
    total_checks = 6

    # Check HTTPS result
    if doc.get("https_checker") == "Https is secure":
        score += 1

    # Check security headers result
    headers = doc.get("security_headers_check", {})
    required_headers = [
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "X-Content-Type-Options"
    ]
    
    for header in required_headers:
        if headers.get(header) == "present":
            score += 1

    return {"total": f"{score}/{total_checks}"}

# Fetch all documents from MongoDB
async def get_all_urls():
    return await collection.find().to_list(length=1000)

# Update MongoDB with the score
async def update_score(url_entry, score):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "score": score,
                    "last_scored": datetime.utcnow()
                }
            }
        )
        print(f"Updated score for {url_entry['url']} - {score['total']}")
    except Exception as e:
        print(f"Error updating score for {url_entry['url']}: {e}")

# Main function to calculate and update scores
async def calculate_and_update_scores():
    urls = await get_all_urls()
    for url_entry in urls:
        score = calculate_score(url_entry)
        await update_score(url_entry, score)

# Run the scoring process
if __name__ == "__main__":
    asyncio.run(calculate_and_update_scores())
