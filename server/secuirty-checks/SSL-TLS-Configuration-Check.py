import datetime
import ssl
import socket
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from urllib.parse import urlparse

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# SSL/TLS checker function
def check_ssl_tls_configuration(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc

        context = ssl.create_default_context()
        conn = socket.create_connection((hostname, 443), timeout=10)
        sock = context.wrap_socket(conn, server_hostname=hostname)

        # Get SSL certificate
        cert = sock.getpeercert()

        # Extract certificate details
        ssl_result = {
            "issuer": cert.get("issuer"),
            "subject": cert.get("subject"),
            "not_before": cert.get("notBefore"),
            "not_after": cert.get("notAfter"),
            "protocol": sock.version()  # SSL/TLS protocol version
        }
        sock.close()
        return {"status": "secure", "details": ssl_result}
    
    except ssl.SSLError as e:
        print(f"SSL error for {url}: {e}")
        return {"status": "insecure", "error": str(e)}
    except socket.error as e:
        print(f"Socket error for {url}: {e}")
        return {"status": "insecure", "error": "Connection failed"}
    except Exception as e:
        print(f"Error checking SSL/TLS for {url}: {e}")
        return {"status": "error", "error": str(e)}

# Fetch URLs that haven't been checked for SSL/TLS configuration
async def get_urls_for_ssl_check():
    return await collection.find({"ssl_tls_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with SSL/TLS check results
async def update_ssl_result(url_entry, ssl_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "ssl_tls_check": ssl_result,
                    "last_scanned_ssl": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated SSL/TLS result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating SSL/TLS result: {e}")

# Main scanning function
async def scan_and_update_ssl():
    urls = await get_urls_for_ssl_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for SSL/TLS configuration: {url}")

        # Perform SSL/TLS configuration check
        ssl_result = check_ssl_tls_configuration(url)

        # Update MongoDB with the results
        await update_ssl_result(url_entry, ssl_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_ssl())
