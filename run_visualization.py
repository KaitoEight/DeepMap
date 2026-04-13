#!/usr/bin/env python3
"""
Script helper để chạy DeepMap Visualization
Giúp khởi động backend và mở dashboard tự động
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def start_backend():
    """Khởi động backend server"""
    print("🚀 Khởi động Backend Server...")
    print("=" * 50)
    
    try:
        # Kiểm tra requirements
        try:
            import fastapi
            import uvicorn
        except ImportError:
            print("❌ Thiếu dependencies!")
            print("Cài đặt: pip install fastapi uvicorn requests")
            return False
        
        # Chạy uvicorn
        print("Backend sẽ chạy tại: http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        print("=" * 50)
        
        # Chạy backend trong subprocess
        cmd = [sys.executable, "-m", "uvicorn", "backend:app", "--reload", "--port", "8000"]
        subprocess.Popen(cmd)
        
        # Chờ backend khởi động
        time.sleep(3)
        print("✅ Backend đang chạy!")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi động backend: {e}")
        return False

def start_server():
    """Khởi động HTTP server cho HTML"""
    print("\n📊 Khởi động HTTP Server cho Dashboard...")
    print("=" * 50)
    
    try:
        print("Dashboard sẽ chạy tại: http://localhost:8080")
        print("=" * 50)
        
        # Chạy HTTP server
        cmd = [sys.executable, "-m", "http.server", "8080"]
        subprocess.Popen(cmd, cwd=Path(__file__).parent)
        
        time.sleep(2)
        print("✅ HTTP Server đang chạy!")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi động HTTP server: {e}")
        return False

def open_dashboard():
    """Mở dashboard trong trình duyệt"""
    print("\n🌐 Mở Dashboard...")
    time.sleep(2)
    
    url = "http://localhost:8080/index.html"
    print(f"Mở: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Dashboard đã mở!")
    except:
        print(f"⚠️  Mở trình duyệt thất bại, vui lòng vào: {url}")

def print_info():
    """Hiển thị thông tin"""
    print("\n" + "=" * 50)
    print("🗺️  DeepMap - Visualization Dashboard")
    print("=" * 50)
    print("""
Các dịch vụ sẽ chạy tại:
  • Backend API: http://localhost:8000
  • API Docs: http://localhost:8000/docs
  • Dashboard: http://localhost:8080/index.html

Hướng dẫn sử dụng:
  1. Nhập Vĩ độ & Kinh độ
  2. Chọn Bán kính tìm kiếm
  3. Nhấn "🔍 Tìm kiếm"
  4. Xem kết quả trên bản đồ & biểu đồ

Loại Địa điểm & Hot Score:
  • Restaurant, Cafe, Attraction: 8.0
  • Park, Marketplace: 7.0
  • Supermarket: 6.0
  • Hospital, School, Bus Stop: 4.0

Nhấn Ctrl+C để dừng.
""")
    print("=" * 50)

if __name__ == "__main__":
    print_info()
    
    # Khởi động backend
    if not start_backend():
        print("❌ Không thể khởi động backend!")
        sys.exit(1)
    
    # Khởi động HTTP server
    if not start_server():
        print("❌ Không thể khởi động HTTP server!")
        sys.exit(1)
    
    # Mở dashboard
    open_dashboard()
    
    print("\n💡 Tips:")
    print("  • Mở lại Dashboard: http://localhost:8080/index.html")
    print("  • Xem API Docs: http://localhost:8000/docs")
    print("  • Dùng Ctrl+C để dừng services")
    print("\n✅ Tất cả services đang chạy! Hãy thử tìm kiếm địa điểm.")
    print("=" * 50)
    
    try:
        # Giữ process chạy
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Đã dừng services.")
        sys.exit(0)
