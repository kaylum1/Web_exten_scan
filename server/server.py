from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bs4 import BeautifulSoup
import requests
import datetime

app = FastAPI()

# MongoDB connection
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]        # Database name
collection = db["urllogs"]      # Collection name

# Pydantic model for request body
class ScanRequest(BaseModel):
    url: str

@app.post("/scan")
async def scan_url(request: ScanRequest):
    url = request.url

    # Check if URL already scanned recently (e.g., within the last 7 days)
    existing_scan = await collection.find_one({"url": url})
    if existing_scan:
        return {"message": "Existing result", "data": existing_scan}

    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Example analysis (customize as needed)
        uses_https = url.startswith("https")
        tracker_count = len(soup.find_all("script", src=True))  # Count script tags with src attribute
        cookie_count = len(response.cookies)

        # Example score calculation
        score = (50 if uses_https else 0) + (50 if tracker_count == 0 else 20)

        # Create scan result
        scan_result = {
            "url": url,
            "score": score,
            "details": {
                "uses_https": uses_https,
                "tracker_count": tracker_count,
                "cookie_count": cookie_count
            },
            "timestamp": datetime.datetime.utcnow()
        }

        # Store result in MongoDB
        await collection.insert_one(scan_result)

        return {"message": "New result", "data": scan_result}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {e}")
