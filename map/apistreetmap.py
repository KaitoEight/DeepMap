import requests
import math
import time

# --- 1. HÀM TÍNH KHOẢNG CÁCH HAVERSINE ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Bán kính Trái Đất (mét)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- 2. HÀM LẤY DỮ LIỆU TỪ OVERPASS API (CÓ RETRY) ---
def get_nearby_pois(lat, lon, radius=1000, retries=3):
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Thêm [timeout:30] để server không ngắt kết nối sớm
    overpass_query = f"""
    [out:json][timeout:30];
    (
      nwr["amenity"="hospital"](around:{radius},{lat},{lon});
      nwr["amenity"="school"](around:{radius},{lat},{lon});
      nwr["amenity"="marketplace"](around:{radius},{lat},{lon});
      nwr["shop"="supermarket"](around:{radius},{lat},{lon});
      nwr["highway"="bus_stop"](around:{radius},{lat},{lon});
    );
    out center;
    """
    
    headers = {'User-Agent': 'RealEstateRecommendSystem/1.0'}
    
    for attempt in range(retries):
        try:
            # Tăng timeout của requests lên 35s
            response = requests.post(overpass_url, data=overpass_query, headers=headers, timeout=35)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 504:
                print(f"⚠️ Lần {attempt+1}: Server nghẽn, đang thử lại...")
                time.sleep(2)
            else:
                print(f"❌ Lỗi HTTP: {e}")
                break
        except Exception as e:
            print(f"❌ Lỗi mạng: {e}")
            break
            
    return None

# --- 3. CHẠY THỬ VÀ XỬ LÝ DỮ LIỆU ---
home_lat, home_lon = 10.869638, 106.803820 # Khu Làng Đại học / Suối Tiên

print("🚀 Đang quét dữ liệu, vui lòng đợi...")
poi_data = get_nearby_pois(home_lat, home_lon)

if poi_data:
    # Dùng List thay vì Set để dễ dàng lưu khoảng cách và sắp xếp
    poi_list = [] 
    
    # Dùng Set phụ để kiểm tra trùng lặp tên (tránh việc 1 trạm xe buýt hiện 2 lần)
    seen_names = set() 

    for element in poi_data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name')
        
        # Sửa lỗi lấy nhãn: Gom cả amenity, shop, và highway
        poi_type = tags.get('amenity') or tags.get('shop') or tags.get('highway')
        
        # Nếu không có tên nhưng là trạm xe buýt, cho nó cái tên mặc định
        if not name and poi_type == 'bus_stop':
            name = "Trạm xe buýt (Không tên)"
            
        # Lấy tọa độ của điểm đó (xử lý cả dạng node và way)
        poi_lat = element.get('lat') or element.get('center', {}).get('lat')
        poi_lon = element.get('lon') or element.get('center', {}).get('lon')
        
        if name and poi_lat and poi_lon and name not in seen_names:
            seen_names.add(name)
            
            # Tính khoảng cách
            distance = haversine(home_lat, home_lon, poi_lat, poi_lon)
            
            # Lưu vào danh sách dưới dạng Dictionary
            poi_list.append({
                "name": name,
                "type": poi_type,
                "distance": distance
            })

    # SẮP XẾP DANH SÁCH THEO KHOẢNG CÁCH (Gần -> Xa)
    poi_list_sorted = sorted(poi_list, key=lambda x: x['distance'])

    print(f"\n✅ Tìm thấy {len(poi_list_sorted)} tiện ích xung quanh:")
    print("-" * 50)
    for poi in poi_list_sorted:
        # Format khoảng cách cho đẹp (vd: 450m hoặc 1.2km)
        dist_str = f"{poi['distance']:.0f}m" if poi['distance'] < 1000 else f"{poi['distance']/1000:.1f}km"
        
        # In ra màn hình: [Khoảng cách] Tên địa điểm (Loại)
        print(f"[{dist_str}] {poi['name']} ({poi['type']})")

else:
    print("⚠️ Không lấy được dữ liệu.")