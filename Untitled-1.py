import win32com.client
import pythoncom
import os
from datetime import datetime

class CANoeReportManager:
    def __init__(self):
        self.can_app = None
        self.measurement = None
        self.configuration = None
        
    def connect_to_canoe(self):
        """Connect to CANoe application"""
        try:
            self.can_app = win32com.client.Dispatch("CANoe.Application")
            print("Successfully connected to CANoe")
            return True
        except Exception as e:
            print(f"Failed to connect to CANoe: {e}")
            return False
    
    def open_configuration(self, cfg_path):
        """Open CANoe configuration file"""
        if not self.can_app:
            print("Please connect to CANoe first")
            return False
            
        try:
            if not os.path.exists(cfg_path):
                print(f"Configuration file does not exist: {cfg_path}")
                return False
                
            self.can_app.Configuration.Open(cfg_path)
            self.configuration = self.can_app.Configuration
            print(f"Successfully opened configuration file: {cfg_path}")
            return True
        except Exception as e:
            print(f"Failed to open configuration file: {e}")
            return False
def setup_test_report(self, report_settings):
        """
        Configure test report settings
        
        Args:
            report_settings: Dictionary containing report configuration parameters
        """
        try:
            # Get test configuration
            test_configuration = self.configuration.TestSetup.TestConfigurations.Item(1)
            
            # Configure test report
            test_report = test_configuration.ReportConfiguration
            
            # Set report format
            if 'format' in report_settings:
                test_report.Format = report_settings['format']  # e.g., "HTML", "XML"
            
            # Set report path
            if 'output_path' in report_settings:
                test_report.OutputPath = report_settings['output_path']
            
            # Set whether to automatically generate report after test
            if 'generate_after_test' in report_settings:
                test_report.GenerateReportAfterTest = report_settings['generate_after_test']
            
            # Set report verbosity level
            if 'verbosity' in report_settings:
                test_report.Verbosity = report_settings['verbosity']  # e.g., 0-minimal, 1-standard, 2-detailed
            
            print("Test report configuration completed")
            return True
            
        except Exception as e:
            print(f"Failed to configure test report: {e}")
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
def start_measurement(self):
        """Start measurement"""
        try:
            if self.can_app.Measurement.Running:
                print("Measurement is already running")
                return True
                
            self.can_app.Measurement.Start()
            print("Measurement started")
            return True
        except Exception as e:
            print(f"Failed to start measurement: {e}")
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
    
def run_test_sequence(self, test_sequence_name, wait_for_completion=True, timeout=60):
        """Run specified test sequence"""
        try:
            test_environment = self.configuration.TestSetup.TestEnvironments.Item(1)
            test_sequence = None
            
            # Find test sequence
            for i in range(1, test_environment.TestSequences.Count + 1):
                seq = test_environment.TestSequences.Item(i)
                if seq.Name == test_sequence_name:
                    test_sequence = seq
                    break
            
            if not test_sequence:
                print(f"Test sequence not found: {test_sequence_name}")
                return False
            
            # Run test sequence
            test_sequence.Start()
            print(f"Started executing test sequence: {test_sequence_name}")
            
            if wait_for_completion:
                import time
                start_time = time.time()
                
                while test_sequence.Running:
                    if time.time() - start_time > timeout:
                        print(f"Test sequence execution timed out (>{timeout} seconds)")
                        test_sequence.Stop()
                        return False
                    time.sleep(1)
                
                print(f"Test sequence execution completed: {test_sequence_name}")
            
            return True
            
        except Exception as e:
            print(f"Failed to execute test sequence: {e}")
            return False
def get_test_results_summary(self):
        """Get test result summary"""
        try:
            test_service = self.can_app.GetTestService()
            test_results = test_service.Results
            
            summary = {
                'total_tests': test_results.Count,
                'passed': 0,
                'failed': 0,
                'inconclusive': 0,
                'total_execution_time': 0
            }
            
            # Count results
            for i in range(1, test_results.Count + 1):
                result = test_results.Item(i)
                verdict = result.Verdict
                
                if verdict == 1:  # Pass
                    summary['passed'] += 1
                elif verdict == 2:  # Fail
                    summary['failed'] += 1
                elif verdict == 3:  # Inconclusive
                    summary['inconclusive'] += 1
                
                summary['total_execution_time'] += result.ExecutionTime
            
            return summary
            
        except Exception as e:
            print(f"Failed to get test result summary: {e}")
            return None
    
def get_detailed_test_results(self):
        """Get detailed test results"""
        try:
            test_service = self.can_app.GetTestService()
            test_results = test_service.Results
            
            detailed_results = []
            
            for i in range(1, test_results.Count + 1):
                result = test_results.Item(i)
                
                test_info = {
                    'name': result.Name,
                    'verdict': self._verdict_to_string(result.Verdict),
                    'execution_time': result.ExecutionTime,
                    'start_time': result.StartTime,
                    'end_time': result.EndTime,
                    'error_message': result.ErrorMessage if hasattr(result, 'ErrorMessage') else ""
                }
                
                detailed_results.append(test_info)
            
            return detailed_results
            
        except Exception as e:
            print(f"Failed to get detailed test results: {e}")
            return None
    
def _verdict_to_string(self, verdict):
        """Convert verdict code to string"""
        verdict_map = {
            0: "None",
            1: "Pass",
            2: "Fail", 
            3: "Inconclusive"
        }
        return verdict_map.get(verdict, "Unknown")
    
def generate_statistics_report(self, output_file=None):
        """Generate statistics report"""
        summary = self.get_test_results_summary()
        detailed_results = self.get_detailed_test_results()
        
        if not summary or not detailed_results:
            print("Unable to generate statistics report")
            return False
        
        # Generate text report
        report_content = self._format_statistics_report(summary, detailed_results)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Statistics report saved to: {output_file}")
        else:
            print(report_content)
        
        return True
    
def _format_statistics_report(self, summary, detailed_results):
        """Format statistics report"""
        report = "=" * 50 + "\n"
        report += "CANoe Test Statistics Report\n"
        report += "=" * 50 + "\n\n"
        
        # Summary section
        report += "Test Summary:\n"
        report += f"  Total tests: {summary['total_tests']}\n"
        report += f"  Passed: {summary['passed']}\n"
        report += f"  Failed: {summary['failed']}\n"
        report += f"  Inconclusive: {summary['inconclusive']}\n"
        report += f"  Total execution time: {summary['total_execution_time']:.2f} seconds\n"
        
        if summary['total_tests'] > 0:
            pass_rate = (summary['passed'] / summary['total_tests']) * 100
            report += f"  Pass rate: {pass_rate:.1f}%\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += "Detailed Test Results:\n"
        report += "=" * 50 + "\n"
        
        # Detailed results
        for i, test in enumerate(detailed_results, 1):
            report += f"\n{i}. {test['name']}\n"
            report += f"   Verdict: {test['verdict']}\n"
            report += f"   Execution time: {test['execution_time']:.2f} seconds\n"
            report += f"   Start time: {test['start_time']}\n"
            report += f"   End time: {test['end_time']}\n"
            if test['error_message']:
                report += f"   Error message: {test['error_message']}\n"
        
        return report
# ====================== HÀM CHÍNH ======================
def main():
    # Create report manager instance
    report_manager = CANoeReportManager()
    
    # Connect to CANoe
    if not report_manager.connect_to_canoe():
        return
    
    # Open configuration file
    cfg_file = r"D:\Config\VF2_LHD.cfg"
    if not report_manager.open_configuration(cfg_file):
        return
    
    # Configure HTML report
    output_dir = r"D:\VF2\Report"
    if not report_manager.configure_html_report(output_dir):
        return
    
    # Start measurement
    if not report_manager.start_measurement():
        return
    
    try:
        # Run test sequence
        test_sequence_name = "MainTestSequence"
        if report_manager.run_test_sequence(test_sequence_name, timeout=120):
            # Generate statistics report
            stats_report = os.path.join(output_dir, f"Statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            report_manager.generate_statistics_report(stats_report)
        
    finally:
        # Stop measurement
        report_manager.stop_measurement()
# ====================== CHẠY CHƯƠNG TRÌNH ======================
if __name__ == "__main__":
    main()
   