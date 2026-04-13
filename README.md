# Hot Places Recommendation System

Hệ thống gợi ý các địa điểm "hot" xung quanh khu vực được chọn trên bản đồ, sử dụng dữ liệu từ OpenStreetMap và mô hình AI đánh giá nhận thức con người.

## Cấu trúc dự án

- `backend.py`: API backend sử dụng FastAPI
- `run_backend.py`: Script chạy server
- `model_integration.py`: Tích hợp mô hình đánh giá hình ảnh địa điểm
- `map/apistreetmap.py`: Module lấy dữ liệu POI từ OpenStreetMap
- `human-perception-place-pulse/`: Mô hình đánh giá nhận thức con người từ hình ảnh đường phố
- `requirements_backend.txt`: Dependencies cho backend

## Cài đặt

1. Cài đặt dependencies cho backend:
   ```
   pip install -r requirements_backend.txt
   ```

2. (Tùy chọn) Cài đặt dependencies cho mô hình AI:
   ```
   pip install -r human-perception-place-pulse/requirements.txt
   ```

3. (Tùy chọn) Tải mô hình AI (chạy eval.py một lần):
   ```
   cd human-perception-place-pulse
   python eval.py
   ```

## Chạy hệ thống

```
python run_backend.py
```

API sẽ chạy trên http://localhost:8000

## API Endpoint

- `POST /recommend`: Gửi lat, lon, radius để nhận danh sách gợi ý POI

Ví dụ request:
```json
{
  "lat": 10.869638,
  "lon": 106.803820,
  "radius": 1000
}
```

Response: Danh sách 10 POI gần nhất, sắp xếp theo điểm "hot" (restaurant/cafe/attraction = 8.0, park/market = 7.0, etc.) và khoảng cách.

## Frontend Integration

Xem `FRONTEND_INTEGRATION.md` để tích hợp với frontend React/Vite.

## Tính năng hiện tại

- ✅ Lấy dữ liệu POI từ OpenStreetMap (restaurant, cafe, park, supermarket, hospital, school, bus_stop, attraction)
- ✅ Tính khoảng cách Haversine
- ✅ Gợi ý dựa trên loại POI (hot_score giả định)
- ✅ API FastAPI với validation
- ✅ Sắp xếp theo hot_score và khoảng cách

## Tính năng tương lai

- 🔄 Tích hợp Google Street View để lấy hình ảnh thực tế
- 🔄 Sử dụng mô hình AI để tính điểm "hot" chính xác dựa trên hình ảnh
- 🔄 Thêm filters và sorting options
- 🔄 Caching và optimization

## Frontend Integration

Xem `FRONTEND_INTEGRATION.md` để tích hợp với frontend React/Vite.

## Tính năng tương lai

- Tích hợp Google Street View để lấy hình ảnh thực tế
- Sử dụng mô hình AI để tính điểm "hot" chính xác
- Thêm filters và sorting options</content>
<parameter name="filePath">e:\Project\DeepMap\README.md