# 🗺️ DeepMap - Hướng dẫn sử dụng Dashboard Visualization

## Mô tả

Dashboard interaktif này giúp bạn:
- 📍 Xem các POI (Points of Interest) trên bản đồ OpenStreetMap
- 📊 Visualize dữ liệu hot scores, khoảng cách, và phân loại
- 📈 Phân tích thống kê các địa điểm được đề xuất
- 🔍 Tìm kiếm địa điểm trong một bán kính nhất định

## Yêu cầu

- Python 3.8+
- FastAPI
- Requests
- Trình duyệt modern hỗ trợ HTML5

## Cài đặt & Chạy

### 1. Cài đặt dependencies:
```bash
pip install -r requirements_backend.txt
```

Nếu chưa có, cài đặt:
```bash
pip install fastapi uvicorn requests
```

### 2. Khởi động Backend API:
```bash
python run_backend.py
```

Hoặc:
```bash
uvicorn backend:app --reload --port 8000
```

Backend sẽ chạy tại: `http://localhost:8000`

### 3. Mở Dashboard:
- Mở file `index.html` trong trình duyệt
- Hoặc dùng Python HTTP server:
  ```bash
  python -m http.server 8080
  ```
  Rồi mở: `http://localhost:8080/index.html`

## Tính năng

### 🔍 Tìm kiếm
1. Nhập **Vĩ độ (Latitude)** và **Kinh độ (Longitude)**
2. Chọn **Bán kính (Radius)** theo thích hợp
3. Nhấn **🔍 Tìm kiếm**

**Ví dụ:**
- Vĩ độ: 10.869638
- Kinh độ: 106.803820
- Bán kính: 1000 (mét)

### 📍 Bản đồ Tương tác
- **🔵 Marker Blue** - Vị trí tìm kiếm
- **🔴 Marker Red** - Hot Score >= 8 (Rất hot)
- **🟠 Marker Orange** - Hot Score 6-8 (Hot)
- **🟡 Marker Yellow** - Hot Score 4-6 (Bình thường)
- **⚪ Marker Grey** - Hot Score < 4 (Ít hot)

Click vào marker để xem chi tiết.

### 📋 Danh sách Địa điểm
Hiển thị top 10 địa điểm được sắp xếp theo:
1. Hot Score (cao nhất trước)
2. Khoảng cách (gần nhất trước)

### 📊 Biểu đồ Thống kê

**1. Hot Score Distribution (Phân bố Hot Score)**
- Bar chart hiển thị hot score của mỗi địa điểm
- Màu sắc tương ứng với mức độ hot

**2. Distance Distribution (Phân bố Khoảng cách)**
- Bar chart hiển thị khoảng cách từ vị trí tìm kiếm
- Đơn vị: mét

**3. Type Distribution (Phân bố Loại địa điểm)**
- Doughnut chart hiển thị % của từng loại địa điểm
- Loại có thể bao gồm: restaurant, cafe, park, attraction, supermarket, v.v.

### 📈 Thống kê Tổng hợp

Hiển thị 4 chỉ số chính:
- **Tổng địa điểm** - Số lượng POI được tìm thấy
- **Hot Score trung bình** - Trung bình cộng hot scores
- **Khoảng cách trung bình** - Trung bình khoảng cách (km)
- **Hot Score cao nhất** - Giá trị hot score lớn nhất

## API Endpoints

### POST /recommend
Tìm các địa điểm được đề xuất

**Request:**
```json
{
    "lat": 10.869638,
    "lon": 106.803820,
    "radius": 1000
}
```

**Response:**
```json
[
    {
        "name": "Restaurant Name",
        "type": "restaurant",
        "distance": 500,
        "lat": 10.87,
        "lon": 106.81,
        "hot_score": 8.5
    }
]
```

## Loại Địa điểm & Hot Score

| Loại | Hot Score |
|------|-----------|
| restaurant, cafe, attraction | 8.0 |
| park, marketplace | 7.0 |
| supermarket | 6.0 |
| hospital, school, bus_stop | 4.0 |
| Khác | 5.0 |

## Sử dụng với API từ xa

Nếu backend chạy trên server khác, sửa dòng này trong `index.html`:
```javascript
const API_URL = 'http://your-server-address:8000';
```

## Debugging

### Lỗi CORS
Nếu gặp lỗi CORS, đảm bảo backend.py đã được cập nhật với CORS middleware.

### Map không hiển thị
- Kiểm tra internet connection
- Leaflet CDN có thể bị block

### API không respond
- Kiểm tra backend đang chạy: `http://localhost:8000/docs`
- Kiểm tra console của trình duyệt (F12) để xem lỗi

## Mở rộng

### Thêm Loại Địa điểm
Sửa hàm `recommend_hot_places()` trong `backend.py`:
```python
if poi_type in ['restaurant', 'cafe', 'attraction']:
    hot_score = 8.0
# Thêm loại mới tại đây
```

### Thay đổi Hot Score Logic
Sửa phần scoring logic trong `backend.py` hoặc JavaScript.

## Liên hệ & Support

Nếu gặp vấn đề, kiểm tra:
1. Backend đang chạy?
2. URL API đúng?
3. Coordinates hợp lệ?
4. Internet connection OK?
