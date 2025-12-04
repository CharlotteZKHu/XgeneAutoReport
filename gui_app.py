import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import sys
import threading
import os
import shutil
import pandas as pd
import config
import data_handler
import report_compiler
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

class SmartRedirector(object):
    """
    Redirects print statements to the GUI text widget.
    Colors text RED if it contains "WARNING" or "ERROR".
    """
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_text):
        if not str_text: return
        self.widget.after(0, self._append_text, str_text)

    def _append_text(self, text):
        self.widget.configure(state="normal")
        
        # Determine tag based on content
        tag = "normal"
        upper_text = text.upper()
        
        if "ERROR" in upper_text or "FAIL" in upper_text:
            tag = "error"
        elif "WARNING" in upper_text:
            tag = "warning"
        elif "SUCCESS" in upper_text:
            tag = "success"
        elif "PROCESSING" in upper_text:
            tag = "info"
            
        self.widget.insert("end", text, (tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class EnterpriseReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("X-Gene Diagnostics | Laboratory Information System")
        self.root.geometry("1100x780")
        self.root.minsize(950, 650)
        
        # --- APP ICON (Window Title Bar & Taskbar) ---
        try:
            # Using x-gene_icon2.png as requested
            icon_path = os.path.join(config.ASSETS_DIR, "x-gene_icon2.png")
            if os.path.exists(icon_path):
                self.app_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, self.app_icon)
        except Exception as e:
            print(f"Warning: Could not load app icon: {e}")

        # --- BIOMEDICAL THEME PALETTE ---
        self.c = {
            "sidebar_bg":   "#263238",  # Dark Slate Blue (Professional, Stable)
            "sidebar_fg":   "#CFD8DC",  # Blue-Grey text
            "main_bg":      "#ECEFF1",  # Light Blue-Grey (Sterile background)
            "card_bg":      "#FFFFFF",  # Pure White (Cards)
            "accent":       "#00897B",  # Teal (Scientific/Medical accent)
            "accent_hover": "#00796B",  # Darker Teal
            "text_dark":    "#37474F",  # Dark Slate text
            "text_light":   "#78909C",  # Light Slate text
            "success":      "#2E7D32",  # Medical Green
            "warning":      "#D32F2F",  # Alert Red
            "error":        "#B71C1C",  # Deep Red
            "input_bg":     "#F7F9F9",  # Very light input field
            "status_bar":   "#263238",  # Matches Sidebar
            "status_fg":    "#ECEFF1"   # Light text for dark footer
        }
        
        # --- FONTS ---
        base_font = "Segoe UI" if "win" in sys.platform else "Helvetica Neue"
        self.f_header = font.Font(family=base_font, size=18, weight="bold")
        self.f_card_title = font.Font(family=base_font, size=11, weight="bold")
        self.f_sub = font.Font(family=base_font, size=11, weight="bold")
        self.f_norm = font.Font(family=base_font, size=10)
        self.f_mono = font.Font(family="Consolas", size=9)

        # --- FIX: Initialize Variables FIRST ---
        self.demographics_path = tk.StringVar()
        self.results_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # --- LAYOUT CONSTRUCTION ---
        self.sidebar = tk.Frame(root, bg=self.c["sidebar_bg"], width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.right_panel = tk.Frame(root, bg=self.c["main_bg"])
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_main_content()
        self._build_status_bar()
        
        # Redirect stdout/stderr
        self.redirector = SmartRedirector(self.log_widget)
        sys.stdout = self.redirector
        sys.stderr = self.redirector

    def _build_sidebar(self):
        brand_frame = tk.Frame(self.sidebar, bg=self.c["sidebar_bg"], pady=40)
        brand_frame.pack(fill=tk.X)
        
        # Updated Icon Name: x-gene_icon2.png
        try:
            icon_path = os.path.join(config.ASSETS_DIR, "x-gene_icon2.png")
            if os.path.exists(icon_path):
                self.icon_img = tk.PhotoImage(file=icon_path)
                self.icon_img = self.icon_img.subsample(2, 2) 
                tk.Label(brand_frame, image=self.icon_img, bg=self.c["sidebar_bg"]).pack()
        except:
            pass 
            
        tk.Label(brand_frame, text="X-GENE", font=(self.f_header.cget("family"), 20, "bold"), 
                 bg=self.c["sidebar_bg"], fg="#FFFFFF").pack(pady=(15,0))
        tk.Label(brand_frame, text="LABORATORY SYSTEMS", font=(self.f_header.cget("family"), 9, "bold"), 
                 bg=self.c["sidebar_bg"], fg="#90A4AE").pack()

        tk.Frame(self.sidebar, bg="#37474F", height=1).pack(fill=tk.X, padx=20, pady=20)

        # Only "Report Generator" remains
        self._sidebar_item("  Report Generator", True)
        # Removed "Batch History" & "System Config"
        
        tk.Label(self.sidebar, text="v2.7.3 | Enterprise", bg=self.c["sidebar_bg"], fg="#546E7A", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=20)

    def _sidebar_item(self, text, active=False):
        bg = self.c["sidebar_bg"]
        fg = self.c["sidebar_fg"]
        font_style = self.f_norm
        
        if active:
            bg = "#37474F"
            fg = "#FFFFFF"
            font_style = self.f_sub
            
        btn = tk.Label(self.sidebar, text=text, font=font_style, bg=bg, fg=fg, anchor="w", padx=25, pady=12, cursor="hand2")
        btn.pack(fill=tk.X)
        if active:
            tk.Frame(btn, bg=self.c["accent"], width=5).pack(side=tk.LEFT, fill=tk.Y)

    def _build_main_content(self):
        header = tk.Frame(self.right_panel, bg="#FFFFFF", height=70, padx=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Report Generation", font=self.f_header, bg="#FFFFFF", fg=self.c["text_dark"]).pack(side=tk.LEFT, fill=tk.Y)

        self.pad = tk.Frame(self.right_panel, bg=self.c["main_bg"], padx=40, pady=30)
        self.pad.pack(fill=tk.BOTH, expand=True)

        input_card = self._create_card(self.pad, "Batch Configuration")
        input_card.pack(fill=tk.X, pady=(0, 20))
        
        self._make_row(input_card, "Patient Demographics", self.demographics_path, self.browse_demographics)
        self._make_row(input_card, "Lab Results (Crosswalk)", self.results_path, self.browse_results)
        self._make_row(input_card, "Archive Location (Opt)", self.output_path, self.browse_output, is_dir=True)

        btn_frame = tk.Frame(input_card, bg=self.c["card_bg"], pady=10)
        btn_frame.pack(fill=tk.X)
        
        self.run_btn = tk.Button(btn_frame, text="INITIATE BATCH PROCESSING", 
                                 bg=self.c["accent"], fg="#FFFFFF",
                                 activebackground=self.c["accent_hover"], activeforeground="#FFFFFF",
                                 font=("Segoe UI", 10, "bold"), relief="flat", padx=30, pady=10,
                                 cursor="hand2", command=self.start_generation_thread)
        self.run_btn.pack(side=tk.RIGHT)

        log_card = self._create_card(self.pad, "System Execution Logs")
        log_card.pack(fill=tk.BOTH, expand=True)
        
        self.log_widget = scrolledtext.ScrolledText(log_card, font=self.f_mono, state="disabled", 
                                                    bd=0, bg="#FAFAFA", padx=15, pady=15)
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.log_widget.tag_config("normal", foreground="#455A64")
        self.log_widget.tag_config("info", foreground=self.c["accent"], font=(self.f_mono.cget("family"), 9, "bold"))
        self.log_widget.tag_config("success", foreground=self.c["success"], font=(self.f_mono.cget("family"), 9, "bold"))
        self.log_widget.tag_config("warning", foreground=self.c["warning"], font=(self.f_mono.cget("family"), 9, "bold"))
        self.log_widget.tag_config("error", foreground=self.c["error"], font=(self.f_mono.cget("family"), 9, "bold"))

    def _build_status_bar(self):
        status_frame = tk.Frame(self.right_panel, bg=self.c["status_bar"], height=35, padx=20)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        tk.Frame(status_frame, bg="#E0E0E0", height=1).pack(side=tk.TOP, fill=tk.X)
        
        self.status_lbl = tk.Label(status_frame, text="System Ready", font=("Segoe UI", 9, "bold"), 
                                   bg=self.c["status_bar"], fg=self.c["status_fg"])
        self.status_lbl.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(status_frame, text="X-Gene LIS Connected", font=("Segoe UI", 9), 
                 bg=self.c["status_bar"], fg="#90A4AE").pack(side=tk.RIGHT, fill=tk.Y)

    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.c["card_bg"], padx=25, pady=25)
        t_frame = tk.Frame(card, bg=self.c["card_bg"])
        t_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(t_frame, text=title.upper(), font=self.f_card_title, fg=self.c["text_light"], bg=self.c["card_bg"]).pack(anchor="w")
        tk.Frame(t_frame, bg="#ECEFF1", height=2).pack(fill=tk.X, pady=(8,0))
        return card

    def _make_row(self, parent, label, var, cmd, is_dir=False):
        row = tk.Frame(parent, bg=self.c["card_bg"])
        row.pack(fill=tk.X, pady=8)
        
        tk.Label(row, text=label, width=22, anchor="w", bg=self.c["card_bg"], fg=self.c["text_dark"], font=self.f_norm).pack(side=tk.LEFT)
        
        ent = tk.Entry(row, textvariable=var, font=("Segoe UI", 10), bg=self.c["input_bg"], 
                       fg=self.c["text_dark"],
                       relief="flat", highlightthickness=1, highlightbackground="#CFD8DC", highlightcolor=self.c["accent"])
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, ipady=6)
        
        icon = "📂" if is_dir else "📄"
        tk.Button(row, text=icon, command=cmd, bg=self.c["main_bg"], fg=self.c["text_dark"], 
                  relief="flat", padx=12, pady=3, cursor="hand2").pack(side=tk.LEFT)

    def browse_demographics(self):
        f = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if f: self.demographics_path.set(f)

    def browse_results(self):
        f = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if f: self.results_path.set(f)

    def browse_output(self):
        d = filedialog.askdirectory()
        if d: self.output_path.set(d)

    def start_generation_thread(self):
        self.run_btn.config(state="disabled", bg="#B0BEC5", text="PROCESSING...")
        self.status_lbl.config(text="Processing Request...", fg="#FFFFFF")
        self.log_widget.configure(state="normal")
        self.log_widget.delete(1.0, tk.END)
        self.log_widget.configure(state="disabled")
        threading.Thread(target=self.run_process, daemon=True).start()

    def _finish(self, total, success, fail):
        self.run_btn.config(state="normal", bg=self.c["accent"], text="INITIATE BATCH PROCESSING")
        self.status_lbl.config(text="Processing Complete", fg=self.c["status_fg"])
        messagebox.showinfo("Report Summary", f"Batch Complete.\n\nTotal: {total}\nSuccess: {success}\nFailed: {fail}")

    def _reset_error(self):
        self.run_btn.config(state="normal", bg=self.c["accent"], text="INITIATE BATCH PROCESSING")
        self.status_lbl.config(text="System Error", fg="#EF5350")

    def run_process(self):
        try:
            d_path = self.demographics_path.get()
            r_path = self.results_path.get()
            copy_dest = self.output_path.get()

            if not d_path or not r_path:
                print("ERROR: Missing input files.")
                self.root.after(0, self._reset_error)
                return

            print("--- Starting Batch Analysis ---")
            
            if os.path.exists(config.OUTPUT_DIR):
                try:
                    shutil.rmtree(config.OUTPUT_DIR)
                    os.makedirs(config.OUTPUT_DIR)
                    print(f"INFO: Output directory cleaned: {config.OUTPUT_DIR}")
                except Exception as e:
                    print(f"WARNING: Could not clean output directory: {e}")
            else:
                os.makedirs(config.OUTPUT_DIR)
            
            demographics_df = data_handler.load_demographics(d_path)
            crosswalk_df = data_handler.load_crosswalk(r_path)
            results_sheets_dict = data_handler.load_all_results_sheets(r_path, crosswalk_df)

            if demographics_df is None or crosswalk_df is None or not results_sheets_dict:
                print("CRITICAL ERROR: Data Verification Failed.")
                self.root.after(0, self._reset_error)
                return

            success = 0
            fail = 0
            total_reports = 0

            for _, patient_row in demographics_df.iterrows():
                p_code = patient_row['Barcode']
                p_panel = patient_row['Panel']
                
                try:
                    entry = crosswalk_df.loc[p_panel]
                    t_name = entry['Result Template']
                    s_name = entry['Result Sheet']
                except KeyError:
                    print(f"Skipping {p_code}: Panel '{p_panel}' unknown.")
                    fail += 1
                    continue

                t_path = os.path.join(config.TEMPLATE_DIR, f"{t_name}.tex")
                if not os.path.exists(t_path):
                    print(f"Skipping {p_code}: Template '{t_name}' missing.")
                    fail += 1
                    continue

                if s_name not in results_sheets_dict:
                    print(f"Skipping {p_code}: Sheet '{s_name}' missing.")
                    fail += 1
                    continue
                
                res_df = results_sheets_dict[s_name]
                p_res_df = res_df[res_df['Barcode'] == p_code]

                if p_res_df.empty:
                    print(f"Info: No results for {p_code} in '{s_name}'.")
                    continue
                
                total_reports += len(p_res_df)

                for _, res_row in p_res_df.iterrows():
                    p_df = pd.DataFrame([patient_row])
                    r_df = pd.DataFrame([res_row])
                    merged = pd.merge(r_df, p_df.drop(columns=['Panel']), on='Barcode', how='left')
                    rec = merged.to_dict('records')[0]
                    
                    if report_compiler.compile_single_report(rec, t_path, config.OUTPUT_DIR, p_panel, s_name):
                        success += 1
                    else:
                        fail += 1

            if copy_dest and os.path.isdir(copy_dest):
                print(f"Archiving files to: {copy_dest}")
                count = 0
                for root, _, files in os.walk(config.OUTPUT_DIR):
                    for f in files:
                        if f.lower().endswith(".pdf"):
                            src = os.path.join(root, f)
                            rel = os.path.relpath(root, config.OUTPUT_DIR)
                            dst_dir = os.path.join(copy_dest, rel)
                            if not os.path.exists(dst_dir): os.makedirs(dst_dir)
                            shutil.copy2(src, os.path.join(dst_dir, f))
                            count += 1
                print(f"SUCCESS: Archived {count} files.")

            print(f"Batch Finished. Success: {success}, Failed: {fail}")
            self.root.after(0, lambda: self._finish(total_reports, success, fail))

        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, self._reset_error)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = tk.Tk()
    app = EnterpriseReportApp(root)
    root.mainloop()