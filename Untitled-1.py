import win32com.client
import os
from datetime import datetime
import time
import subprocess
import winreg

# ========================================
# CHỈ CẦN SỬA 3 DÒNG NÀY THÔI
# ========================================
cfg_path      = r"D:\WORK\CAPL-Test-Module\VF2_LHD.cfg"
report_dir    = r"D:\WORK\CAPL-Test-Module\Report"
sequence_name = "MainTestSequence"
# ========================================

class CANoeAuto:
    def __init__(self):
        self.app = None
        self.configuration = None

    def connect_to_canoe(self):
        print("Connecting to CANoe (smart + stable mode)...")

        # Bước 1: Thử kết nối với CANoe đang chạy (nếu có)
        for _ in range(10):  # Thử 10 lần (30 giây)
            try:
                self.app = win32com.client.Dispatch("CANoe.Application")
                self.configuration = self.app.Configuration
                print("CONNECTED TO EXISTING CANoe INSTANCE!")
                print(f"Config: {getattr(self.configuration, 'Name', 'Unknown')}")
                return True
            except:
                time.sleep(3)

        print("No running instance with COM → Starting new one in Normal mode...")

        # Bước 2: Tự động tìm CANoe.exe (hỗ trợ mọi phiên bản)
        possible_versions = ["19.0", "18.0", "17.0", "2024", "2023", "2022"]
        canoe_exe = None

        for ver in possible_versions:
            for root in ["", r"WOW6432Node"]:
                try:
                    path = fr"SOFTWARE\{root}\Vector\CANoe\{ver}" if root else fr"SOFTWARE\Vector\CANoe\{ver}"
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    install_dir = winreg.QueryValueEx(key, "InstallDir")[0]
                    exe = os.path.join(install_dir, "CANoe32.exe" if root else "CANoe.exe")
                    if os.path.exists(exe):
                        canoe_exe = exe
                        print(f"Found CANoe {ver}: {exe}")
                        break
                    winreg.CloseKey(key)
                except:
                    continue
            if canoe_exe:
                break

        if not canoe_exe:
            print("[ERROR] CANoe installation not found!")
            return False

        # Bước 3: Mở CANoe ở chế độ NORMAL (có COM)
        cmd = [canoe_exe, "/Normal", cfg_path]
        print(f"Launching: {' '.join(cmd)}")
        subprocess.Popen(cmd, shell=True)  # shell=True để tránh lỗi path

        # Bước 4: Chờ COM đăng ký (tối đa 90s)
        max_wait = 90
        waited = 0
        while waited < max_wait:
            try:
                time.sleep(3)
                self.app = win32com.client.Dispatch("CANoe.Application")
                self.configuration = self.app.Configuration
                print("CONNECTED SUCCESSFULLY AFTER LAUNCH!")
                print(f"Loaded: {getattr(self.configuration, 'Name', 'Unknown')}")
                return True
            except:
                waited += 3
                print(f"   Waiting for CANoe COM... ({waited}s/90s)")

        print("[ERROR] CANoe failed to register COM after 90s")
        return False

    # === CÁC HÀM KHÁC GIỮ NGUYÊN (đã test ổn định) ===
    def setup_test_report(self, report_settings=None):
        try:
            os.makedirs(report_dir, exist_ok=True)
            if report_settings is None:
                report_path = os.path.join(report_dir, f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                report_settings = {
                    'format': "HTML",
                    'output_path': report_path,
                    'generate_after_test': True,
                    'verbosity': 2
                }
            tc = self.configuration.TestSetup.TestConfigurations.Item(1)
            rp = tc.ReportConfiguration
            rp.Format = report_settings['format']
            rp.OutputPath = report_settings['output_path']
            rp.GenerateReportAfterTest = report_settings['generate_after_test']
            rp.Verbosity = report_settings['verbosity']
            print(f"Report configured: {report_settings['output_path']}")
            return True
        except Exception as e:
            print(f"[ERROR] Report config failed: {e}")
            return False

    def start_measurement(self):
        try:
            if not self.app.Measurement.Running:
                self.app.Measurement.Start()
                print("Measurement STARTED")
            return True
        except Exception as e:
            print(f"[ERROR] Start measurement failed: {e}")
            return False

    def stop_measurement(self):
        try:
            if self.app.Measurement.Running:
                self.app.Measurement.Stop()
                print("Measurement STOPPED")
        except Exception as e:
            print(f"[WARN] Stop measurement: {e}")

    def run_test_sequence(self, sequence_name, timeout=1800):
        try:
            env = self.configuration.TestSetup.TestEnvironments.Item(1)
            seq = None
            for i in range(1, env.TestSequences.Count + 1):
                s = env.TestSequences.Item(i)
                if s.Name.strip() == sequence_name.strip():
                    seq = s
                    break
            if not seq:
                print(f"[ERROR] Sequence not found: {sequence_name}")
                return False
            print(f"Running sequence: {sequence_name}")
            seq.Start()
            start = time.time()
            while seq.Running:
                if time.time() - start > timeout:
                    seq.Stop()
                    print("TIMEOUT!")
                    return False
                time.sleep(1)
            print("SEQUENCE COMPLETED")
            return True
        except Exception as e:
            print(f"[ERROR] Run sequence failed: {e}")
            return False

    def generate_statistics_report(self):
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            total = rs.Count
            passed = failed = inconclusive = 0
            total_time = 0.0
            details = []

            for i in range(1, total + 1):
                r = rs.Item(i)
                v = r.Verdict
                if v == 1: passed += 1
                elif v == 2: failed += 1
                elif v == 3: inconclusive += 1
                total_time += r.ExecutionTime
                details.append(f"{i:3}. {r.Name} -> {'PASS' if v==1 else 'FAIL' if v==2 else 'INC'} ({r.ExecutionTime:.2f}s)")

            file_path = os.path.join(report_dir, f"Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("="*70 + "\n")
                f.write("CANoe TEST RESULTS\n")
                f.write("="*70 + "\n\n")
                f.write("\n".join(details))
                f.write("\n\n" + "="*70 + "\n")
                f.write(f"TOTAL: {total} | PASS: {passed} | FAIL: {failed} | INC: {inconclusive}\n")
                f.write(f"PASS RATE: {passed/total*100:5.1f}% | TIME: {total_time:.1f}s\n")
            print(f"Summary saved: {file_path}")
        except Exception as e:
            print(f"[ERROR] Generate report failed: {e}")

# ====================== MAIN ======================
def main():
    canoe = CANoeAuto()

    if not canoe.connect_to_canoe():
        print("CANNOT CONNECT TO CANoe → STOP")
        return

    if not canoe.setup_test_report():
        return

    if not canoe.start_measurement():
        return

    try:
        if canoe.run_test_sequence(sequence_name, timeout=1800):
            canoe.generate_statistics_report()
    finally:
        canoe.stop_measurement()
        print("ALL DONE! CANoe can stay open.")

if __name__ == "__main__":
    main()