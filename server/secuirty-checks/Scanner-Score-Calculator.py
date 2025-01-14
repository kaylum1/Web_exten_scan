import pymongo
import datetime

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = pymongo.MongoClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# Define weights for each check
weights = {
    "xss_check": 15,
    "sql_injection_check": 20,
    "open_redirect_check": 5,
    "directory_listing_check": 5,
    "cookie_security_check": 15,
    "subdomain_takeover_check": 5,
    "csrf_check": 10,
    "sensitive_data_check": 20,
    "ssl_tls_check": 10,
    "auth_check": 20
}

# Function to calculate score for a single URL entry
def calculate_score(url_entry):
    total_score = 0
    max_score = sum(weights.values())  # Total possible weight
    
    # XSS Check
    if isinstance(url_entry.get("xss_check"), list):
        vulnerable = any(entry.get("status") == "vulnerable" for entry in url_entry["xss_check"])
        total_score += 0 if vulnerable else weights["xss_check"]
    else:
        print(f"Warning: 'xss_check' format unexpected for URL: {url_entry.get('url')}")

    # SQL Injection Check
    if isinstance(url_entry.get("sql_injection_check"), list):
        vulnerable = any(entry.get("status") == "vulnerable" for entry in url_entry["sql_injection_check"])
        total_score += 0 if vulnerable else weights["sql_injection_check"]
    else:
        print(f"Warning: 'sql_injection_check' format unexpected for URL: {url_entry.get('url')}")

    # Open Redirect Check
    if isinstance(url_entry.get("open_redirect_check"), list):
        vulnerable = any(entry.get("status") == "vulnerable" for entry in url_entry["open_redirect_check"])
        total_score += 0 if vulnerable else weights["open_redirect_check"]
    else:
        print(f"Warning: 'open_redirect_check' format unexpected for URL: {url_entry.get('url')}")

    # Directory Listing Check
    if isinstance(url_entry.get("directory_listing_check"), list):
        vulnerable = any(entry.get("status") == "vulnerable" for entry in url_entry["directory_listing_check"])
        total_score += 0 if vulnerable else weights["directory_listing_check"]
    else:
        print(f"Warning: 'directory_listing_check' format unexpected for URL: {url_entry.get('url')}")

    # Cookie Security Check
    cookie_check = url_entry.get("cookie_security_check")
    if isinstance(cookie_check, list):
        secure_present = all(cookie.get("secure") == "present" for cookie in cookie_check)
        http_only_present = all(cookie.get("http_only") == "present" for cookie in cookie_check)
        if secure_present and http_only_present:
            total_score += weights["cookie_security_check"]
        elif secure_present or http_only_present:
            total_score += weights["cookie_security_check"] / 2
    else:
        print(f"Warning: 'cookie_security_check' format unexpected for URL: {url_entry.get('url')}")

    # Subdomain Takeover Check
    if isinstance(url_entry.get("subdomain_takeover_check"), dict):
        if url_entry["subdomain_takeover_check"].get("status") != "vulnerable":
            total_score += weights["subdomain_takeover_check"]
    else:
        print(f"Warning: 'subdomain_takeover_check' format unexpected for URL: {url_entry.get('url')}")

    # CSRF Check
    if isinstance(url_entry.get("csrf_check"), list):
        vulnerable = any(entry.get("csrf_token") == "missing" for entry in url_entry["csrf_check"])
        total_score += 0 if vulnerable else weights["csrf_check"]
    else:
        print(f"Warning: 'csrf_check' format unexpected for URL: {url_entry.get('url')}")

    # Sensitive Data Exposure Check
    if isinstance(url_entry.get("sensitive_data_check"), list):
        exposed = any(entry.get("status") == "exposed" for entry in url_entry["sensitive_data_check"])
        total_score += 0 if exposed else weights["sensitive_data_check"]
    else:
        print(f"Warning: 'sensitive_data_check' format unexpected for URL: {url_entry.get('url')}")

    # SSL/TLS Configuration Check
    ssl_check = url_entry.get("ssl_tls_check")
    if isinstance(ssl_check, dict) and ssl_check.get("status") == "secure":
        total_score += weights["ssl_tls_check"]
    else:
        print(f"Warning: 'ssl_tls_check' format unexpected for URL: {url_entry.get('url')}")

    # Broken Authentication and Session Management Check
    auth_check = url_entry.get("auth_check")
    if isinstance(auth_check, dict):
        weak_session_id = auth_check.get("weak_session_id", "") == "weak"
        cookies_secure = auth_check.get("cookies_secure", "") == "present"
        cookies_http_only = auth_check.get("cookies_http_only", "") == "present"
        if not weak_session_id and cookies_secure and cookies_http_only:
            total_score += weights["auth_check"]
        elif not weak_session_id and (cookies_secure or cookies_http_only):
            total_score += weights["auth_check"] / 2
    else:
        print(f"Warning: 'auth_check' format unexpected for URL: {url_entry.get('url')}")

    # Normalize score to a percentage
    return (total_score / max_score) * 100

# Function to generate report for all URLs and update MongoDB with scores
def generate_report():
    urls = collection.find()
    report = []
    
    for url_entry in urls:
        url = url_entry.get("url")
        score = calculate_score(url_entry)

        # Append the result to the report list
        report.append({
            "url": url,
            "score": round(score, 2),
            "last_scanned": url_entry.get("last_scanned", "Unknown")
        })

        # Update the MongoDB entry with the calculated score
        try:
            collection.update_one(
                {"_id": url_entry["_id"]},
                {"$set": {"score": round(score, 2)}}
            )
            print(f"Score updated for URL: {url}")
        except Exception as e:
            print(f"Error updating score for URL: {url}. Error: {e}")

    # Print the report
    for entry in report:
        print(f"URL: {entry['url']}\nScore: {entry['score']}%\nLast Scanned: {entry['last_scanned']}\n{'-'*40}")
    
    return report

# Run the report generation
if __name__ == "__main__":
    generate_report()




'''
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
'''