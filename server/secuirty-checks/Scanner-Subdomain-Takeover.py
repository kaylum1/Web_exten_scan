import requests
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import dns.resolver
from urllib.parse import urlparse

# MongoDB connection (replace with your actual connection string)
MONGO_URI = 'mongodb+srv://kaylumsmith:HS0KKaCbX4pbFiMM@diss-server.beqfh.mongodb.net/urlLogger?retryWrites=true&w=majority'
client = AsyncIOMotorClient(MONGO_URI)
db = client["urlLogger"]
collection = db["urllogs"]

# List of known services vulnerable to subdomain takeover
vulnerable_services = {
    "github.io": "There is no repository here.",
    "amazonaws.com": "NoSuchBucket",
    "herokuapp.com": "No such app",
    "readthedocs.io": "Project not found",
    "netlify.app": "Page Not Found"
}

# Subdomain takeover checker function
def check_subdomain_takeover(url):
    try:
        parsed_url = urlparse(url)
        subdomain = parsed_url.netloc

        # Resolve the subdomain's DNS records
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(subdomain, 'CNAME')

        for rdata in answers:
            cname_target = str(rdata.target).strip(".")
            print(f"Found CNAME target for {subdomain}: {cname_target}")

            # Check if the CNAME target matches known vulnerable services
            for service, error_message in vulnerable_services.items():
                if service in cname_target:
                    # Send a request to the subdomain to check for takeover message
                    response = requests.get(url, timeout=10)
                    if error_message in response.text:
                        return {"status": "vulnerable", "service": service}

        return {"status": "not vulnerable"}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"No DNS record found for {url}")
        return {"status": "no DNS record"}
    except requests.RequestException as e:
        print(f"Error checking subdomain takeover for {url}: {e}")
        return {"error": "Failed to check subdomain takeover"}

# Fetch URLs that haven't been checked for subdomain takeover
async def get_urls_for_subdomain_check():
    return await collection.find({"subdomain_takeover_check": {"$exists": False}}).to_list(length=100)

# Update MongoDB with subdomain takeover check results
async def update_subdomain_result(url_entry, subdomain_result):
    try:
        await collection.update_one(
            {"_id": url_entry["_id"]},
            {
                "$set": {
                    "subdomain_takeover_check": subdomain_result,
                    "last_scanned_subdomain": datetime.datetime.utcnow()
                }
            }
        )
        print(f"Updated subdomain takeover result for {url_entry['url']}")
    except Exception as e:
        print(f"Error updating subdomain takeover result: {e}")

# Main scanning function
async def scan_and_update_subdomains():
    urls = await get_urls_for_subdomain_check()
    for url_entry in urls:
        url = url_entry["url"]
        print(f"Scanning URL for subdomain takeover: {url}")

        # Perform subdomain takeover check
        subdomain_result = check_subdomain_takeover(url)

        # Update MongoDB with the results
        await update_subdomain_result(url_entry, subdomain_result)

# Run the scanning process
if __name__ == "__main__":
    asyncio.run(scan_and_update_subdomains())
