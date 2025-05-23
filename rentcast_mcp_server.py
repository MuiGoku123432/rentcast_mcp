from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE = "https://api.rentcast.io/v1"

def _proxy(endpoint, params):
    try:
        key = params.pop("api_key")
        if not key:
            raise ValueError("API key is missing")
        
        url = BASE + endpoint
        headers = {"X-Api-Key": key}
        
        r = requests.get(url, headers=headers, params=params, timeout=30)
        
        if r.status_code != 200:
            raise Exception(f"RentCast API Error {r.status_code}: {r.text}")
        
        return r.json()
    except Exception as e:
        raise Exception(f"API request failed: {str(e)}")

# Create FastMCP server
mcp = FastMCP("RentCast MCP – local", version="1.0.0")

@mcp.tool()
def search_property(
    address: str = None,
    city: str = None,
    state: str = None,
    zip: str = None,
    limit: int = 20,
    api_key: str = None
) -> dict:
    """Search properties by address, city, state or ZIP."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    
    params = {"api_key": api_key}
    if address:
        params["address"] = address
    if city:
        params["city"] = city
    if state:
        params["state"] = state
    if zip:
        params["zip"] = zip
    if limit:
        params["limit"] = min(max(limit, 1), 100)
    
    return _proxy("/properties", params)

@mcp.tool()
def get_property_by_id(property_id: str, api_key: str = None) -> dict:
    """Return a single property record by RentCast ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy(f"/properties/{property_id}", {"api_key": api_key})

@mcp.tool()
def get_value_estimate(address: str, api_key: str = None) -> dict:
    """Return the current value AVM for an address."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy("/valuations/value", {"address": address, "api_key": api_key})

@mcp.tool()
def get_rent_estimate(address: str, api_key: str = None) -> dict:
    """Return the long-term rent AVM for an address."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy("/valuations/rent/long-term", {"address": address, "api_key": api_key})

@mcp.tool()
def search_sale_listings(
    city: str = None,
    state: str = None,
    bbox: str = None,
    limit: int = 20,
    api_key: str = None
) -> dict:
    """Search active *sale* listings in a region. bbox format: min_lat,min_lon,max_lat,max_lon"""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    
    params = {"api_key": api_key}
    if city:
        params["city"] = city
    if state:
        params["state"] = state
    if bbox:
        params["bbox"] = bbox
    if limit:
        params["limit"] = min(max(limit, 1), 100)
    
    return _proxy("/listings/sale", params)

@mcp.tool()
def search_rental_listings(
    city: str = None,
    state: str = None,
    bbox: str = None,
    limit: int = 20,
    api_key: str = None
) -> dict:
    """Search active *rental* listings in a region."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    
    params = {"api_key": api_key}
    if city:
        params["city"] = city
    if state:
        params["state"] = state
    if bbox:
        params["bbox"] = bbox
    if limit:
        params["limit"] = min(max(limit, 1), 100)
    
    return _proxy("/listings/rental/long-term", params)

@mcp.tool()
def get_market_stats(zip: str, api_key: str = None) -> dict:
    """Get ZIP-level market statistics."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy("/markets", {"zip": zip, "api_key": api_key})

@mcp.tool()
def get_random_properties(limit: int = 10, api_key: str = None) -> dict:
    """Return random sample properties for demo/testing."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    
    params = {"api_key": api_key, "limit": min(max(limit, 1), 100)}
    return _proxy("/properties/random", params)

@mcp.tool()
def get_sale_listing_by_id(listing_id: str, api_key: str = None) -> dict:
    """Return a single sale listing record by listing ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy(f"/listings/sale/{listing_id}", {"api_key": api_key})

@mcp.tool()
def get_rental_listing_by_id(listing_id: str, api_key: str = None) -> dict:
    """Return a single rental listing record by listing ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy(f"/listings/rental/long-term/{listing_id}", {"api_key": api_key})

@mcp.tool()
def ping_rate_limit(api_key: str = None) -> dict:
    """Check remaining quota for this API key."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _proxy("/rate-limits", {"api_key": api_key})

if __name__ == "__main__":
    mcp.run()
