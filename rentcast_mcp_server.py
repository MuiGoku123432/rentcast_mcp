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
        
        data = r.json()
        if isinstance(data, list):
            return {"results": data, "count": len(data)}
        return data
    except Exception as e:
        raise Exception(f"API request failed: {str(e)}")


# ── Formatting helpers ──────────────────────────────────────────────

def _fmt_currency(value):
    if value is None:
        return "-"
    return f"${value:,.0f}"


def _fmt_address(obj):
    if not obj:
        return "-"
    if isinstance(obj, str):
        return obj
    if obj.get("formattedAddress"):
        return obj["formattedAddress"]
    # Try flat fields
    line = obj.get("addressLine1") or obj.get("address")
    city = obj.get("city", "")
    state = obj.get("state", "")
    z = obj.get("zipCode") or obj.get("zip") or ""
    if line:
        parts = [p for p in [line, city, state] if p]
        return f"{', '.join(parts)} {z}".strip()
    # Try nested address dict
    nested = obj.get("address")
    if isinstance(nested, dict):
        return _fmt_address(nested)
    return "-"


def _trunc_date(val):
    if not val:
        return "-"
    return str(val)[:10]


# ── List formatters ─────────────────────────────────────────────────

def _fmt_sale_listings(data):
    items = data.get("results", [])
    count = data.get("count", len(items))
    if not items:
        return f"## Sale Listings ({count} results)\n\nNo listings found."
    rows = ["| # | Address | Price | Beds | Baths | Sqft | Type | Listed |",
            "|---|---------|-------|------|-------|------|------|--------|"]
    for i, p in enumerate(items, 1):
        rows.append(
            f"| {i} | {_fmt_address(p)} | {_fmt_currency(p.get('price'))} "
            f"| {p.get('bedrooms', '-')} | {p.get('bathrooms', '-')} "
            f"| {p.get('squareFootage', '-'):,} | {p.get('propertyType', '-')} "
            f"| {_trunc_date(p.get('listedDate'))} |"
            if p.get('squareFootage') else
            f"| {i} | {_fmt_address(p)} | {_fmt_currency(p.get('price'))} "
            f"| {p.get('bedrooms', '-')} | {p.get('bathrooms', '-')} "
            f"| - | {p.get('propertyType', '-')} "
            f"| {_trunc_date(p.get('listedDate'))} |"
        )
    return f"## Sale Listings ({count} results)\n\n" + "\n".join(rows)


def _fmt_rental_listings(data):
    items = data.get("results", [])
    count = data.get("count", len(items))
    if not items:
        return f"## Rental Listings ({count} results)\n\nNo listings found."
    rows = ["| # | Address | Rent | Beds | Baths | Sqft | Type | Listed |",
            "|---|---------|------|------|-------|------|------|--------|"]
    for i, p in enumerate(items, 1):
        sqft = p.get("squareFootage")
        sqft_str = f"{sqft:,}" if sqft else "-"
        rows.append(
            f"| {i} | {_fmt_address(p)} | {_fmt_currency(p.get('price'))} "
            f"| {p.get('bedrooms', '-')} | {p.get('bathrooms', '-')} "
            f"| {sqft_str} | {p.get('propertyType', '-')} "
            f"| {_trunc_date(p.get('listedDate'))} |"
        )
    return f"## Rental Listings ({count} results)\n\n" + "\n".join(rows)


def _fmt_property_list(data):
    items = data.get("results", [])
    count = data.get("count", len(items))
    if not items:
        return f"## Properties ({count} results)\n\nNo properties found."
    rows = ["| # | Address | Beds | Baths | Sqft | Type | Year | Last Sale | Taxes/yr |",
            "|---|---------|------|-------|------|------|------|-----------|----------|"]
    for i, p in enumerate(items, 1):
        sqft = p.get("squareFootage")
        sqft_str = f"{sqft:,}" if sqft else "-"
        last_sale = _fmt_currency(p.get("lastSalePrice"))
        taxes = _fmt_currency(p.get("taxAssessment", {}).get("taxAmount") if isinstance(p.get("taxAssessment"), dict) else p.get("propertyTaxes"))
        rows.append(
            f"| {i} | {_fmt_address(p)} | {p.get('bedrooms', '-')} "
            f"| {p.get('bathrooms', '-')} | {sqft_str} "
            f"| {p.get('propertyType', '-')} | {p.get('yearBuilt', '-')} "
            f"| {last_sale} | {taxes} |"
        )
    return f"## Properties ({count} results)\n\n" + "\n".join(rows)


# ── Single-object formatters ────────────────────────────────────────

def _fmt_property_detail(data):
    addr = _fmt_address(data)
    sqft = data.get("squareFootage")
    sqft_str = f"{sqft:,}" if sqft else "-"
    lot = data.get("lotSize")
    lot_str = f"{lot:,} sqft" if lot else "-"

    lines = [
        f"## {addr}",
        "",
        f"**Beds:** {data.get('bedrooms', '-')} | **Baths:** {data.get('bathrooms', '-')} "
        f"| **Sqft:** {sqft_str} | **Lot:** {lot_str}",
        f"**Type:** {data.get('propertyType', '-')} | **Year Built:** {data.get('yearBuilt', '-')}",
    ]

    last_price = data.get("lastSalePrice")
    last_date = data.get("lastSaleDate")
    if last_price or last_date:
        lines += ["", "### Sale History",
                   f"- **Last Sale:** {_fmt_currency(last_price)} on {_trunc_date(last_date)}"]

    tax = data.get("taxAssessment") or data.get("propertyTaxes")
    if isinstance(tax, dict):
        lines += ["", "### Tax Info",
                   f"- **Annual Taxes:** {_fmt_currency(tax.get('taxAmount'))} ({tax.get('year', '-')})",
                   f"- **Assessed Value:** {_fmt_currency(tax.get('assessedValue'))}"]
    elif tax is not None:
        lines += ["", "### Tax Info", f"- **Annual Taxes:** {_fmt_currency(tax)}"]

    return "\n".join(lines)


def _fmt_value_estimate(data):
    lines = [
        "## Value Estimate",
        "",
        f"**Estimated Value:** {_fmt_currency(data.get('price'))}",
        f"**Range:** {_fmt_currency(data.get('priceLow'))} – {_fmt_currency(data.get('priceHigh'))}",
    ]
    comps = data.get("comparables", [])[:5]
    if comps:
        lines += ["", "### Comparables (top 5)",
                   "| Address | Sale Price | Date | Sqft | Distance |",
                   "|---------|-----------|------|------|----------|"]
        for c in comps:
            sqft = c.get("squareFootage")
            sqft_str = f"{sqft:,}" if sqft else "-"
            dist = c.get("distance")
            dist_str = f"{dist:.1f} mi" if dist is not None else "-"
            lines.append(
                f"| {_fmt_address(c)} | {_fmt_currency(c.get('price'))} "
                f"| {_trunc_date(c.get('lastSaleDate') or c.get('listedDate'))} "
                f"| {sqft_str} | {dist_str} |"
            )
    return "\n".join(lines)


def _fmt_rent_estimate(data):
    lines = [
        "## Rent Estimate",
        "",
        f"**Estimated Rent:** {_fmt_currency(data.get('rent'))}/mo",
        f"**Range:** {_fmt_currency(data.get('rentLow'))}/mo – {_fmt_currency(data.get('rentHigh'))}/mo",
    ]
    comps = data.get("comparables", [])[:5]
    if comps:
        lines += ["", "### Comparables (top 5)",
                   "| Address | Rent | Beds | Baths | Sqft | Distance |",
                   "|---------|------|------|-------|------|----------|"]
        for c in comps:
            sqft = c.get("squareFootage")
            sqft_str = f"{sqft:,}" if sqft else "-"
            dist = c.get("distance")
            dist_str = f"{dist:.1f} mi" if dist is not None else "-"
            lines.append(
                f"| {_fmt_address(c)} | {_fmt_currency(c.get('price') or c.get('rent'))}/mo "
                f"| {c.get('bedrooms', '-')} | {c.get('bathrooms', '-')} "
                f"| {sqft_str} | {dist_str} |"
            )
    return "\n".join(lines)


def _fmt_market_stats(data):
    lines = [
        f"## Market Statistics: {data.get('zipCode', data.get('zip', '-'))}",
        "",
        f"**Median Price:** {_fmt_currency(data.get('salePrice', {}).get('median') if isinstance(data.get('salePrice'), dict) else data.get('medianPrice'))} "
        f"| **Median Rent:** {_fmt_currency(data.get('rentalPrice', {}).get('median') if isinstance(data.get('rentalPrice'), dict) else data.get('medianRent'))}/mo",
    ]

    sale = data.get("salePrice")
    rental = data.get("rentalPrice")
    if isinstance(sale, dict):
        lines.append(f"**Price/sqft:** ${sale.get('medianPerSqft', '-')}")
    if isinstance(rental, dict):
        lines[-1] += f" | **Rent/sqft:** ${rental.get('medianPerSqft', '-')}"

    # By bedroom count
    bd_sale = data.get("salePriceByBedroom") or data.get("detailedSalePrice") or {}
    bd_rent = data.get("rentalPriceByBedroom") or data.get("detailedRentalPrice") or {}
    bedrooms = sorted(set(list(bd_sale.keys()) + list(bd_rent.keys())))
    if bedrooms:
        lines += ["", "### By Bedroom Count",
                   "| Beds | Med. Rent | Med. Price |",
                   "|------|-----------|------------|"]
        for b in bedrooms:
            r = bd_rent.get(b, {})
            s = bd_sale.get(b, {})
            r_val = _fmt_currency(r.get("median") if isinstance(r, dict) else r)
            s_val = _fmt_currency(s.get("median") if isinstance(s, dict) else s)
            lines.append(f"| {b} | {r_val}/mo | {s_val} |")

    # Trend data
    history = data.get("history") or data.get("trends") or []
    if isinstance(history, list) and history:
        recent = history[-3:]
        lines += ["", "### Recent Trends",
                   "| Month | Med. Price | Med. Rent |",
                   "|-------|-----------|-----------|"]
        for t in recent:
            month = _trunc_date(t.get("date") or t.get("month"))[:7]
            lines.append(
                f"| {month} | {_fmt_currency(t.get('medianPrice') or t.get('salePrice', {}).get('median') if isinstance(t.get('salePrice'), dict) else t.get('medianPrice'))} "
                f"| {_fmt_currency(t.get('medianRent') or t.get('rentalPrice', {}).get('median') if isinstance(t.get('rentalPrice'), dict) else t.get('medianRent'))}/mo |"
            )
    return "\n".join(lines)


def _fmt_single_sale_listing(data):
    lines = [
        f"## {_fmt_address(data)}",
        "",
        f"- **Price:** {_fmt_currency(data.get('price'))}",
        f"- **Beds:** {data.get('bedrooms', '-')} | **Baths:** {data.get('bathrooms', '-')}",
    ]
    sqft = data.get("squareFootage")
    lines.append(f"- **Sqft:** {f'{sqft:,}' if sqft else '-'}")
    lines += [
        f"- **Type:** {data.get('propertyType', '-')}",
        f"- **Year Built:** {data.get('yearBuilt', '-')}",
        f"- **Listed:** {_trunc_date(data.get('listedDate'))}",
        f"- **Status:** {data.get('status', '-')}",
        f"- **Days on Market:** {data.get('daysOnMarket', '-')}",
    ]
    lot = data.get("lotSize")
    if lot:
        lines.append(f"- **Lot:** {lot:,} sqft")
    if data.get("description"):
        lines += ["", "### Description", data["description"][:500]]
    return "\n".join(lines)


def _fmt_single_rental_listing(data):
    lines = [
        f"## {_fmt_address(data)}",
        "",
        f"- **Rent:** {_fmt_currency(data.get('price'))}/mo",
        f"- **Beds:** {data.get('bedrooms', '-')} | **Baths:** {data.get('bathrooms', '-')}",
    ]
    sqft = data.get("squareFootage")
    lines.append(f"- **Sqft:** {f'{sqft:,}' if sqft else '-'}")
    lines += [
        f"- **Type:** {data.get('propertyType', '-')}",
        f"- **Listed:** {_trunc_date(data.get('listedDate'))}",
        f"- **Status:** {data.get('status', '-')}",
    ]
    if data.get("description"):
        lines += ["", "### Description", data["description"][:500]]
    return "\n".join(lines)


def _fmt_rate_limit(data):
    remaining = data.get("remainingRequests", data.get("remaining", "?"))
    total = data.get("totalRequests", data.get("total", "?"))
    reset = _trunc_date(data.get("resetDate") or data.get("reset"))
    return f"**Rate Limit:** {remaining}/{total} requests remaining (resets {reset})"


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
) -> str:
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
    
    return _fmt_property_list(_proxy("/properties", params))

@mcp.tool()
def get_property_by_id(property_id: str, api_key: str = None) -> str:
    """Return a single property record by RentCast ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_property_detail(_proxy(f"/properties/{property_id}", {"api_key": api_key}))

@mcp.tool()
def get_value_estimate(address: str, api_key: str = None) -> str:
    """Return the current value AVM for an address."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_value_estimate(_proxy("/valuations/value", {"address": address, "api_key": api_key}))

@mcp.tool()
def get_rent_estimate(address: str, api_key: str = None) -> str:
    """Return the long-term rent AVM for an address."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_rent_estimate(_proxy("/valuations/rent/long-term", {"address": address, "api_key": api_key}))

@mcp.tool()
def search_sale_listings(
    city: str = None,
    state: str = None,
    bbox: str = None,
    limit: int = 20,
    api_key: str = None
) -> str:
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
    
    return _fmt_sale_listings(_proxy("/listings/sale", params))

@mcp.tool()
def search_rental_listings(
    city: str = None,
    state: str = None,
    bbox: str = None,
    limit: int = 20,
    api_key: str = None
) -> str:
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
    
    return _fmt_rental_listings(_proxy("/listings/rental/long-term", params))

@mcp.tool()
def get_market_stats(zip: str, api_key: str = None) -> str:
    """Get ZIP-level market statistics."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_market_stats(_proxy("/markets", {"zipCode": zip, "api_key": api_key}))

@mcp.tool()
def get_random_properties(limit: int = 10, api_key: str = None) -> str:
    """Return random sample properties for demo/testing."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    
    params = {"api_key": api_key, "limit": min(max(limit, 1), 100)}
    return _fmt_property_list(_proxy("/properties/random", params))

@mcp.tool()
def get_sale_listing_by_id(listing_id: str, api_key: str = None) -> str:
    """Return a single sale listing record by listing ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_single_sale_listing(_proxy(f"/listings/sale/{listing_id}", {"api_key": api_key}))

@mcp.tool()
def get_rental_listing_by_id(listing_id: str, api_key: str = None) -> str:
    """Return a single rental listing record by listing ID."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_single_rental_listing(_proxy(f"/listings/rental/long-term/{listing_id}", {"api_key": api_key}))

@mcp.tool()
def ping_rate_limit(api_key: str = None) -> str:
    """Check remaining quota for this API key."""
    if not api_key:
        api_key = os.getenv("RENTCAST_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (either as parameter or RENTCAST_API_KEY environment variable)")
    return _fmt_rate_limit(_proxy("/rate-limits", {"api_key": api_key}))

if __name__ == "__main__":
    mcp.run()
