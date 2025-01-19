from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse

import subprocess
import datetime
import psutil
import os
import signal

from fastapi.responses import JSONResponse



# Create FastAPI app
app = FastAPI()


'''
#to start server from web needed to be added
server_process = None  # To track the server process
'''
server_running = True


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










#//======================================================================================
#//LOGGING URLS TO DATABASE step 3:
#//======================================================================================


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




 # //======================================================================================
 # //PRINT SCORE step 4 + PRINT database step 4:
 # //======================================================================================



@app.get("/getAllLogsAndInfo")
async def get_all_logs_and_info():
    try:
        # Fetch all documents from the collection
        logs_cursor = collection.find({})
        logs = await logs_cursor.to_list(length=None)  # Convert cursor to list

        # Convert ObjectId to string and ensure all fields are JSON serializable
        formatted_logs = []
        for log in logs:
            log["_id"] = str(log["_id"])  # Convert ObjectId to string
            formatted_logs.append(log)

        # Return the full documents, including all fields
        return {"success": True, "logs": formatted_logs}
    except Exception as e:
        print(f"Error fetching detailed logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching detailed logs: {e}")







@app.get("/get-score")
async def get_scores():
    try:
        # Fetch all documents and project only the 'score' field
        logs_cursor = collection.find({}, {"_id": 0, "score": 1})  # Exclude '_id' and include only 'score'
        scores = await logs_cursor.to_list(length=None)  # Convert cursor to list

        # Extract scores into a simple list
        score_list = [log["score"] for log in scores]

        return {"success": True, "scores": score_list}
    except Exception as e:
        print(f"Error fetching scores: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching scores: {e}")





# Startup event to test MongoDB connection
@app.on_event("startup")
async def startup_event():
    try:
        # Check if the connection to MongoDB works
        await collection.count_documents({})
        print("MongoDB connection successful")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")






 # //======================================================================================
 # //RUN WEB SCAN step 3:
 # //======================================================================================

@app.get("/run-scan")
async def run_scan():
    try:
        # List of all scanner scripts to run
        scanner_scripts = [
            "secuirty-checks/Scanner-HTTPS-Check.py",
            "secuirty-checks/Scanner-Security-Headers-Check.py",
            "secuirty-checks/Scanner-Cookie-Security-Check.py",
            "secuirty-checks/Scanner-CSRF-Check.py",
            "secuirty-checks/Scanner-Directory-Listing-Check.py",
            "secuirty-checks/Scanner-Open-Redirect-Check.py",
            "secuirty-checks/Scanner-Sensitive-Data-Exposure-Check.py",
            "secuirty-checks/Scanner-SQL-Injection-Check.py",
            "secuirty-checks/Scanner-Subdomain-Takeover.py",
            "secuirty-checks/Scanner-XSS-Check.py",
            "secuirty-checks/SSL-TLS-Configuration-Check.py",
            "secuirty-checks/Scanner-Broken-Authentication-and-Session-Management-Check.py",
            "secuirty-checks/Scanner-Score-Calculator.py"
        ]

        # Dictionary to store the results of each scan
        result = {}

        # Run each scanner script and collect its output
        for script in scanner_scripts:
            output = subprocess.check_output(['python', script]).decode('utf-8')
            result[script] = output

        return result

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error running scan: {str(e)}")









  #//======================================================================================
  #//STARTING SERVER FROM WEB step 2:
  #//======================================================================================


@app.get("/health")
def health_check():
    # Add logic to check database connectivity
    db_status = check_database_connection()
    server_status = "running"  # You can dynamically determine this
    return JSONResponse({"server_status": server_status, "database_status": db_status})

def check_database_connection():
    try:
        # Replace with actual database connection check
        return "connected"
    except:
        return "disconnected"

@app.post("/control")
def control_server(action: str):
    global server_running
    if action == "start" and not server_running:
        # Logic to start the server (for testing, toggle the state)
        server_running = True
        return JSONResponse({"message": "Server started", "server_status": "running"})
    elif action == "stop" and server_running:
        # Logic to stop the server (toggle state)
        server_running = False
        return JSONResponse({"message": "Server stopped", "server_status": "stopped"})
    else:
        return JSONResponse({"message": "Invalid action or server already in desired state"}, status_code=400)
'''
# Endpoint to start the server
@app.post("/start-server")
async def start_server():
    global server_process
    try:
        # Check if the server is already running
        if server_process and server_process.poll() is None:
            print("Server is already running.")
            return {"status": "running", "message": "Server is already running!"}

        # Start the FastAPI server using uvicorn and output logs to the terminal
        print("Starting the server...")
        server_process = subprocess.Popen(
            ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=None,  # Send stdout directly to the terminal
            stderr=None   # Send stderr directly to the terminal
        )

        # Ensure the process started correctly
        if server_process.poll() is not None:
            raise Exception("Server process terminated immediately after starting.")

        print("Server started successfully.")
        return {"status": "success", "message": "Server started successfully!"}
    except Exception as e:
        print(f"Error while starting server: {e}")
        return {"status": "error", "message": str(e)}





@app.post("/stop-server")
async def stop_server():
    global server_process
    try:
        if server_process:
            print(f"server_process status before stopping: {server_process}")

            # Attempt to terminate the server process
            server_process.terminate()
            server_process.wait(timeout=5)  # Wait for the process to terminate

            # Check if the process has stopped
            if server_process.poll() is None:
                print("Failed to terminate the server process.")
                return {"status": "error", "message": "Failed to stop the server process."}

            # Clear the global process reference
            server_process = None
            print("Server stopped successfully.")
            return {"status": "success", "message": "Server stopped successfully!"}
        else:
            print("No server is currently running.")
            return {"status": "error", "message": "No server is running!"}
    except Exception as e:
        print(f"Error while stopping server: {e}")
        return {"status": "error", "message": str(e)}






# Endpoint to check server status
@app.get("/server-status")
async def server_status():
    try:
        for process in psutil.process_iter(attrs=['name', 'cmdline']):
            if "uvicorn" in process.info['cmdline']:
                return {"status": "running"}
        return {"status": "stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



'''



'''

@app.get("/run-scan")
async def run_scan():
    try:
        https_check_output = subprocess.check_output(['python', 'Scanner-HTTPS-Check.py']).decode('utf-8')
        headers_check_output = subprocess.check_output(['python', 'Scanner-Security-Headers-Check.py']).decode('utf-8')
        score_calc_output = subprocess.check_output(['python', 'Scanner-Score-Calculator.py']).decode('utf-8')
        

        result = {
            "HTTPS Check": https_check_output,
            "Security Headers Check": headers_check_output,
            "Score Calculator": score_calc_output,
        }
        return result
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error running scan: {str(e)}")
'''

















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