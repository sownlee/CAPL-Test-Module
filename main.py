import win32com.client
import pythoncom
import os
from datetime import datetime

#==========
cfg_path = r"D:\Config\VF3_LHD.cfg"

# Bước 1: Mở file .cfg → CANoe sẽ tự khởi động và load config luôn
print("CANoe...")
os.startfile(cfg_path)

# Bước 2: (Tùy chọn) Đợi CANoe khởi động rồi connect bằng Python
time.sleep(8)  # CANoe cần ~5-10s để load config nặng

# Connect để điều khiển tiếp
app = win32com.client.Dispatch("CANoe.Application")
print("CANoe đã sẵn sàng!")
print("Config đang chạy:", app.Configuration.Name)