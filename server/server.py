from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import datetime

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins (to allow requests from the browser extension)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]        # Database name
collection = db["urllogs"]      # Collection name

# Pydantic model for incoming URL data
class URLLog(BaseModel):
    url: str

# Endpoint to log URLs
@app.post("/log")
async def log_url(data: URLLog):
    print(f"Received URL: {data.url}")  # Log received URL
    try:
        log_entry = {
            "url": data.url,
            "timestamp": datetime.datetime.utcnow()
        }
        await collection.insert_one(log_entry)
        print(f"URL logged successfully: {data.url}")  # Log successful insertion
        return {"message": "URL logged successfully"}
    except Exception as e:
        print(f"Error logging URL: {e}")  # Log any errors
        raise HTTPException(status_code=500, detail=f"Error logging URL: {e}")

# Startup event to test MongoDB connection
@app.on_event("startup")
async def startup_event():
    try:
        # Check if the connection to MongoDB works
        await collection.count_documents({})
        print("MongoDB connection successful")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
