from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse
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

# Helper function to normalize URLs
def normalize_url(url):
    parsed_url = urlparse(url)
    # Reconstruct the URL with only scheme and netloc (domain)
    normalized = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return normalized.rstrip('/')  # Remove trailing slash if present

# Endpoint to log URLs
@app.post("/log")
async def log_url(data: URLLog):
    # Normalize the URL before logging
    url_to_log = normalize_url(data.url)

    print(f"Received URL: {data.url}")
    print(f"Normalized URL: {url_to_log}")

    try:
        # Check if the normalized URL already exists in the database
        existing_entry = await collection.find_one({"url": url_to_log})
        if existing_entry:
            print(f"Duplicate URL detected: {url_to_log}")
            return {"message": "URL already logged", "url": url_to_log}

        # If not a duplicate, insert the new URL
        log_entry = {
            "url": url_to_log,
            "timestamp": datetime.datetime.utcnow()
        }
        await collection.insert_one(log_entry)
        print(f"URL logged in MongoDB: {url_to_log}")
        return {"message": "URL logged successfully", "url": url_to_log}
    except Exception as e:
        print(f"Error logging URL: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging URL: {e}")

# Endpoint to retrieve all logs from MongoDB
@app.get("/getAllLogs")
async def get_all_logs():
    try:
        # Fetch all documents from the collection
        logs_cursor = collection.find({})
        logs = await logs_cursor.to_list(length=None)  # Convert cursor to list

        # Format the logs for response
        formatted_logs = [
            {
                "url": log["url"],
                "timestamp": log["timestamp"].isoformat() if "timestamp" in log else None
            } for log in logs
        ]

        # Check if logs exist before returning
        if not formatted_logs:
            return {"message": "No logs found"}

        return {"message": "Logs retrieved successfully", "logs": formatted_logs}
    except Exception as e:
        print(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {e}")

# Startup event to test MongoDB connection
@app.on_event("startup")
async def startup_event():
    try:
        # Check if the connection to MongoDB works
        await collection.count_documents({})
        print("MongoDB connection successful")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")



'''
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse
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

# Helper function to normalize URLs
def normalize_url(url):
    parsed_url = urlparse(url)
    # Reconstruct the URL with only scheme and netloc (domain)
    normalized = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return normalized.rstrip('/')  # Remove trailing slash if present

# Endpoint to log URLs
@app.post("/log")
async def log_url(data: URLLog):
    # Normalize the URL before logging
    url_to_log = normalize_url(data.url)

    print(f"Received URL: {data.url}")
    print(f"Normalized URL: {url_to_log}")

    try:
        # Check if the normalized URL already exists in the database
        existing_entry = await collection.find_one({"url": url_to_log})
        if existing_entry:
            print(f"Duplicate URL detected: {url_to_log}")
            return {"message": "URL already logged", "url": url_to_log}

        # If not a duplicate, insert the new URL
        log_entry = {
            "url": url_to_log,
            "timestamp": datetime.datetime.utcnow()
        }
        await collection.insert_one(log_entry)
        print(f"URL logged in MongoDB: {url_to_log}")
        return {"message": "URL logged successfully", "url": url_to_log}
    except Exception as e:
        print(f"Error logging URL: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging URL: {e}")

@app.get("/getAllLogs")
async def get_all_logs():
    try:
        # Fetch all documents from the collection
        logs_cursor = collection.find({})
        logs = await logs_cursor.to_list(length=None)  # Convert cursor to list

        # Format the logs for response
        formatted_logs = [
            {"url": log["url"], "timestamp": log["timestamp"].isoformat()} for log in logs
        ]

        return formatted_logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {e}")


# Startup event to test MongoDB connection
@app.on_event("startup")
async def startup_event():
    try:
        # Check if the connection to MongoDB works
        await collection.count_documents({})
        print("MongoDB connection successful")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
'''