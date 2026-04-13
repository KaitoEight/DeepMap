"""
DeepMap — Real Estate Data Module
Dữ liệu BĐS mẫu & thuật toán scoring cho hệ thống recommend.
Production-ready: dễ dàng thay thế mock data bằng database thực.
"""

from __future__ import annotations
import math
import random
from typing import List, Dict, Optional

# ============================================================
# 1. MOCK LISTINGS — Khu vực Thủ Đức / Làng Đại Học
# ============================================================

MOCK_LISTINGS: List[Dict] = [
    # --- Phòng trọ ---
    {
        "id": 1, "title": "Phòng trọ cao cấp gần ĐH Nông Lâm",
        "type": "Phòng trọ", "price": 3.5, "area": 25,
        "address": "43 Kha Vạn Cân, Linh Trung, Thủ Đức",
        "lat": 10.8712, "lon": 106.7985,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng trọ mới xây, có gác lửng, ban công thoáng mát. Gần ĐH Nông Lâm, chợ Thủ Đức.",
        "amenities": ["Wifi", "Máy lạnh", "Gác lửng", "Ban công"],
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400"
    },
    {
        "id": 2, "title": "Phòng trọ sinh viên giá rẻ Linh Xuân",
        "type": "Phòng trọ", "price": 1.8, "area": 18,
        "address": "120 Quốc lộ 1A, Linh Xuân, Thủ Đức",
        "lat": 10.8658, "lon": 106.7892,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng trọ giá rẻ cho sinh viên, an ninh 24/7, gần trạm xe buýt.",
        "amenities": ["Wifi", "Giữ xe"],
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400"
    },
    {
        "id": 3, "title": "Phòng trọ full nội thất Hiệp Bình Phước",
        "type": "Phòng trọ", "price": 4.0, "area": 28,
        "address": "Đường số 8, Hiệp Bình Phước, Thủ Đức",
        "lat": 10.8535, "lon": 106.7110,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Full nội thất, tự do giờ giấc. Gần Gigamall, bến xe Miền Đông mới.",
        "amenities": ["Wifi", "Máy lạnh", "Tủ lạnh", "Máy giặt"],
        "image": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400"
    },
    {
        "id": 4, "title": "Phòng trọ sạch sẽ gần ĐHQG",
        "type": "Phòng trọ", "price": 2.5, "area": 20,
        "address": "Nguyễn Xí, Linh Trung, Thủ Đức",
        "lat": 10.8690, "lon": 106.8010,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng sạch đẹp, yên tĩnh, gần cổng ĐHQG. Phù hợp sinh viên và nhân viên văn phòng.",
        "amenities": ["Wifi", "Máy lạnh", "Bảo vệ 24/7"],
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400"
    },
    {
        "id": 5, "title": "Phòng trọ mini Linh Chiểu",
        "type": "Phòng trọ", "price": 2.0, "area": 16,
        "address": "68 Hoàng Diệu 2, Linh Chiểu, Thủ Đức",
        "lat": 10.8520, "lon": 106.7640,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng trọ mini tiện nghi, gần ĐH Sư Phạm Kỹ Thuật.",
        "amenities": ["Wifi", "Bếp chung"],
        "image": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=400"
    },
    {
        "id": 6, "title": "Phòng trọ cao cấp Phạm Văn Đồng",
        "type": "Phòng trọ", "price": 4.5, "area": 30,
        "address": "188 Phạm Văn Đồng, Hiệp Bình Chánh, Thủ Đức",
        "lat": 10.8410, "lon": 106.7230,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng rộng, nội thất cao cấp, view đẹp. Gần Emart, Gigamall.",
        "amenities": ["Wifi", "Máy lạnh", "Tủ lạnh", "Ban công", "Thang máy"],
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"
    },

    # --- Chung cư ---
    {
        "id": 7, "title": "Căn hộ Vinhomes Grand Park 1PN",
        "type": "Chung cư", "price": 7.0, "area": 45,
        "address": "Nguyễn Xiển, Long Bình, Thủ Đức",
        "lat": 10.8445, "lon": 106.8380,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Căn hộ Vinhomes Grand Park, full nội thất, tiện ích 5 sao. Gồm gym, hồ bơi, công viên.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "Công viên", "An ninh 24/7"],
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400"
    },
    {
        "id": 8, "title": "Căn hộ Masteri Thảo Điền 2PN",
        "type": "Chung cư", "price": 18.0, "area": 75,
        "address": "Xa Lộ Hà Nội, Thảo Điền, Thủ Đức",
        "lat": 10.8025, "lon": 106.7420,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ cao cấp Masteri, view sông Sài Gòn, full nội thất nhập khẩu.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "Sauna", "BBQ"],
        "image": "https://images.unsplash.com/photo-1502672023488-70e25813eb80?w=400"
    },
    {
        "id": 9, "title": "Căn hộ The Sun Avenue 2PN",
        "type": "Chung cư", "price": 12.0, "area": 68,
        "address": "28 Mai Chí Thọ, An Phú, Thủ Đức",
        "lat": 10.7880, "lon": 106.7530,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ The Sun Avenue, nội thất cơ bản, gần Metro, tiện di chuyển.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym"],
        "image": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=400"
    },
    {
        "id": 10, "title": "Căn hộ Centana Thủ Thiêm 3PN",
        "type": "Chung cư", "price": 14.0, "area": 88,
        "address": "36 Mai Chí Thọ, An Phú, Thủ Đức",
        "lat": 10.7910, "lon": 106.7480,
        "bedrooms": 3, "bathrooms": 2,
        "description": "Căn 3 phòng ngủ rộng rãi, phù hợp gia đình. Gần trường quốc tế, bệnh viện.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Sân chơi trẻ em"],
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400"
    },
    {
        "id": 11, "title": "Căn hộ Flora Novia 2PN giá tốt",
        "type": "Chung cư", "price": 8.5, "area": 60,
        "address": "Phạm Văn Đồng, Hiệp Bình Chánh, Thủ Đức",
        "lat": 10.8380, "lon": 106.7180,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ Flora Novia, giá tốt, nội thất cơ bản. Gần Gigamall.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi"],
        "image": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=400"
    },
    {
        "id": 12, "title": "Căn hộ Bình Thọ Studio",
        "type": "Chung cư", "price": 5.5, "area": 35,
        "address": "Đường số 5, Bình Thọ, Thủ Đức",
        "lat": 10.8490, "lon": 106.7580,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Studio full nội thất, gần ĐH GTVT, chợ Bình Thọ.",
        "amenities": ["Wifi", "Máy lạnh", "Tủ lạnh", "Máy giặt"],
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400"
    },

    # --- Nhà nguyên căn ---
    {
        "id": 13, "title": "Nhà nguyên căn 1 trệt 1 lầu Linh Đông",
        "type": "Nhà nguyên căn", "price": 8.0, "area": 60,
        "address": "Phạm Văn Đồng, Linh Đông, Thủ Đức",
        "lat": 10.8460, "lon": 106.7340,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Nhà 1 trệt 1 lầu, có sân để xe, phù hợp gia đình nhỏ.",
        "amenities": ["Wifi", "Sân để xe", "Sân thượng"],
        "image": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400"
    },
    {
        "id": 14, "title": "Nhà phố Thảo Điền 3 tầng",
        "type": "Nhà nguyên căn", "price": 35.0, "area": 120,
        "address": "Xuân Thủy, Thảo Điền, Thủ Đức",
        "lat": 10.8065, "lon": 106.7350,
        "bedrooms": 4, "bathrooms": 3,
        "description": "Nhà phố sang trọng khu Thảo Điền, đầy đủ nội thất cao cấp, có garage.",
        "amenities": ["Wifi", "Máy lạnh", "Garage", "Sân vườn", "Camera an ninh"],
        "image": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"
    },
    {
        "id": 15, "title": "Nhà nguyên căn mặt tiền Linh Xuân",
        "type": "Nhà nguyên căn", "price": 10.0, "area": 80,
        "address": "Quốc lộ 1A, Linh Xuân, Thủ Đức",
        "lat": 10.8630, "lon": 106.7870,
        "bedrooms": 3, "bathrooms": 2,
        "description": "Nhà mặt tiền đường lớn, phù hợp ở và kinh doanh.",
        "amenities": ["Wifi", "Mặt tiền", "Sân để xe"],
        "image": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400"
    },
    {
        "id": 16, "title": "Nhà nguyên căn hẻm xe hơi Bình Thọ",
        "type": "Nhà nguyên căn", "price": 12.0, "area": 90,
        "address": "Đường số 11, Bình Thọ, Thủ Đức",
        "lat": 10.8510, "lon": 106.7620,
        "bedrooms": 3, "bathrooms": 2,
        "description": "Nhà hẻm xe hơi, 1 trệt 2 lầu, gần chợ Bình Thọ.",
        "amenities": ["Wifi", "Máy lạnh", "Sân để xe", "Sân thượng"],
        "image": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400"
    },

    # --- Căn hộ dịch vụ ---
    {
        "id": 17, "title": "Căn hộ dịch vụ cao cấp An Phú",
        "type": "Căn hộ dịch vụ", "price": 10.0, "area": 40,
        "address": "Lương Định Của, An Phú, Thủ Đức",
        "lat": 10.7940, "lon": 106.7460,
        "bedrooms": 1, "bathrooms": 1,
        "description": "CHDV full nội thất cao cấp, dọn phòng hàng tuần, gần Metro.",
        "amenities": ["Wifi", "Máy lạnh", "Dọn phòng", "Bếp", "Thang máy"],
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"
    },
    {
        "id": 18, "title": "CHDV gần KCN Công Nghệ Cao",
        "type": "Căn hộ dịch vụ", "price": 5.0, "area": 30,
        "address": "Đường số 1, Linh Trung, Thủ Đức",
        "lat": 10.8595, "lon": 106.8050,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phù hợp chuyên gia, kỹ sư làm việc tại SHTP. Đầy đủ nội thất.",
        "amenities": ["Wifi", "Máy lạnh", "Tủ lạnh", "Bếp"],
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400"
    },

    # --- Thêm listings phân bố đều ---
    {
        "id": 19, "title": "Phòng trọ view công viên Suối Tiên",
        "type": "Phòng trọ", "price": 3.0, "area": 22,
        "address": "Xa lộ Hà Nội, Linh Trung, Thủ Đức",
        "lat": 10.8680, "lon": 106.8120,
        "bedrooms": 1, "bathrooms": 1,
        "description": "View đẹp, thoáng mát, gần Suối Tiên và bến xe Miền Đông mới.",
        "amenities": ["Wifi", "Ban công", "Máy lạnh"],
        "image": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=400"
    },
    {
        "id": 20, "title": "Căn hộ Lavita Charm 2PN",
        "type": "Chung cư", "price": 9.0, "area": 65,
        "address": "Nguyễn Văn Bá, Trường Thọ, Thủ Đức",
        "lat": 10.8380, "lon": 106.7560,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ mới bàn giao, gần ngã tư Bình Thái, tiện di chuyển.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "BBQ"],
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400"
    },
    {
        "id": 21, "title": "Nhà trọ giá rẻ gần ĐH Bách Khoa",
        "type": "Phòng trọ", "price": 1.5, "area": 14,
        "address": "Dĩ An, Bình Dương (giáp TP Thủ Đức)",
        "lat": 10.8750, "lon": 106.7950,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Giá siêu rẻ, an ninh tốt, gần cổng sau ĐH Bách Khoa cơ sở 2.",
        "amenities": ["Wifi", "Giữ xe"],
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400"
    },
    {
        "id": 22, "title": "Căn hộ Thủ Thiêm Dragon 1PN",
        "type": "Chung cư", "price": 11.0, "area": 50,
        "address": "Mai Chí Thọ, Thủ Thiêm, Thủ Đức",
        "lat": 10.7850, "lon": 106.7560,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Vị trí đắc địa Thủ Thiêm, tiện ích đầy đủ, view thành phố.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "Sky bar"],
        "image": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=400"
    },
    {
        "id": 23, "title": "Phòng trọ gần Bệnh viện Thủ Đức",
        "type": "Phòng trọ", "price": 2.8, "area": 20,
        "address": "Lê Văn Chí, Linh Trung, Thủ Đức",
        "lat": 10.8560, "lon": 106.7770,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Gần BV Thủ Đức, chợ Linh Trung, trường học. An ninh tốt.",
        "amenities": ["Wifi", "Máy lạnh", "Bảo vệ"],
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400"
    },
    {
        "id": 24, "title": "Nhà nguyên căn Tam Phú",
        "type": "Nhà nguyên căn", "price": 7.0, "area": 55,
        "address": "Đường Tam Bình, Tam Phú, Thủ Đức",
        "lat": 10.8620, "lon": 106.7500,
        "bedrooms": 2, "bathrooms": 1,
        "description": "Nhà 1 trệt 1 lầu, khu dân cư yên tĩnh, gần chợ Tam Bình.",
        "amenities": ["Wifi", "Sân để xe"],
        "image": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400"
    },
    {
        "id": 25, "title": "Căn hộ Depot Metro Tham Lương",
        "type": "Chung cư", "price": 6.5, "area": 48,
        "address": "Depot Metro, Linh Đông, Thủ Đức",
        "lat": 10.8430, "lon": 106.7290,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Gần ga Metro, tiện di chuyển. Nội thất cơ bản.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi"],
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400"
    },
    {
        "id": 26, "title": "CHDV Thảo Điền Village",
        "type": "Căn hộ dịch vụ", "price": 15.0, "area": 55,
        "address": "Nguyễn Văn Hưởng, Thảo Điền, Thủ Đức",
        "lat": 10.8100, "lon": 106.7310,
        "bedrooms": 1, "bathrooms": 1,
        "description": "CHDV sang trọng khu Thảo Điền, phong cách Indochine, hồ bơi sân vườn.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Sân vườn", "Dọn phòng"],
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400"
    },
    {
        "id": 27, "title": "Phòng trọ mới xây gần Vincom Thủ Đức",
        "type": "Phòng trọ", "price": 3.2, "area": 24,
        "address": "Võ Văn Ngân, Bình Thọ, Thủ Đức",
        "lat": 10.8480, "lon": 106.7710,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Gần Vincom Thủ Đức, chợ đêm. Phòng mới xây, sạch sẽ.",
        "amenities": ["Wifi", "Máy lạnh", "Ban công"],
        "image": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=400"
    },
    {
        "id": 28, "title": "Căn hộ Him Lam Phú Đông 2PN",
        "type": "Chung cư", "price": 8.0, "area": 63,
        "address": "Him Lam Phú Đông, Thủ Đức",
        "lat": 10.8555, "lon": 106.7260,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ giá tốt, view thoáng, tiện ích đầy đủ. Gần Phạm Văn Đồng.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "Sân chơi"],
        "image": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=400"
    },
    {
        "id": 29, "title": "Nhà mặt tiền kinh doanh Dĩ An",
        "type": "Nhà nguyên căn", "price": 15.0, "area": 100,
        "address": "Quốc lộ 1K, Dĩ An (giáp Thủ Đức)",
        "lat": 10.8800, "lon": 106.7920,
        "bedrooms": 3, "bathrooms": 2,
        "description": "Nhà mặt tiền QL1K, 2 tầng, phù hợp kinh doanh cửa hàng.",
        "amenities": ["Wifi", "Mặt tiền", "Sân để xe", "Gác lửng"],
        "image": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"
    },
    {
        "id": 30, "title": "Căn hộ Safira Khang Điền 2PN",
        "type": "Chung cư", "price": 9.5, "area": 67,
        "address": "Võ Chí Công, Phú Hữu, Thủ Đức",
        "lat": 10.8170, "lon": 106.8100,
        "bedrooms": 2, "bathrooms": 2,
        "description": "Căn hộ mới, tiện ích đầy đủ. Gần cao tốc, cầu Phú Mỹ.",
        "amenities": ["Wifi", "Máy lạnh", "Hồ bơi", "Gym", "Công viên BBQ"],
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400"
    },
    {
        "id": 31, "title": "Phòng trọ cao cấp Trường Thọ",
        "type": "Phòng trọ", "price": 3.8, "area": 26,
        "address": "Đường Nguyễn Văn Bá, Trường Thọ, Thủ Đức",
        "lat": 10.8330, "lon": 106.7600,
        "bedrooms": 1, "bathrooms": 1,
        "description": "Phòng cao cấp, cách chân cầu Rạch Chiếc 500m. Yên tĩnh, mát mẻ.",
        "amenities": ["Wifi", "Máy lạnh", "Tủ lạnh"],
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400"
    },
    {
        "id": 32, "title": "Nhà nguyên căn An Phú 4PN",
        "type": "Nhà nguyên căn", "price": 25.0, "area": 140,
        "address": "An Phú, Thủ Đức",
        "lat": 10.7970, "lon": 106.7410,
        "bedrooms": 4, "bathrooms": 3,
        "description": "Biệt thự mini khu An Phú, full nội thất, sân vườn rộng.",
        "amenities": ["Wifi", "Máy lạnh", "Garage", "Sân vườn", "BBQ"],
        "image": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400"
    },
]


# ============================================================
# 2. SCORING ALGORITHMS
# ============================================================

# Trọng số từng loại POI khi tính amenity score
POI_WEIGHTS = {
    "hospital": 8,
    "school": 6,
    "marketplace": 7,
    "supermarket": 9,
    "bus_stop": 4,
    "restaurant": 5,
    "cafe": 4,
    "attraction": 6,
    "park": 7,
}

# Trọng số cho overall score
SCORE_WEIGHTS = {
    "amenity": 0.40,    # Tiện ích xung quanh
    "price": 0.30,      # Giá cả hợp lý
    "area": 0.15,       # Diện tích
    "variety": 0.15,    # Đa dạng tiện ích
}


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách giữa 2 điểm (mét)."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def filter_listings_in_bounds(
    listings: List[Dict],
    sw_lat: float, sw_lon: float,
    ne_lat: float, ne_lon: float,
    filters: Optional[Dict] = None,
) -> List[Dict]:
    """Lọc BĐS nằm trong bounds và theo filters."""
    result = []
    for listing in listings:
        lat, lon = listing["lat"], listing["lon"]
        if sw_lat <= lat <= ne_lat and sw_lon <= lon <= ne_lon:
            # Áp dụng filters
            if filters:
                if filters.get("type") and listing["type"] != filters["type"]:
                    continue
                if filters.get("max_price") and listing["price"] > filters["max_price"]:
                    continue
                if filters.get("min_price") and listing["price"] < filters["min_price"]:
                    continue
                if filters.get("min_area") and listing["area"] < filters["min_area"]:
                    continue
                if filters.get("bedrooms") and listing["bedrooms"] < filters["bedrooms"]:
                    continue
            result.append(listing.copy())
    return result


def calculate_amenity_score(lat: float, lon: float, pois: List[Dict], radius: float = 1000) -> Dict:
    """
    Tính điểm tiện ích cho 1 vị trí dựa trên POI xung quanh.
    Returns: {
        "total_score": float (0-10),
        "category_scores": {...},
        "poi_count": int,
        "nearby_pois": [...]
    }
    """
    category_counts = {
        "healthcare": 0,    # hospital
        "education": 0,     # school
        "shopping": 0,      # marketplace, supermarket
        "transport": 0,     # bus_stop
        "dining": 0,        # restaurant, cafe
        "leisure": 0,       # attraction, park
    }
    
    category_map = {
        "hospital": "healthcare",
        "school": "education",
        "marketplace": "shopping",
        "supermarket": "shopping",
        "bus_stop": "transport",
        "restaurant": "dining",
        "cafe": "dining",
        "attraction": "leisure",
        "park": "leisure",
    }
    
    nearby_pois = []
    total_weighted = 0
    
    for poi in pois:
        poi_lat = poi.get("lat") or poi.get("center", {}).get("lat", 0)
        poi_lon = poi.get("lon") or poi.get("center", {}).get("lon", 0)
        if not poi_lat or not poi_lon:
            continue
            
        dist = haversine(lat, lon, poi_lat, poi_lon)
        if dist > radius:
            continue
        
        tags = poi.get("tags", {})
        poi_type = (
            tags.get("amenity")
            or tags.get("shop")
            or tags.get("highway")
            or tags.get("tourism")
            or tags.get("leisure")
        )
        
        if poi_type and poi_type in POI_WEIGHTS:
            # Closer POIs score higher (decay by distance)
            distance_factor = max(0.2, 1.0 - (dist / radius))
            weight = POI_WEIGHTS.get(poi_type, 3)
            score_contribution = weight * distance_factor
            total_weighted += score_contribution
            
            category = category_map.get(poi_type, "other")
            category_counts[category] += 1
            
            name = tags.get("name", f"{poi_type} (Unnamed)")
            nearby_pois.append({
                "name": name,
                "type": poi_type,
                "distance": round(dist),
                "lat": poi_lat,
                "lon": poi_lon,
            })
    
    # Normalize total score to 0-10
    total_count = sum(category_counts.values())
    raw_score = min(total_weighted / 5, 10) if total_weighted > 0 else 0
    
    # Category scores (0-10 each)
    category_scores = {}
    for cat, count in category_counts.items():
        category_scores[cat] = min(count * 2.5, 10)
    
    # Variety bonus: more categories = higher score
    active_categories = sum(1 for v in category_counts.values() if v > 0)
    variety_bonus = (active_categories / len(category_counts)) * 2
    
    final_score = min(round(raw_score + variety_bonus, 1), 10)
    
    return {
        "total_score": final_score,
        "category_scores": category_scores,
        "poi_count": total_count,
        "nearby_pois": sorted(nearby_pois, key=lambda x: x["distance"])[:15],
    }


def calculate_price_score(price: float, listing_type: str) -> float:
    """
    Tính điểm giá cả (0-10). Giá càng hợp lý so với trung bình thị trường -> điểm càng cao.
    """
    # Bảng giá trung bình thị trường (triệu/tháng)
    avg_prices = {
        "Phòng trọ": 3.0,
        "Chung cư": 10.0,
        "Nhà nguyên căn": 12.0,
        "Căn hộ dịch vụ": 8.0,
    }
    avg = avg_prices.get(listing_type, 5.0)
    ratio = price / avg if avg > 0 else 1.0
    
    # Score: 10 nếu giá bằng TB, giảm dần nếu đắt hơn, tăng nhẹ nếu rẻ hơn
    if ratio <= 0.5:
        return 9.5  # Rất rẻ
    elif ratio <= 0.8:
        return 8.5
    elif ratio <= 1.0:
        return 7.5
    elif ratio <= 1.3:
        return 6.0
    elif ratio <= 1.8:
        return 4.5
    else:
        return 3.0


def calculate_area_score(area: float, listing_type: str) -> float:
    """
    Tính điểm diện tích (0-10). Diện tích rộng hơn trung bình -> điểm cao hơn.
    """
    avg_areas = {
        "Phòng trọ": 20.0,
        "Chung cư": 60.0,
        "Nhà nguyên căn": 80.0,
        "Căn hộ dịch vụ": 35.0,
    }
    avg = avg_areas.get(listing_type, 30.0)
    ratio = area / avg if avg > 0 else 1.0
    
    if ratio >= 1.5:
        return 9.0
    elif ratio >= 1.2:
        return 8.0
    elif ratio >= 1.0:
        return 7.0
    elif ratio >= 0.8:
        return 5.5
    else:
        return 4.0


def calculate_overall_score(
    amenity_score: float,
    price_score: float,
    area_score: float,
    variety_score: float,
) -> float:
    """Tính điểm tổng thể (0-10) — weighted average."""
    total = (
        amenity_score * SCORE_WEIGHTS["amenity"]
        + price_score * SCORE_WEIGHTS["price"]
        + area_score * SCORE_WEIGHTS["area"]
        + variety_score * SCORE_WEIGHTS["variety"]
    )
    return round(min(total, 10), 1)


def analyze_area(pois_raw: List[Dict], bounds: Dict) -> Dict:
    """
    Phân tích tổng quát khu vực dựa trên POIs.
    Returns thống kê để hiển thị radar chart.
    """
    center_lat = (bounds["sw_lat"] + bounds["ne_lat"]) / 2
    center_lon = (bounds["sw_lon"] + bounds["ne_lon"]) / 2
    
    result = calculate_amenity_score(center_lat, center_lon, pois_raw, radius=2000)
    
    return {
        "center": {"lat": center_lat, "lon": center_lon},
        "area_score": result["total_score"],
        "category_scores": result["category_scores"],
        "total_pois": result["poi_count"],
        "top_pois": result["nearby_pois"][:10],
    }
