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

    # 1. Connection and Basic Control
    def connect_to_canoe(self):
        if not os.path.exists(cfg_path):
            print("[ERROR] Configuration file not found!")
            return False
        
        print("Opening CANoe with .cfg file...")
        os.startfile(cfg_path)           # Cách của bạn - SIÊU ỔN ĐỊNH
        print("Waiting for CANoe to fully start (60s)...")
        time.sleep(60)                    # CANoe 17/18 cần 12-18s
        
        try:
            self.app = win32com.client.Dispatch("CANoe.Application")
            ten_cfg = self.app.Configuration.Name
            print("CONNECTED TO CANoe SUCCESSFULLY!")
            print(f"Loaded configuration: {ten_cfg}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            print("Tip: CANoe may still be loading -> increase sleep time to 20s")
            return False

    # 2. Test Report Configuration
    def configure_test_report(self):
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

            print(f"HTML report will be saved to:")
            print(f"   {duong_dan}")
            return True
        except Exception as e:
            print(f"[ERROR] Report configuration failed: {e}")
            return False
    def configure_html_report(self, output_dir, report_name=None):
        """Configure HTML format test report"""
        if report_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"TestReport_{timestamp}.html"
            
        report_path = os.path.join(output_dir, report_name)
        
        report_settings = {
            'format': "HTML",
            'output_path': report_path,
            'generate_after_test': True,
            'verbosity': 2  # Detailed report
        }
        
        return self.setup_test_report(report_settings)
    # 3. Measurement Control - Start
    def start_measurement(self):
        try:
            if self.app.Measurement.Running:
                print("Measurement is already running")
            else:
                self.app.Measurement.Start()
                print("Measurement STARTED")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start measurement: {e}")
            return False
    def stop_measurement(self):
        """Stop measurement"""
        try:
            if self.can_app.Measurement.Running:
                self.can_app.Measurement.Stop()
                print("Measurement stopped")
            return True
        except Exception as e:
            print(f"Failed to stop measurement: {e}")
            return False
    # 4. Test Execution - Run Sequence
    def run_test_sequence(self, ten_seq, timeout=1200):
        try:
            env = self.app.Configuration.TestSetup.TestEnvironments.Item(1)
            seq = None
            for i in range(1, env.TestSequences.Count + 1):
                s = env.TestSequences.Item(i)
                if s.Name.strip() == ten_seq.strip():
                    seq = s
                    break
            if not seq:
                print(f"[ERROR] Test sequence not found: {ten_seq}")
                return False

            print(f"Executing test sequence: {ten_seq}")
            seq.Start()
            start = time.time()
            while seq.Running:
                if time.time() - start > timeout:
                    seq.Stop()
                    print("TIMEOUT - Sequence stopped!")
                    return False
                time.sleep(1)
            print(f"SEQUENCE COMPLETED: {ten_seq}")
            return True
        except Exception as e:
            print(f"[ERROR] Sequence execution failed: {e}")
            return False

    # 5. Test Result Statistics and Analysis
    def generate_statistics_report(self):
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            tong = rs.Count
            ok = fail = inc = 0
            tong_tg = 0.0

            file_txt = os.path.join(report_dir, f"Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(file_txt, "w", encoding="utf-8") as f:
                f.write("="*70 + "\n")
                f.write("CANoe TEST RESULTS SUMMARY\n")
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
                f.write(f"TOTAL TC: {tong} | PASS: {ok} | FAIL: {fail} | INCONCLUSIVE: {inc}\n")
                f.write(f"PASS RATE: {ok/tong*100:5.1f}% | Total time: {tong_tg:.1f}s\n")
            print(f"Text summary report saved: {file_txt}")
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {e}")

    # 6. Measurement Control - Stop (dùng trong finally)
    def stop_measurement(self):
        try:
            if self.app.Measurement.Running:
                self.app.Measurement.Stop()
                print("Measurement STOPPED")
        except:
            pass

# ====================== MAIN ======================
def main():
    can = CANoeAuto()

    if not can.connect_to_canoe():
        return

    if not can.configure_test_report():
        return

    if not can.start_measurement():
        return

    try:
        if can.run_test_sequence(sequence_name, timeout=1800):
            can.generate_statistics_report()
    finally:
        can.stop_measurement()
        print("ALL DONE! You can now close CANoe or leave it open.")

if __name__ == "__main__":
    main()