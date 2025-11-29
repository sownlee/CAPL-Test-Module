import win32com.client
import os
from datetime import datetime
import time

# ========================================
# CHỈ CẦN SỬA 3 DÒNG NÀY THÔI
# ========================================
cfg_path      = r"D:\WORK\CAPL-Test-Module\VF2_LHD.cfg"          # File config của bạn
report_dir    = r"D:\WORK\CAPL-Test-Module\Report"               # Thư mục lưu báo cáo
sequence_name = "MainTestSequence"                               # Tên sequence cần chạy
# ========================================

class CANoeAuto:
    def __init__(self):
        self.app = None
        self.configuration = None  # Để đồng bộ tên biến với CSDN

    # ===================================================================
    # 1. Connection and Basic Control
    # ===================================================================
    def connect_to_canoe(self):
        """Connect to CANoe and load configuration (smart mode - reuse if running)"""
        print("Connecting to CANoe (smart mode)...")
        max_wait = 90
        waited = 0
        opened_cfg = False

        while waited < max_wait:
            try:
                self.app = win32com.client.Dispatch("CANoe.Application")
                self.configuration = self.app.Configuration
                cfg_name = "Unknown"
                try:
                    cfg_name = self.configuration.Name if self.configuration.Name else "No config loaded"
                except:
                    pass
                print("CONNECTED TO CANoe SUCCESSFULLY!")
                print(f"Current configuration: {cfg_name}")
                if opened_cfg:
                    print("   → Configuration loaded successfully")
                else:
                    print("   → Reused running instance")
                return True
            except:
                if waited == 0 and os.path.exists(cfg_path):
                    print("Opening configuration file...")
                    os.startfile(cfg_path)
                    opened_cfg = True
                    print("Waiting for CANoe COM initialization...")
                time.sleep(3)
                waited += 3
                print(f"   Still waiting... ({waited}s/90s)")

        print("[ERROR] CANoe connection failed after 90s")
        return False

    # ===================================================================
    # 2. Test Report Configuration
    # ===================================================================
    def setup_test_report(self, report_settings=None):
        """
        Configure test report settings (giống CSDN 100%)
        Nếu không truyền settings → tự động tạo HTML report với timestamp
        """
        try:
            # Tạo thư mục nếu chưa có
            os.makedirs(report_dir, exist_ok=True)
            # Nếu không truyền settings → dùng cách của bạn (tốt hơn CSDN)
            if report_settings is None:
                report_path = os.path.join(
                    report_dir,
                    f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                report_settings = {
                    'format': "HTML",
                    'output_path': report_path,
                    'generate_after_test': True,
                    'verbosity': 2
                }
            # Áp dụng cấu hình
            tc = self.configuration.TestSetup.TestConfigurations.Item(1)
            rp = tc.ReportConfiguration
            if 'format' in report_settings:
                rp.Format = report_settings['format']
            if 'output_path' in report_settings:
                rp.OutputPath = report_settings['output_path']
            if 'generate_after_test' in report_settings:
                rp.GenerateReportAfterTest = report_settings['generate_after_test']
            if 'verbosity' in report_settings:
                rp.Verbosity = report_settings['verbosity']
            print("Test report configuration completed")
            print(f"   → {report_settings['output_path']}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to configure test report: {e}")
            return False

    # ===================================================================
    # 3. Measurement Control
    # ===================================================================
    def start_measurement(self):
        """Start CANoe measurement"""
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
        """Stop CANoe measurement (giữ nguyên logic của bạn)"""
        try:
            if self.app.Measurement.Running:  # Sửa self.can_app → self.app (lỗi typo)
                self.app.Measurement.Stop()
                print("Measurement STOPPED")
        except Exception as e:
            print(f"[WARN] Measurement already stopped or error: {e}")

    # ===================================================================
    # 4. Test Execution
    # ===================================================================
    def run_test_sequence(self, sequence_name, timeout=1800):
        """Run specified test sequence"""
        try:
            env = self.configuration.TestSetup.TestEnvironments.Item(1)
            seq = None
            for i in range(1, env.TestSequences.Count + 1):
                s = env.TestSequences.Item(i)
                if s.Name.strip() == sequence_name.strip():
                    seq = s
                    break
            if not seq:
                print(f"[ERROR] Test sequence not found: {sequence_name}")
                return False

            print(f"Executing test sequence: {sequence_name}")
            seq.Start()

            start_time = time.time()
            while seq.Running:
                if time.time() - start_time > timeout:
                    seq.Stop()
                    print(f"TIMEOUT after {timeout}s - Sequence stopped!")
                    return False
                time.sleep(1)

            print(f"SEQUENCE COMPLETED: {sequence_name}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to execute test sequence: {e}")
            return False

    # ===================================================================
    # 5. Test Result Statistics and Analysis (giống CSDN 100%)
    # ===================================================================
    def _verdict_to_string(self, verdict):
        """Convert verdict code to string (helper from CSDN)"""
        mapping = {0: "None", 1: "PASS", 2: "FAIL", 3: "INCONCLUSIVE"}
        return mapping.get(verdict, "UNKNOWN")

    def get_test_results_summary(self):
        """Get test result summary (from CSDN)"""
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            summary = {
                'total_tests': rs.Count,
                'passed': 0, 'failed': 0, 'inconclusive': 0,
                'total_execution_time': 0.0
            }
            for i in range(1, rs.Count + 1):
                r = rs.Item(i)
                v = r.Verdict
                if v == 1: summary['passed'] += 1
                elif v == 2: summary['failed'] += 1
                elif v == 3: summary['inconclusive'] += 1
                summary['total_execution_time'] += r.ExecutionTime
            return summary
        except Exception as e:
            print(f"[ERROR] Failed to get test summary: {e}")
            return None

    def get_detailed_test_results(self):
        """Get detailed test results (from CSDN)"""
        try:
            ts = self.app.GetTestService()
            rs = ts.Results
            details = []
            for i in range(1, rs.Count + 1):
                r = rs.Item(i)
                details.append({
                    'no': i,
                    'name': r.Name,
                    'verdict': self._verdict_to_string(r.Verdict),
                    'execution_time': r.ExecutionTime,
                    'error_message': getattr(r, 'ErrorMessage', '') if hasattr(r, 'ErrorMessage') else ''
                })
            return details
        except Exception as e:
            print(f"[ERROR] Failed to get detailed results: {e}")
            return None

    def generate_statistics_report(self, output_file=None):
        """Generate statistics report (updated from your code + CSDN)"""
        try:
            summary = self.get_test_results_summary()
            details = self.get_detailed_test_results()
            if not summary or not details:
                print("[ERROR] Cannot generate report - missing data")
                return False

            if output_file is None:
                output_file = os.path.join(report_dir, f"Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

            lines = []
            lines.append("=" * 70)
            lines.append("CANoe TEST RESULTS SUMMARY")
            lines.append("=" * 70)
            lines.append("")

            lines.append("TEST SUMMARY:")
            lines.append(f"  Total tests       : {summary['total_tests']}")
            lines.append(f"  Passed            : {summary['passed']}")
            lines.append(f"  Failed            : {summary['failed']}")
            lines.append(f"  Inconclusive      : {summary['inconclusive']}")
            lines.append(f"  Total time        : {summary['total_execution_time']:.1f}s")
            if summary['total_tests'] > 0:
                rate = summary['passed'] / summary['total_tests'] * 100
                lines.append(f"  PASS RATE         : {rate:5.1f}%")
            lines.append("")

            lines.append("=" * 70)
            lines.append("DETAILED RESULTS:")
            lines.append("=" * 70)
            for d in details:
                lines.append(f"{d['no']:3}. {d['name']}")
                lines.append(f"     → {d['verdict']} ({d['execution_time']:.2f}s)")
                if d['error_message']:
                    lines.append(f"     Error: {d['error_message']}")

            content = "\n".join(lines)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Text summary report saved: {output_file}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to generate statistics report: {e}")
            return False
    # ===================================================================
    # 6. CAPL Integration - Python gọi CAPL (MỚI THÊM)
    # ===================================================================
    def capl_call_function(self, function_name, *args):
        """Gọi hàm CAPL từ Python (ví dụ: StartMyTest(), SendFrame(0x123))"""
        try:
            capl = self.app.CAPL
            if not args:
                capl.Call(function_name)
            else:
                capl.Call(function_name, *args)
            print(f"CAPL function called: {function_name}{args}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to call CAPL function {function_name}: {e}")
            return False

    def capl_set_variable(self, variable_path, value):
        """Set giá trị biến CAPL từ Python (ví dụ: ns::TestMode = 1)"""
        try:
            self.app.CAPL.SetVariable(variable_path, value)
            print(f"CAPL variable set: {variable_path} = {value}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to set CAPL variable {variable_path}: {e}")
            return False

    def capl_get_variable(self, variable_path):
        """Lấy giá trị biến CAPL về Python"""
        try:
            value = self.app.CAPL.GetVariable(variable_path)
            print(f"CAPL variable read: {variable_path} = {value}")
            return value
        except Exception as e:
            print(f"[ERROR] Failed to get CAPL variable {variable_path}: {e}")
            return None

    def capl_compile_and_load(self, capl_file_path):
        """Compile và load file .can từ Python"""
        try:
            capl = self.app.CAPL
            capl.CompileAndLoad(capl_file_path)
            print(f"CAPL script loaded: {capl_file_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load CAPL script {capl_file_path}: {e}")
            return False

    def capl_send_message(self, can_id, dlc, data_bytes):
        """Gửi CAN message từ Python qua CAPL (rất tiện cho restbus)"""
        try:
            # Dùng hàm CAPL có sẵn: SendCANMessage(id, dlc, data...)
            self.capl_call_function("SendCANMessage", can_id, dlc, *data_bytes)
            return True
        except:
            return False
# ====================== MAIN ======================
def main():
    canoe = CANoeAuto()

    if not canoe.connect_to_canoe():
        return
    # Load CAPL script (nếu cần)
    capl_path = r"D:\WORK\CAPL-Test-Module\MyCAPL.can"
    if os.path.exists(capl_path):
        canoe.capl_compile_and_load(capl_path)
    if not canoe.setup_test_report():  # Đổi tên gọi để đồng bộ
        return

    if not canoe.start_measurement():
        return

    try:
        if canoe.run_test_sequence(sequence_name, timeout=1800):
            canoe.generate_statistics_report()
    finally:
        canoe.stop_measurement()
        print("ALL DONE! You can now close CANoe or leave it open.")

if __name__ == "__main__":
    main()