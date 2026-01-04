import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class DTCTool:
    def __init__(self, root):
        self.root = root
        self.root.title("DTC Reader Tool")
        self.root.geometry("600x400")

        self.ecus = {}  # ECU name -> {'req_id': str, 'resp_id': str, 'dll_file': str, 'dtc_file': str}

        # Pick Vehicle
        tk.Label(root, text="Pick Vehicle:").grid(row=0, column=0, sticky="w")
        self.vehicle_var = tk.StringVar(value="VF2")
        ttk.Entry(root, textvariable=self.vehicle_var).grid(row=0, column=1, sticky="w")

        # Pick ECU
        tk.Label(root, text="Pick ECU:").grid(row=1, column=0, sticky="w")
        self.ecu_combo = ttk.Combobox(root)
        self.ecu_combo.grid(row=1, column=1, sticky="w")
        self.ecu_combo.bind("<<ComboboxSelected>>", self.load_ecu_details)

        # Add New ECU
        ttk.Button(root, text="Add New ECU", command=self.add_new_ecu).grid(row=1, column=2, padx=10)

        # ID Request
        tk.Label(root, text="ID Request(HEX):").grid(row=2, column=0, sticky="w")
        self.req_id_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.req_id_var).grid(row=2, column=1, sticky="w")

        # ID Response
        tk.Label(root, text="ID Response(HEX):").grid(row=3, column=0, sticky="w")
        self.resp_id_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.resp_id_var).grid(row=3, column=1, sticky="w")

        # Similar names
        tk.Label(root, text="Similar names:").grid(row=4, column=0, sticky="w")
        self.similar_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.similar_var).grid(row=4, column=1, sticky="w")

        # DLL File
        tk.Label(root, text="DLL File:").grid(row=5, column=0, sticky="w")
        self.dll_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.dll_var, state="readonly").grid(row=5, column=1, sticky="w")
        ttk.Button(root, text="Import DLL", command=self.import_dll).grid(row=5, column=2, padx=10)

        # DTC File
        tk.Label(root, text="DTC File:").grid(row=6, column=0, sticky="w")
        self.dtc_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.dtc_var, state="readonly").grid(row=6, column=1, sticky="w")
        ttk.Button(root, text="Import DTC", command=self.import_dtc).grid(row=6, column=2, padx=10)

        # Read DTC button
        ttk.Button(root, text="Read DTC", command=self.read_dtc).grid(row=7, column=1, pady=20)

        # Result area
        self.result_text = tk.Text(root, height=10, width=60)
        self.result_text.grid(row=8, column=0, columnspan=3)

    def add_new_ecu(self):
        ecu_name = tk.simpledialog.askstring("Add ECU", "Enter ECU name:")
        if ecu_name:
            req_id = tk.simpledialog.askstring("ID Request", "Enter ID Request (HEX):")
            resp_id = tk.simpledialog.askstring("ID Response", "Enter ID Response (HEX):")
            self.ecus[ecu_name] = {'req_id': req_id or '', 'resp_id': resp_id or '', 'dll_file': '', 'dtc_file': ''}
            self.ecu_combo['values'] = list(self.ecus.keys())
            self.ecu_combo.set(ecu_name)
            self.load_ecu_details()

    def load_ecu_details(self, event=None):
        ecu = self.ecu_combo.get()
        if ecu in self.ecus:
            data = self.ecus[ecu]
            self.req_id_var.set(data['req_id'])
            self.resp_id_var.set(data['resp_id'])
            self.dll_var.set(data['dll_file'])
            self.dtc_var.set(data['dtc_file'])

    def import_dll(self):
        file = filedialog.askopenfilename(filetypes=[("DLL files", "*.dll")])
        if file:
            ecu = self.ecu_combo.get()
            if ecu:
                self.ecus[ecu]['dll_file'] = file
                self.dll_var.set(file)

    def import_dtc(self):
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file:
            ecu = self.ecu_combo.get()
            if ecu:
                self.ecus[ecu]['dtc_file'] = file
                self.dtc_var.set(file)

    def read_dtc(self):
        ecu = self.ecu_combo.get()
        if not ecu or not self.ecus[ecu]['dtc_file']:
            messagebox.showerror("Error", "Select ECU and import DTC file")
            return

        # Giả lập đọc DTC từ ECU (thay bằng diag thật: OBD/CANoe API)
        simulated_dtc_codes = ["P0001", "P0002", "U0001"]  # List DTC code đọc được từ ECU

        # Parse DTC list từ file xlsx (giả sử sheet "DTC-List" hoặc sheet 0, cột 0: DTC code, cột 1: Description)
        dtc_file = self.ecus[ecu]['dtc_file']
        try:
            df = pd.read_excel(dtc_file, sheet_name=0)  # Hoặc sheet_name="DTC-List"
            dtc_list = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))  # Cột 0: code, cột 1: desc

            # In ra DTC có trong ECU
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"DTC in {ecu}:\n")
            for code in simulated_dtc_codes:
                desc = dtc_list.get(code, "Not found in DTC list")
                self.result_text.insert(tk.END, f"{code}: {desc}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = tk.Tk()
app = DTCTool(root)
root.mainloop()