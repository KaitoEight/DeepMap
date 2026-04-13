from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import math
import time
from typing import List, Optional, Dict

from real_estate_data import (
    MOCK_LISTINGS,
    haversine,
    filter_listings_in_bounds,
    calculate_amenity_score,
    calculate_price_score,
    calculate_area_score,
    calculate_overall_score,
    analyze_area,
)

app = FastAPI(
    title="DeepMap — Real Estate Recommendation System",
    version="2.0.0",
    description="Hệ thống recommend bất động sản dựa trên khu vực bản đồ, phân tích tiện ích xung quanh.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class LocationRequest(BaseModel):
    lat: float
    lon: float
    radius: int = 1000

class AreaBoundsRequest(BaseModel):
    sw_lat: float
    sw_lon: float
    ne_lat: float
    ne_lon: float
    # Optional filters
    type: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    min_area: Optional[float] = None
    bedrooms: Optional[int] = None
    sort_by: Optional[str] = "overall_score"  # overall_score, price, area, amenity

class POI(BaseModel):
    name: str
    type: str
    distance: float
    lat: float
    lon: float
    hot_score: float


# ============================================================
# OVERPASS API HELPER
# ============================================================

def get_nearby_pois(lat, lon, radius=1000, retries=3):
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    overpass_query = """
    [out:json][timeout:30];
    (
      nwr["amenity"="hospital"](around:%d,%f,%f);
      nwr["amenity"="school"](around:%d,%f,%f);
      nwr["amenity"="marketplace"](around:%d,%f,%f);
      nwr["shop"="supermarket"](around:%d,%f,%f);
      nwr["highway"="bus_stop"](around:%d,%f,%f);
      nwr["amenity"="restaurant"](around:%d,%f,%f);
      nwr["amenity"="cafe"](around:%d,%f,%f);
      nwr["tourism"="attraction"](around:%d,%f,%f);
      nwr["leisure"="park"](around:%d,%f,%f);
    );
    out center;
    """ % (radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon, radius, lat, lon)
    
    headers = {'User-Agent': 'DeepMapRecommendSystem/2.0'}
    
    for attempt in range(retries):
        try:
            response = requests.post(overpass_url, data=overpass_query, headers=headers, timeout=35)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 504:
                print(f"Attempt {attempt+1}: Server busy, retrying...")
                time.sleep(2)
            else:
                print(f"HTTP Error: {e}")
                break
        except Exception as e:
            print(f"Network Error: {e}")
            break
            
    return None


def get_pois_in_bbox(sw_lat, sw_lon, ne_lat, ne_lon, retries=3):
    """Lấy POIs trong bounding box thay vì circle."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    overpass_query = f"""
    [out:json][timeout:30];
    (
      nwr["amenity"="hospital"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["amenity"="school"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["amenity"="marketplace"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["shop"="supermarket"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["highway"="bus_stop"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["amenity"="restaurant"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["amenity"="cafe"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["tourism"="attraction"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
      nwr["leisure"="park"]({sw_lat},{sw_lon},{ne_lat},{ne_lon});
    );
    out center;
    """
    
    headers = {'User-Agent': 'DeepMapRecommendSystem/2.0'}
    
    for attempt in range(retries):
        try:
            response = requests.post(overpass_url, data=overpass_query, headers=headers, timeout=35)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if hasattr(response, 'status_code') and response.status_code == 504:
                print(f"Attempt {attempt+1}: Server busy, retrying...")
                time.sleep(2)
            else:
                print(f"HTTP Error: {e}")
                break
        except Exception as e:
            print(f"Network Error: {e}")
            break
            
    return None


# ============================================================
# API — HOT PLACES (giữ nguyên endpoint cũ)
# ============================================================

@app.post("/recommend", response_model=List[POI])
async def recommend_hot_places(request: LocationRequest):
    poi_data = get_nearby_pois(request.lat, request.lon, request.radius)
    
    if not poi_data:
        raise HTTPException(status_code=500, detail="Unable to fetch POI data")
    
    poi_list = []
    seen_names = set()
    
    for element in poi_data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name')
        
        poi_type = tags.get('amenity') or tags.get('shop') or tags.get('highway') or tags.get('tourism') or tags.get('leisure')
        
        if not name and poi_type == 'bus_stop':
            name = "Bus Stop (Unnamed)"
            
        poi_lat = element.get('lat') or element.get('center', {}).get('lat')
        poi_lon = element.get('lon') or element.get('center', {}).get('lon')
        
        if name and poi_lat and poi_lon and name not in seen_names:
            seen_names.add(name)
            
            distance = haversine(request.lat, request.lon, poi_lat, poi_lon)
            
            hot_score = 5.0
            if poi_type in ['supermarket']: 
                hot_score = 9.0
            elif poi_type in ['attraction']:
                hot_score = 7.0
            elif poi_type in ['hospital']:
                hot_score = 6.0
            else:
                hot_score = 4.0
            
            poi_list.append({
                "name": name,
                "type": poi_type,
                "distance": distance,
                "lat": poi_lat,
                "lon": poi_lon,
                "hot_score": hot_score
            })
    
    poi_list_sorted = sorted(poi_list, key=lambda x: (-x['hot_score'], x['distance']))
    
    return poi_list_sorted[:10]


# ============================================================
# API — REAL ESTATE RECOMMENDATION
# ============================================================

@app.post("/api/area-recommend")
async def area_recommend(request: AreaBoundsRequest):
    """
    Recommend BĐS trong vùng chọn trên bản đồ.
    - Lọc listings trong bounds
    - Lấy POIs trong vùng từ Overpass
    - Tính amenity score cho từng listing
    - Tính overall score và sort
    """
    # 1. Lọc listings trong bounds
    filters = {}
    if request.type:
        filters["type"] = request.type
    if request.max_price:
        filters["max_price"] = request.max_price
    if request.min_price:
        filters["min_price"] = request.min_price
    if request.min_area:
        filters["min_area"] = request.min_area
    if request.bedrooms:
        filters["bedrooms"] = request.bedrooms

    matched_listings = filter_listings_in_bounds(
        MOCK_LISTINGS,
        request.sw_lat, request.sw_lon,
        request.ne_lat, request.ne_lon,
        filters if filters else None,
    )
    
    if not matched_listings:
        return {
            "listings": [],
            "area_analysis": None,
            "total": 0,
            "message": "Không tìm thấy BĐS nào trong khu vực được chọn."
        }
    
    # 2. Mở rộng bounds một chút để lấy POIs xung quanh
    padding = 0.005  # ~500m
    poi_data = get_pois_in_bbox(
        request.sw_lat - padding, request.sw_lon - padding,
        request.ne_lat + padding, request.ne_lon + padding,
    )
    
    pois_raw = poi_data.get("elements", []) if poi_data else []
    
    # 3. Tính score cho từng listing
    for listing in matched_listings:
        amenity_result = calculate_amenity_score(
            listing["lat"], listing["lon"], pois_raw, radius=800
        )
        listing["amenity_score"] = amenity_result["total_score"]
        listing["amenity_details"] = amenity_result["category_scores"]
        listing["nearby_poi_count"] = amenity_result["poi_count"]
        listing["nearby_pois"] = amenity_result["nearby_pois"][:5]
        
        price_score = calculate_price_score(listing["price"], listing["type"])
        listing["price_score"] = price_score
        
        area_score = calculate_area_score(listing["area"], listing["type"])
        listing["area_score"] = area_score
        
        variety_count = sum(1 for v in amenity_result["category_scores"].values() if v > 0)
        variety_score = min(variety_count * 1.67, 10)
        listing["variety_score"] = round(variety_score, 1)
        
        listing["overall_score"] = calculate_overall_score(
            amenity_result["total_score"],
            price_score,
            area_score,
            variety_score,
        )
    
    # 4. Sort
    sort_key = request.sort_by or "overall_score"
    reverse = True
    if sort_key == "price":
        reverse = False  # giá thấp trước
    
    matched_listings.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse)
    
    # 5. Phân tích khu vực
    area_analysis = analyze_area(pois_raw, {
        "sw_lat": request.sw_lat,
        "sw_lon": request.sw_lon,
        "ne_lat": request.ne_lat,
        "ne_lon": request.ne_lon,
    })
    
    return {
        "listings": matched_listings,
        "area_analysis": area_analysis,
        "total": len(matched_listings),
    }


@app.post("/api/area-analyze")
async def area_analyze(request: AreaBoundsRequest):
    """Phân tích tiện ích khu vực (không cần BĐS)."""
    padding = 0.003
    poi_data = get_pois_in_bbox(
        request.sw_lat - padding, request.sw_lon - padding,
        request.ne_lat + padding, request.ne_lon + padding,
    )
    
    if not poi_data:
        raise HTTPException(status_code=500, detail="Không thể lấy dữ liệu POI")
    
    result = analyze_area(poi_data.get("elements", []), {
        "sw_lat": request.sw_lat,
        "sw_lon": request.sw_lon,
        "ne_lat": request.ne_lat,
        "ne_lon": request.ne_lon,
    })
    
    return result


@app.get("/api/listings")
async def get_all_listings(
    type: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
):
    """Lấy tất cả listings (có filter)."""
    result = MOCK_LISTINGS
    if type:
        result = [l for l in result if l["type"] == type]
    if max_price:
        result = [l for l in result if l["price"] <= max_price]
    if min_price:
        result = [l for l in result if l["price"] >= min_price]
    return result


@app.get("/api/listing/{listing_id}")
async def get_listing_detail(listing_id: int):
    """Chi tiết 1 listing."""
    for l in MOCK_LISTINGS:
        if l["id"] == listing_id:
            return l
    raise HTTPException(status_code=404, detail="Listing not found")


@app.get("/api/listing-types")
async def get_listing_types():
    """Lấy danh sách loại BĐS."""
    types = list(set(l["type"] for l in MOCK_LISTINGS))
    return types


@app.get("/api/stats")
async def get_stats():
    """Thống kê tổng quát."""
    prices = [l["price"] for l in MOCK_LISTINGS]
    areas = [l["area"] for l in MOCK_LISTINGS]
    return {
        "total_listings": len(MOCK_LISTINGS),
        "avg_price": round(sum(prices) / len(prices), 1),
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_area": round(sum(areas) / len(areas), 1),
        "types": {t: sum(1 for l in MOCK_LISTINGS if l["type"] == t) for t in set(l["type"] for l in MOCK_LISTINGS)},
    }


# Serve static files
@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")