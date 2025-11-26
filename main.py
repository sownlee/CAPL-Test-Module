import win32com.client
import os
import time
from datetime import datetime

# ====================== CẤU HÌNH ======================
cfg_path = r"D:\Config\VF3_LHD.cfg"          # Đường dẫn config của bạn
wait_time = 10                               # Thời gian chờ CANoe load config (giây)

# ====================== HÀM CHÍNH ======================
def main():
    # Bước 1: Mở file .cfg → CANoe tự khởi động và load config
    if not os.path.exists(cfg_path):
        print(f"Error: Configuration file not found!\n   {cfg_path}")
        return
    
    print(f"Opening configuration file...\n   {cfg_path}")
    os.startfile(cfg_path)
    
    # Bước 2: Đợi CANoe khởi động hoàn toàn
    print(f"Waiting {wait_time} seconds for CANoe to start and load configuration...")
    time.sleep(wait_time)
    
    # Bước 3: Kết nối COM với CANoe
    app = None
    for prog_id in ["CANoe64.Application", "CANoe.Application"]:  # Ưu tiên 64-bit
        try:
            app = win32com.client.Dispatch(prog_id)
            print(f"Successfully connected to CANoe ({prog_id})")
            break
        except Exception as e:
            continue
    
    if not app:
        print("Failed to connect to CANoe!")
        print("   Please run CANoe as Administrator at least once.")
        print("   Or check if CANoe version matches Python bitness (32/64-bit).")
        return
    
    # Bước 4: Kiểm tra config đã load thành công chưa
    try:
        config_name = app.Configuration.Name
        print(f"Configuration loaded successfully: {config_name}")
        print(f"CANoe Version: {app.Version}")
        print("CANoe is ready for automation!")
        
        # Giữ cửa sổ mở để bạn xem kết quả
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print("Configuration not fully loaded yet or error occurred:")
        print(f"   {e}")
        print("   Try increasing wait_time (currently {wait_time}s)")

# ====================== CHẠY CHƯƠNG TRÌNH ======================
if __name__ == "__main__":
    main()