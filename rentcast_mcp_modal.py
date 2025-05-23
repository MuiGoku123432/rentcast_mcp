"""
RentCast → MCP wrapper deployed on Modal.

• FastAPI provides the HTTP surface.
• `mcp_agent.fastapi.expose` turns each function into an MCP tool *and*
  autogenerates /.well-known/mcp.json.
• Users must pass their own RentCast API key as `api_key` in every call.
  (Smithery will inject it automatically when you publish the server there.)
"""

import os, requests, modal
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from mcp_agent.fastapi import expose   # https://github.com/lastmile-ai/mcp-agent :contentReference[oaicite:0]{index=0}

# ─────────────────────────────────────────── Modal boilerplate ──
image = (
    modal.Image.debian_slim()
    .pip_install_from_requirements_txt(
        [
            "fastapi[standard]",
            "pydantic>=2",
            "requests",
            "mcp-agent",
        ]
    )
)
app = modal.App("rentcast-mcp", image=image)

# ─────────────────────────────────────────── Shared helpers ──
BASE_URL = "https://api.rentcast.io/v1"

def _proxy(endpoint: str, params: dict):
    """Forward the call to RentCast, raise FastAPI-style HTTP errors on failure."""
    api_key = params.pop("api_key")
    headers = {"X-Api-Key": api_key}
    r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    return r.json()

fastapi_app = FastAPI(
    title="RentCast MCP Server",
    version="1.0.0",
    description="A complete MCP wrapper for every public RentCast endpoint."
)

# ─────────────────────────────────────────── MCP tools ──
@expose(
    fastapi_app,
    name="search_property",
    description="Find properties by address or location."
)
class SearchProperty(BaseModel):
    address: str | None = Field(None, description="Full street address.")
    city: str | None = Field(None, description="City name.")
    state: str | None = Field(None, description="Two-letter state code.")
    zip: str | None = Field(None, description="ZIP or ZIP+4.")
    limit: int | None = Field(20, ge=1, le=100, description="Max results.")
    api_key: str = Field(..., description="Your RentCast API key.")

    def run(self):
        return _proxy("/properties", self.model_dump(exclude_none=True))

@expose(
    fastapi_app,
    name="get_property_by_id",
    description="Retrieve a single property record by RentCast ID."
)
class GetPropertyByID(BaseModel):
    property_id: str
    api_key: str

    def run(self):
        return _proxy(f"/properties/{self.property_id}", {"api_key": self.api_key})

@expose(
    fastapi_app,
    name="get_value_estimate",
    description="Return the current value AVM for an address."
)
class GetValueEstimate(BaseModel):
    address: str
    api_key: str
    def run(self):
        return _proxy("/valuations/value", self.model_dump())

@expose(
    fastapi_app,
    name="get_rent_estimate",
    description="Return the long-term rent AVM for an address."
)
class GetRentEstimate(BaseModel):
    address: str
    api_key: str
    def run(self):
        return _proxy("/valuations/rent/long-term", self.model_dump())

@expose(
    fastapi_app,
    name="search_sale_listings",
    description="Search active *sale* listings."
)
class SearchSaleListings(BaseModel):
    city: str | None = None
    state: str | None = None
    bbox: str | None = Field(
        None,
        description="Bounding box 'min_lat,min_lon,max_lat,max_lon'"
    )
    limit: int | None = Field(20, ge=1, le=100)
    api_key: str
    def run(self):
        return _proxy("/listings/sale", self.model_dump(exclude_none=True))

@expose(
    fastapi_app,
    name="search_rental_listings",
    description="Search active *rental* listings."
)
class SearchRentalListings(BaseModel):
    city: str | None = None
    state: str | None = None
    bbox: str | None = None
    limit: int | None = Field(20, ge=1, le=100)
    api_key: str
    def run(self):
        return _proxy("/listings/rental/long-term", self.model_dump(exclude_none=True))

@expose(
    fastapi_app,
    name="get_market_stats",
    description="Return market-level stats for a ZIP code."
)
class GetMarketStats(BaseModel):
    zip: str = Field(..., description="Five-digit ZIP.")
    api_key: str
    def run(self):
        return _proxy("/markets", self.model_dump())

@expose(
    fastapi_app,
    name="get_random_properties",
    description="Fetch random sample properties (handy for demos)."
)
class GetRandom(BaseModel):
    limit: int | None = Field(10, ge=1, le=100)
    api_key: str
    def run(self):
        return _proxy("/properties/random", self.model_dump())

@expose(
    fastapi_app,
    name="ping_rate_limit",
    description="Return current rate-limit status for the supplied key."
)
class PingRateLimit(BaseModel):
    api_key: str
    def run(self):
        return _proxy("/rate-limits", {"api_key": self.api_key})

# ─────────────────────────────────────────── Modal ASGI entry ──
@app.function()
@modal.asgi_app()
def fastapi_entry():
    return fastapi_app
