import win32com.client
import os
from datetime import datetime
import time

# ========================================
# CHỈ CẦN SỬA 3 DÒNG NÀY THÔI
# ========================================
cfg_path      = r"D:\Config\VF3_LHD.cfg"          # File config của bạn
report_dir    = r"D:\VF3\Report"                  # Thư mục lưu báo cáo
sequence_name = "MainTestSequence"                # Tên sequence cần chạy
# ========================================

class CANoeAuto:
    def __init__(self):
        self.app = None

    def mo_canoe(self):
        if not os.path.exists(cfg_path):
            print("Khong tim thay file config!")
            return False
        
        print("Dang mo CANoe bang file .cfg...")
        os.startfile(cfg_path)           # Cách của bạn - SIÊU ỔN ĐỊNH
        print("Dang cho CANoe khoi dong (15s)...")
        time.sleep(15)                    # CANoe 17/18 cần 12-18s
        
        try:
            self.app = win32com.client.Dispatch("CANoe.Application")
            ten_cfg = self.app.Configuration.Name
            print(f"DA KET NOI CANOE THANH CONG!")
            print(f"Config dang chay: {ten_cfg}")
            return True
        except Exception as e:
            print(f"Ket noi that bai: {e}")
            print("Loi nay thuong do CANoe chua load xong -> tang time.sleep len 20")
            return False

    def cau_hinh_report(self):
        try:
            os.makedirs(report_dir, exist_ok=True)
            ten_file = f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            duong_dan = os.path.join(report_dir, ten_file)

            tc = self.app.Configuration.TestSetup.TestConfigurations.Item(1)
            rp = tc.ReportConfiguration
            rp.Format = "HTML"
            rp.OutputPath = duong_dan
            rp.GenerateReportAfterTest = True
            rp.Verbosity = 2

            print(f"Report HTML se luu tai:")
            print(f"   {duong_dan}")
            return True
        except Exception as e:
            print(f"Loi cau hinh report: {e}")
            return False

    def bat_measurement(self):
        try:
            if self.app.Measurement.Running:
                print("Measurement da chay san")
            else:
                self.app.Measurement.Start()
                print("Da BAT Measurement")
            return True
        except Exception as e:
            print(f"Loi bat measurement: {e}")
            return False

    def chay_sequence(self, ten_seq, timeout=1200):
        try:
            env = self.app.Configuration.TestSetup.TestEnvironments.Item(1)
            seq = None
            for i in range(1, env.TestSequences.Count + 1):
                s = env.TestSequences.Item(i)
                if s.Name.strip() == ten_seq.strip():
                    seq = s
                    break
            if not seq:
                print(f"Khong tim thay sequence: {ten_seq}")
                return False

            print(f"Dang chay sequence: {ten_seq}")
            seq.Start()
            start = time.time()
            while seq.Running:
                if time.time() - start > timeout:
                    seq.Stop()
                    print("HET THOI GIAN - Da dung sequence!")
                    return False
                time.sleep(1)
            print(f"SEQUENCE HOAN TAT: {ten_seq}")
            return True
        except Exception as e:
            print(f"Loi chay sequence: {e}")
            return False

    def tao_summary_txt(self):
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            tong = rs.Count
            ok = fail = inc = 0
            tong_tg = 0

            file_txt = os.path.join(report_dir, f"Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(file_txt, "w", encoding="utf-8") as f:
                f.write("="*70 + "\n")
                f.write("KET QUA TEST CANOE\n")
                f.write("="*70 + "\n\n")
                for i in range(1, tong + 1):
                    r = rs.Item(i)
                    v = r.Verdict
                    if v == 1: ok += 1
                    elif v == 2: fail += 1
                    elif v == 3: inc += 1
                    tong_tg += r.ExecutionTime
                    status = "PASS" if v == 1 else "FAIL" if v == 2 else "INCONCLUSIVE"
                    f.write(f"{i:3}. {r.Name} -> {status} ({r.ExecutionTime:.2f}s)\n")
                f.write("\n" + "="*70 + "\n")
                f.write(f"TONG TC: {tong} | PASS: {ok} | FAIL: {fail} | INCONCLUSIVE: {inc}\n")
                f.write(f"TY LE PASS: {ok/tong*100:5.1f}% | Tong thoi gian: {tong_tg:.1f}s\n")
            print(f"Da luu bao cao text: {file_txt}")
        except Exception as e:
            print(f"Loi tao bao cao: {e}")

# ====================== CHAY CHINH ======================
def main():
    can = CANoeAuto()

    if not can.mo_canoe():
        return

    if not can.cau_hinh_report():
        return

    if not can.bat_measurement():
        return

    try:
        if can.chay_sequence(sequence_name, timeout=1800):
            can.tao_summary_txt()
    finally:
        try:
            can.app.Measurement.Stop()
            print("Da dung measurement")
        except:
            pass
        print("HOAN TAT! Ban co the dong CANoe hoac de do")

if __name__ == "__main__":
    main()