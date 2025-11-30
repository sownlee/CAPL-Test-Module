import win32com.client
import os
from datetime import datetime
import time
import subprocess
import winreg

# ========================================
# CHỈ CẦN SỬA 3 DÒNG NÀY THÔI
# ========================================
cfg_path      = r"D:\Config\VF2_LHD.cfg"
report_dir    = r"D:\WORK\CAPL-Test-Module\Report"
sequence_name = "MainTestSequence"
# ========================================

class CANoeAuto:
    def __init__(self):
        self.app = None
        self.configuration = None

    def connect_to_canoe(self):
        print("Connecting to CANoe...")

        # Bước 1: Thử kết nối với CANoe đang chạy (nếu có COM)
        for _ in range(10):
            try:
                self.app = win32com.client.Dispatch("CANoe.Application")
                self.configuration = self.app.Configuration
                print("=> CONNECTED TO EXISTING CANoe INSTANCE!")
                print(f"   Config: {getattr(self.configuration, 'Name', 'Unknown')}")
                return True
            except:
                time.sleep(3)

        print("=> No COM found. Starting CANoe in Normal mode...")

        # Bước 2: Tự động tìm CANoe.exe (hỗ trợ mọi phiên bản)
        possible_versions = ["19.0", "18.0", "17.0", "2024", "2023", "2022"]
        canoe_exe = None

        for ver in possible_versions:
            for root in ["", "WOW6432Node"]:
                try:
                    path = f"SOFTWARE\\{root}\\Vector\\CANoe\\{ver}" if root else f"SOFTWARE\\Vector\\CANoe\\{ver}"
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    install_dir = winreg.QueryValueEx(key, "InstallDir")[0]
                    exe_name = "CANoe32.exe" if root else "CANoe.exe"
                    exe_path = os.path.join(install_dir, exe_name)
                    if os.path.exists(exe_path):
                        canoe_exe = exe_path
                        print(f"=> Found CANoe {ver}: {exe_path}")
                        winreg.CloseKey(key)
                        break
                    winreg.CloseKey(key)
                except:
                    continue
            if canoe_exe:
                break

        if not canoe_exe:
            print("[ERROR] CANoe installation not found in registry!")
            return False

        # Bước 3: Mở CANoe ở chế độ NORMAL (có COM)
        cmd = [canoe_exe, "/Normal", cfg_path]
        print(f"=> Launching: {' '.join(cmd)}")
        subprocess.Popen(cmd, shell=True)

        # Bước 4: Chờ COM đăng ký
        max_wait = 90
        waited = 0
        while waited < max_wait:
            try:
                time.sleep(3)
                self.app = win32com.client.Dispatch("CANoe.Application")
                self.configuration = self.app.Configuration
                print("=> CONNECTED SUCCESSFULLY AFTER LAUNCH!")
                print(f"   Config loaded: {getattr(self.configuration, 'Name', 'Unknown')}")
                return True
            except:
                waited += 3
                print(f"   Waiting for COM registration... ({waited}s/90s)")

        print("[ERROR] CANoe failed to start or register COM after 90s")
        return False

    def setup_test_report(self):
        try:
            os.makedirs(report_dir, exist_ok=True)
            report_path = os.path.join(report_dir, f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            tc = self.configuration.TestSetup.TestConfigurations.Item(1)
            rp = tc.ReportConfiguration
            rp.Format = "HTML"
            rp.OutputPath = report_path
            rp.GenerateReportAfterTest = True
            rp.Verbosity = 2
            print(f"=> Report will be saved: {report_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Report config failed: {e}")
            return False

    def start_measurement(self):
        try:
            if not self.app.Measurement.Running:
                self.app.Measurement.Start()
                print("=> Measurement STARTED")
            return True
        except Exception as e:
            print(f"[ERROR] Start failed: {e}")
            return False

    def stop_measurement(self):
        try:
            if self.app.Measurement.Running:
                self.app.Measurement.Stop()
                print("=> Measurement STOPPED")
        except:
            pass

    def run_test_sequence(self, seq_name, timeout=1800):
        try:
            env = self.configuration.TestSetup.TestEnvironments.Item(1)
            seq = None
            for i in range(1, env.TestSequences.Count + 1):
                s = env.TestSequences.Item(i)
                if s.Name.strip() == seq_name.strip():
                    seq = s
                    break
            if not seq:
                print(f"[ERROR] Sequence not found: {seq_name}")
                return False

            print(f"=> Running sequence: {seq_name}")
            seq.Start()
            start = time.time()
            while seq.Running:
                if time.time() - start > timeout:
                    seq.Stop()
                    print("=> TIMEOUT!")
                    return False
                time.sleep(1)
            print("=> SEQUENCE COMPLETED")
            return True
        except Exception as e:
            print(f"[ERROR] Run sequence failed: {e}")
            return False

    def generate_statistics_report(self):
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            total = rs.Count
            passed = failed = inc = 0
            total_time = 0.0
            lines = []

            for i in range(1, total + 1):
                r = rs.Item(i)
                v = r.Verdict
                if v == 1: passed += 1
                elif v == 2: failed += 1
                else: inc += 1
                total_time += r.ExecutionTime
                status = "PASS" if v == 1 else "FAIL" if v == 2 else "INC"
                lines.append(f"{i:3}. {r.Name} -> {status} ({r.ExecutionTime:.2f}s)")

            file_path = os.path.join(report_dir, f"Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("="*70 + "\n")
                f.write("CANOE TEST RESULTS SUMMARY\n")
                f.write("="*70 + "\n\n")
                f.write("\n".join(lines) + "\n")
                f.write("\n" + "="*70 + "\n")
                f.write(f"TOTAL: {total} | PASS: {passed} | FAIL: {failed} | INC: {inc}\n")
                f.write(f"PASS RATE: {passed/total*100:5.1f}% | TIME: {total_time:.1f}s\n")
            print(f"=> Summary saved: {file_path}")
        except Exception as e:
            print(f"[ERROR] Generate report failed: {e}")

# ====================== MAIN ======================
def main():
    canoe = CANoeAuto()

    if not canoe.connect_to_canoe():
        print("CANNOT CONNECT TO CANOE -> STOP")
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