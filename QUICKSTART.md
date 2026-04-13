# 🎯 DeepMap Visualization - Quick Start

## ⚡ Bắt đầu nhanh (1 phút)

### Cách 1: Chạy tự động (Recommended)
```bash
python run_visualization.py
```
✅ Tự động khởi động backend + dashboard

### Cách 2: Chạy thủ công

**Terminal 1 - Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Dashboard:**
```bash
python -m http.server 8080
```

**Sau đó mở:**
```
http://localhost:8080/index.html
```

## 📋 Các file mới tạo

| File | Mô tả |
|------|-------|
| `index.html` | Dashboard visualization chính |
| `run_visualization.py` | Script tự động khởi động tất cả services |
| `VISUALIZATION_GUIDE.md` | Hướng dẫn chi tiết |

## 🔧 Yêu cầu hệ thống

```bash
pip install fastapi uvicorn requests
```

## 🗺️ Tính năng Dashboard

✅ **Bản đồ Tương tác** - OpenStreetMap với markers màu sắc
✅ **3 Biểu đồ Thống kê** - Hot Score, Distance, Type Distribution  
✅ **Danh sách POI** - Top 10 địa điểm được đề xuất
✅ **Thống kê Tóm tắt** - Các chỉ số chính
✅ **Responsive Design** - Hoạt động tốt trên mọi màn hình

## 📍 Ví dụ Sử dụng

**Tìm kiếm tại Saigon:**
- Vĩ độ: `10.869638`
- Kinh độ: `106.803820`
- Bán kính: `1000` (mét)

## 🎨 Color Coding (Bản đồ)

| Màu | Ý nghĩa |
|-----|---------|
| 🔴 Red | Hot Score ≥ 8 (Rất hot) |
| 🟠 Orange | Hot Score 6-8 (Hot) |
| 🟡 Yellow | Hot Score 4-6 (Bình thường) |
| ⚪ Grey | Hot Score < 4 (Ít hot) |

## 📊 API Response

```json
{
    "recommend": [
        {
            "name": "Landmark Restaurant",
            "type": "restaurant",
            "distance": 450,
            "lat": 10.87,
            "lon": 106.81,
            "hot_score": 8.5
        }
    ]
}
```

## 🐛 Troubleshooting

| Vấn đề | Giải pháp |
|--------|----------|
| Map không hiển thị | Kiểm tra internet connection |
| CORS error | Backend cần CORS middleware (đã thêm) |
| API không response | Đảm bảo backend chạy port 8000 |
| Port 8000/8080 bị chiếm | Sửa port trong code |

## 📚 Tài liệu Chi Tiết

Xem: [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)

## 🚀 Deploy (Optional)

Để deploy lên production:
1. Thay `allow_origins=["*"]` thành domain cần thiết
2. Deploy backend trên server (AWS, Heroku, v.v.)
3. Deploy HTML lên static hosting (GitHub Pages, Netlify, v.v.)

---

**Enjoy! 🎉**
