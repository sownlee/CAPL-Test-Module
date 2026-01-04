import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import win32com.client
import time
import json
from datetime import datetime
import openpyxl

class DTCTool:
    def __init__(self, root):
        self.root = root
        self.root.title("DTC Reader Tool with CANoe API")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.ecus = {}  # ECU name -> dict
        self.load_ecus()  # Load from json
        self.canoe_app = None
        self.canoe_meas = None
        self.vehicle_vin = "RLNVMNMS6ST199010"  # Default VIN, can edit

        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Tab 1: ECU Management
        self.tab_ecu = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ecu, text="ECU Management")

        left_frame = tk.Frame(self.tab_ecu)
        left_frame.grid(row=0, column=0, sticky="n", padx=10)

        right_frame = tk.Frame(self.tab_ecu)
        right_frame.grid(row=0, column=1, sticky="n", padx=10)

        # Pick Vehicle
        tk.Label(left_frame, text="Pick Vehicle:").pack(anchor="w")
        self.vehicle_var = tk.StringVar(value="VF2")
        ttk.Entry(left_frame, textvariable=self.vehicle_var).pack(anchor="w")

        # VIN
        tk.Label(left_frame, text="VIN:").pack(anchor="w")
        self.vin_var = tk.StringVar(value=self.vehicle_vin)
        ttk.Entry(left_frame, textvariable=self.vin_var).pack(anchor="w")

        # CAN Channel
        tk.Label(left_frame, text="CAN Channel:").pack(anchor="w")
        self.channel_var = tk.StringVar(value="1")
        ttk.Combobox(left_frame, textvariable=self.channel_var, values=["1", "2", "3", "4"]).pack(anchor="w")

        # Pick ECU (dropdown)
        tk.Label(left_frame, text="Pick ECU:").pack(anchor="w")
        self.ecu_combo = ttk.Combobox(left_frame, values=list(self.ecus.keys()))
        self.ecu_combo.pack(anchor="w")
        self.ecu_combo.bind("<<ComboboxSelected>>", self.load_ecu_details)

        ttk.Button(left_frame, text="Add New ECU", command=self.add_new_ecu).pack(anchor="w")

        # ID Request/Response
        tk.Label(left_frame, text="ID Request (HEX):").pack(anchor="w")
        self.req_id_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.req_id_var).pack(anchor="w")

        tk.Label(left_frame, text="ID Response (HEX):").pack(anchor="w")
        self.resp_id_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.resp_id_var).pack(anchor="w")

        # DLL & DTC File
        tk.Label(left_frame, text="DLL File:").pack(anchor="w")
        self.dll_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.dll_var, state="readonly").pack(anchor="w")
        ttk.Button(left_frame, text="Import DLL", command=self.import_dll).pack(anchor="w")

        tk.Label(left_frame, text="DTC File:").pack(anchor="w")
        self.dtc_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.dtc_var, state="readonly").pack(anchor="w")
        ttk.Button(left_frame, text="Import DTC", command=self.import_dtc).pack(anchor="w")

        # Connect CANoe
        ttk.Button(left_frame, text="Connect CANoe", command=self.connect_canoe).pack(anchor="w", pady=10)

        # Read/Clear DTC for selected ECU
        ttk.Button(left_frame, text="Read DTC (Selected ECU)", command=self.read_dtc).pack(anchor="w", pady=5)
        ttk.Button(left_frame, text="Clear DTC (Selected ECU)", command=self.clear_dtc).pack(anchor="w", pady=5)

        # ECU List (right side)
        tk.Label(right_frame, text="ECU List").pack(anchor="w")
        self.ecu_listbox = tk.Listbox(right_frame, height=15, width=30)
        self.ecu_listbox.pack(anchor="w")
        self.ecu_listbox.bind("<<ListboxSelect>>", self.select_from_list)
        self.update_ecu_list()

        # Tab 2: Report Summary
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text="Report Summary")

        tk.Label(self.tab_report, text="Vehicle Report Summary").pack(pady=10)

        # Generate Report for all ECUs
        ttk.Button(self.tab_report, text="Generate Full DTC Report & Export XLSX", command=self.generate_report).pack(pady=10)

        # Report result text
        self.report_text = tk.Text(self.tab_report, height=20, width=80)
        self.report_text.pack(pady=10)

    def add_new_ecu(self):
        # same as before
        ecu_name = tk.simpledialog.askstring("Add ECU", "Enter ECU name:")
        if ecu_name:
            req_id = tk.simpledialog.askstring("ID Request", "Enter ID Request (HEX):", initialvalue="7DF")
            resp_id = tk.simpledialog.askstring("ID Response", "Enter ID Response (HEX):", initialvalue="7E8")
            self.ecus[ecu_name] = {'req_id': req_id or '7DF', 'resp_id': resp_id or '7E8', 'dll_file': '', 'dtc_file': ''}
            self.update_ecu_list()
            self.ecu_combo['values'] = list(self.ecus.keys())
            self.ecu_combo.set(ecu_name)
            self.load_ecu_details()

    def update_ecu_list(self):
        self.ecu_listbox.delete(0, tk.END)
        for ecu in self.ecus:
            self.ecu_listbox.insert(tk.END, ecu)

    def select_from_list(self, event):
        selection = self.ecu_listbox.curselection()
        if selection:
            ecu = self.ecu_listbox.get(selection[0])
            self.ecu_combo.set(ecu)
            self.load_ecu_details()

    def load_ecu_details(self, event=None):
        # same as before
        ecu = self.ecu_combo.get()
        if ecu in self.ecus:
            data = self.ecus[ecu]
            self.req_id_var.set(data['req_id'])
            self.resp_id_var.set(data['resp_id'])
            self.dll_var.set(data['dll_file'])
            self.dtc_var.set(data['dtc_file'])

    def import_dll(self):
        # same as before
        file = filedialog.askopenfilename(filetypes=[("DLL files", "*.dll")])
        if file:
            ecu = self.ecu_combo.get()
            if ecu:
                self.ecus[ecu]['dll_file'] = file
                self.dll_var.set(file)

    def import_dtc(self):
        # same as before
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file:
            ecu = self.ecu_combo.get()
            if ecu:
                self.ecus[ecu]['dtc_file'] = file
                self.dtc_var.set(file)

    def connect_canoe(self):
        # same as before
        try:
            self.canoe_app = win32com.client.Dispatch("CANoe.Application")
            self.canoe_meas = self.canoe_app.Measurement
            if self.canoe_meas.Running:
                messagebox.showinfo("Success", "Connected to CANoe! Measurement running.")
            else:
                self.canoe_meas.Start()
                messagebox.showinfo("Success", "Connected and started measurement.")
        except Exception as e:
            messagebox.showerror("Error", f"CANoe not running or COM error: {str(e)}\nRun CANoe first!")

    def send_diag_request(self, service, data=b''):
        # same as before
        ecu = self.ecu_combo.get()
        if not ecu or not self.canoe_app:
            return None

        channel = int(self.channel_var.get())
        req_id = int(self.ecus[ecu]['req_id'], 16)
        resp_id = int(self.ecus[ecu]['resp_id'], 16)

        try:
            diag = self.canoe_app.Diagnostic
            diag.Channel = channel
            diag.RequestID = req_id
            diag.ResponseID = resp_id

            payload = bytes([service]) + data
            response = diag.Request(payload, timeout=2000)
            return response if response else None
        except Exception as e:
            self.result_text.insert(tk.END, f"Diag error for {ecu}: {str(e)}\n")
            return None

    def read_dtc(self):
        self.result_text.delete(1.0, tk.END)
        ecu = self.ecu_combo.get()
        response = self.send_diag_request(0x19, b'\x02')
        if not response:
            self.result_text.insert(tk.END, f"No response from {ecu}\n")
            return

        dtc_codes = self.parse_dtc_response(response)

        dtc_file = self.ecus[ecu]['dtc_file']
        dtc_dict = self.load_dtc_dict(dtc_file)
        self.display_dtc(ecu, dtc_codes, dtc_dict, self.result_text)

    def clear_dtc(self):
        ecu = self.ecu_combo.get()
        response = self.send_diag_request(0x14, b'\xFF\xFF\xFF')
        if response and response[0] == 0x54:
            messagebox.showinfo("Success", f"DTC cleared for {ecu}!")
        else:
            messagebox.showerror("Error", f"Clear failed for {ecu}")

    def generate_report(self):
        self.report_text.delete(1.0, tk.END)
        report_data = []
        time_str = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
        vehicle = self.vehicle_var.get()
        vin = self.vin_var.get()

        for ecu in self.ecus:
            response = self.send_diag_request(0x19, b'\x02')
            if not response:
                report_data.append([ecu, "", "No response", ""])
                continue

            dtc_codes = self.parse_dtc_response(response)
            dtc_file = self.ecus[ecu]['dtc_file']
            dtc_dict = self.load_dtc_dict(dtc_file)

            if dtc_codes:
                for code in dtc_codes:
                    desc = dtc_dict.get(code, "Unknown")
                    report_data.append([ecu, code, desc, ""])
            else:
                report_data.append([ecu, "", "No DTC", ""])

        self.display_report(time_str, vehicle, vin, report_data)

        # Export to xlsx
        export_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if export_file:
            self.export_to_xlsx(time_str, vehicle, vin, report_data, export_file)
            messagebox.showinfo("Success", f"Report exported to {export_file}")

    def parse_dtc_response(self, response):
        dtc_codes = []
        if len(response) > 3 and response[0] == 0x59:
            num_dtcs = response[1]
            for i in range(num_dtcs):
                dtc_bytes = response[2 + i*3 : 5 + i*3]
                dtc_code = f"P{(dtc_bytes[0] & 0x3F):01X}{(dtc_bytes[0] >> 6):01X}{dtc_bytes[1]:02X}{dtc_bytes[2]:02X}"
                dtc_codes.append(dtc_code)
        return dtc_codes

    def load_dtc_dict(self, dtc_file):
        if dtc_file:
            try:
                df = pd.read_excel(dtc_file, sheet_name="DTC-List")
                return dict(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))
            except:
                return {}
        return {}

    def display_dtc(self, ecu, dtc_codes, dtc_dict, text_widget):
        text_widget.insert(tk.END, f"DTCs in {ecu} (Channel {self.channel_var.get()}):\n")
        if dtc_codes:
            for code in dtc_codes:
                desc = dtc_dict.get(code, "Unknown")
                text_widget.insert(tk.END, f"{code}: {desc}\n")
        else:
            text_widget.insert(tk.END, "No DTC\n")

    def display_report(self, time_str, vehicle, vin, report_data):
        self.report_text.insert(tk.END, f"Time: {time_str}\n")
        self.report_text.insert(tk.END, f"Vehicle: {vehicle}\n")
        self.report_text.insert(tk.END, f"VIN: {vin}\n\n")
        self.report_text.insert(tk.END, "DTC Report\n")
        for row in report_data:
            self.report_text.insert(tk.END, f"{row[0]}: {row[1]} {row[2]}\n")

    def export_to_xlsx(self, time_str, vehicle, vin, report_data, file):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Report"

        ws.append(["Time:", time_str])
        ws.append(["Vehicle:", vehicle])
        ws.append(["VIN:", vin])
        ws.append([])  # Blank
        ws.append(["DTC Report"])
        ws.append(["Node", "DTC Code", "DTC Name", "Status bytes", "Remark"])

        for row in report_data:
            ws.append(row + ["", ""])  # Add empty for Status, Remark

        wb.save(file)

    def load_ecus(self):
        if os.path.exists('ecus.json'):
            with open('ecus.json', 'r') as f:
                self.ecus = json.load(f)

    def on_close(self):
        with open('ecus.json', 'w') as f:
            json.dump(self.ecus, f)
        self.root.destroy()

root = tk.Tk()
app = DTCTool(root)
root.mainloop()