import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pdf_generator import generate_pdf
from docx_generator import generate_docx
from video_utils import extract_thumbnails

def get_settings_path():
    app_data = os.getenv('APPDATA')
    if not app_data:
        app_data = os.path.dirname(os.path.abspath(__file__))
    
    config_dir = os.path.join(app_data, 'Images2PDF')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'settings.json')

SETTINGS_FILE = get_settings_path()

# Set Sleek Dark Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PDFGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IMAGES to PDF Converter")
        # Larger window for a more spacious, modern feel
        self.geometry("700x500")
        self.resizable(False, False)
        
        # Configure grid layout for the main window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        self.source_dir = ctk.StringVar(value=os.path.join(downloads_dir, 'Content'))
        self.output_path = ctk.StringVar(value=os.path.join(downloads_dir, 'Report'))
        
        self.settings = self.load_settings()
        self.create_widgets()
        
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def create_widgets(self):
        # Top Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=40, pady=(35, 10), sticky="w")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="IMAGES to PDF Converter", 
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold")
        )
        title_label.pack(anchor="w")
        
        author_label = ctk.CTkLabel(
            header_frame, 
            text="by GamesBondGIT", 
            font=ctk.CTkFont(family="Helvetica", size=14, slant="italic"),
            text_color="gray60"
        )
        author_label.pack(anchor="w", padx=2) 
        
        # Main Content Area (Card Layout)
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- File Selection Section ---
        # Source Directory
        src_label = ctk.CTkLabel(main_frame, text="Source Directory", font=ctk.CTkFont(size=14, weight="bold"))
        src_label.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")
        
        src_entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        src_entry_frame.grid(row=1, column=0, padx=30, pady=0, sticky="ew")
        src_entry_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkEntry(
            src_entry_frame, 
            textvariable=self.source_dir, 
            height=40,
            placeholder_text="Select the Content folder...",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 15))
        
        ctk.CTkButton(
            src_entry_frame, 
            text="Browse", 
            command=self.browse_source, 
            height=40, 
            width=100,
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1)

        # Output File Base
        out_label = ctk.CTkLabel(main_frame, text="Output File Base Name", font=ctk.CTkFont(size=14, weight="bold"))
        out_label.grid(row=2, column=0, padx=30, pady=(20, 5), sticky="w")
        
        out_entry_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        out_entry_frame.grid(row=3, column=0, padx=30, pady=0, sticky="ew")
        out_entry_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkEntry(
            out_entry_frame, 
            textvariable=self.output_path, 
            height=40,
            placeholder_text="e.g. C:/Reports/MyReport (no extension)",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 15))
        
        ctk.CTkButton(
            out_entry_frame, 
            text="Browse", 
            command=self.browse_output, 
            height=40, 
            width=100,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#4b5563",
            hover_color="#374151"
        ).grid(row=0, column=1)

        # --- Actions Section ---
        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.grid(row=4, column=0, padx=30, pady=(40, 20), sticky="ew")
        actions_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            actions_frame, 
            text="⚙ Settings", 
            command=self.open_settings, 
            height=45,
            width=140,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#374151", 
            hover_color="#1f2937"
        ).grid(row=0, column=0, sticky="w")
        
        self.generate_btn = ctk.CTkButton(
            actions_frame, 
            text="Generate Report", 
            command=self.start_generation, 
            height=45,
            width=200,
            font=ctk.CTkFont(size=15, weight="bold"), 
            fg_color="#10b981", 
            hover_color="#059669",
            text_color="white"
        )
        self.generate_btn.grid(row=0, column=1, sticky="e")
        
        # --- Progress Section (Hidden initially) ---
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, variable=self.progress_var, width=620, height=10, progress_color="#10b981")
        self.progress_bar.pack(pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Starting generation...", text_color="gray70", font=ctk.CTkFont(size=12))
        self.status_label.pack()

    def browse_source(self):
        dir_path = filedialog.askdirectory(title="Select Source Directory")
        if dir_path:
            self.source_dir.set(dir_path)
            default_out = os.path.join(dir_path, "Report")
            self.output_path.set(default_out)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(title="Save Base File As")
        if file_path:
            base, ext = os.path.splitext(file_path)
            self.output_path.set(base)

    def update_progress(self, percent):
        self.progress_var.set(percent / 100.0)
        self.status_label.configure(text=f"Generating... {percent}% complete")
        self.update_idletasks()

    def start_generation(self):
        src = self.source_dir.get()
        out_base = self.output_path.get()
        
        if not src or not out_base:
            messagebox.showerror("Error", "Please select both source and output paths.")
            return
            
        self.generate_btn.configure(state="disabled")
        
        # Show progress bar
        self.progress_frame.grid(row=2, column=0, padx=40, pady=(0, 30), sticky="ew")
        
        self.progress_var.set(0)
        self.status_label.configure(text="Starting generation...", text_color="gray70")
        
        threading.Thread(target=self._run_generation, args=(src, out_base), daemon=True).start()
        
    def _run_generation(self, src, out_base):
        try:
            formats = self.settings.get('output_formats', {'pdf': True, 'docx': False})
            do_pdf = formats.get('pdf', True)
            do_docx = formats.get('docx', False)
            
            if not do_pdf and not do_docx:
                self.status_label.configure(text="No output formats selected in Settings.", text_color="#ef4444")
                self.generate_btn.configure(state="normal")
                return
            
            def make_progress_callback(start_pct, scale):
                def callback(percent):
                    scaled = start_pct + (percent * scale / 100.0)
                    self.update_progress(int(scaled))
                return callback

            # Extract thumbnails if requested
            video_settings = self.settings.get('video_thumbs', {})
            if video_settings.get('enabled', False):
                self.status_label.configure(text="Extracting video thumbnails...", text_color="gray70")
                extract_thumbnails(
                    src, 
                    frame_number=video_settings.get('frame_number', 1),
                    progress_callback=make_progress_callback(0, 10) # Takes 10% of total progress
                )
                start_progress = 10
                scale_progress = 90
            else:
                start_progress = 0
                scale_progress = 100

            success = False
            last_out = None
            if do_pdf and do_docx:
                success_pdf = generate_pdf(src, out_base + ".pdf", SETTINGS_FILE, progress_callback=make_progress_callback(start_progress, scale_progress / 2))
                success_docx = generate_docx(src, out_base + ".docx", SETTINGS_FILE, progress_callback=make_progress_callback(start_progress + (scale_progress / 2), scale_progress / 2))
                success = success_pdf or success_docx
                last_out = out_base + ".docx"
            elif do_pdf:
                success = generate_pdf(src, out_base + ".pdf", SETTINGS_FILE, progress_callback=make_progress_callback(start_progress, scale_progress))
                last_out = out_base + ".pdf"
            elif do_docx:
                success = generate_docx(src, out_base + ".docx", SETTINGS_FILE, progress_callback=make_progress_callback(start_progress, scale_progress))
                last_out = out_base + ".docx"
                
            if success:
                self.status_label.configure(text="Finished successfully!", text_color="#10b981")
                self.after(1000, lambda: os.startfile(os.path.dirname(last_out)))
            else:
                self.status_label.configure(text="No images found.", text_color="#f59e0b")
                messagebox.showwarning("Warning", "No images found in the selected directory.")
        except Exception as e:
            self.status_label.configure(text="Error occurred.", text_color="#ef4444")
            messagebox.showerror("Error", f"Failed to generate Report:\n{str(e)}")
        finally:
            self.generate_btn.configure(state="normal")

    def open_settings(self):
        SettingsDialog(self, self.settings, self.save_settings)


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings, save_callback):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("500x470")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.settings = settings
        self.save_callback = save_callback
        
        self.create_widgets()
        
    def create_widgets(self):
        tabview = ctk.CTkTabview(self, corner_radius=10)
        tabview.pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        tabview.add("General")
        tabview.add("Titles")
        tabview.add("Grids")
        
        # --- General Tab ---
        tab_gen = tabview.tab("General")
        tab_gen.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(tab_gen, text="Page Size:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky='w')
        self.page_size_var = ctk.StringVar(value=self.settings.get('page_size', 'A4'))
        ctk.CTkOptionMenu(tab_gen, variable=self.page_size_var, values=['A4', 'LETTER'], width=150).grid(row=0, column=1, padx=20, pady=20, sticky='w')
        
        formats = self.settings.get('output_formats', {'pdf': True, 'docx': False})
        ctk.CTkLabel(tab_gen, text="Output Formats:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 5), sticky='w')
        
        self.fmt_pdf_var = ctk.BooleanVar(value=formats.get('pdf', True))
        ctk.CTkCheckBox(tab_gen, text="Generate PDF (.pdf)", variable=self.fmt_pdf_var).grid(row=2, column=0, columnspan=2, padx=40, pady=5, sticky='w')
        
        self.fmt_docx_var = ctk.BooleanVar(value=formats.get('docx', False))
        ctk.CTkCheckBox(tab_gen, text="Generate Word Doc (.docx)", variable=self.fmt_docx_var).grid(row=3, column=0, columnspan=2, padx=40, pady=5, sticky='w')
        
        video_settings = self.settings.get('video_thumbs', {})
        ctk.CTkLabel(tab_gen, text="Video Thumbnails:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=20, pady=(10, 5), sticky='w')
        self.gen_thumbs_var = ctk.BooleanVar(value=video_settings.get('enabled', False))
        ctk.CTkCheckBox(tab_gen, text="Generate Thumbs from 'Videos' folder", variable=self.gen_thumbs_var).grid(row=5, column=0, columnspan=2, padx=40, pady=5, sticky='w')
        
        ctk.CTkLabel(tab_gen, text="Frame Number to Extract:").grid(row=6, column=0, padx=(40, 5), pady=5, sticky='w')
        self.thumb_frame_var = ctk.StringVar(value=str(video_settings.get('frame_number', 1)))
        ctk.CTkEntry(tab_gen, textvariable=self.thumb_frame_var, width=60).grid(row=6, column=1, padx=5, pady=5, sticky='w')

        # --- Titles Tab ---
        tab_titles = tabview.tab("Titles")
        tab_titles.grid_columnconfigure((1, 3), weight=1)
        
        title_settings = self.settings.get('title_page', {})
        
        ctk.CTkLabel(tab_titles, text="Main Title:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=(15,5), sticky='w')
        self.title_text_var = ctk.StringVar(value=title_settings.get('title_text', 'I&I Content Report'))
        ctk.CTkEntry(tab_titles, textvariable=self.title_text_var, width=150).grid(row=0, column=1, padx=5, pady=(15,5), sticky='w')
        
        ctk.CTkLabel(tab_titles, text="Size:").grid(row=0, column=2, padx=5, pady=(15,5), sticky='w')
        self.title_font_size_var = ctk.StringVar(value=str(title_settings.get('title_font_size', 36)))
        ctk.CTkEntry(tab_titles, textvariable=self.title_font_size_var, width=50).grid(row=0, column=3, padx=5, pady=(15,5), sticky='w')
        
        ctk.CTkLabel(tab_titles, text="Subtitle:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.subtitle_text_var = ctk.StringVar(value=title_settings.get('subtitle_text', 'Posters & Videos'))
        ctk.CTkEntry(tab_titles, textvariable=self.subtitle_text_var, width=150).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ctk.CTkLabel(tab_titles, text="Size:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.subtitle_font_size_var = ctk.StringVar(value=str(title_settings.get('subtitle_font_size', 18)))
        ctk.CTkEntry(tab_titles, textvariable=self.subtitle_font_size_var, width=50).grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        img_settings = self.settings.get('images', {})
        
        self.show_img_titles_var = ctk.BooleanVar(value=img_settings.get('show_title', False))
        ctk.CTkCheckBox(tab_titles, text="Show Names Under Images", variable=self.show_img_titles_var, font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, columnspan=4, padx=20, pady=10, sticky='w')
        
        ctk.CTkLabel(tab_titles, text="Image Name Size:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=20, pady=10, sticky='w')
        self.img_title_size_var = ctk.StringVar(value=str(img_settings.get('title_font_size', 12)))
        ctk.CTkEntry(tab_titles, textvariable=self.img_title_size_var, width=80).grid(row=3, column=1, padx=5, pady=10, sticky='w')
        
        # --- Grids Tab ---
        tab_grids = tabview.tab("Grids")
        tab_grids.grid_columnconfigure((1, 3), weight=1)
        
        # Posters
        ctk.CTkLabel(tab_grids, text="Posters Grid", font=ctk.CTkFont(weight="bold", size=16)).grid(row=0, column=0, columnspan=4, padx=20, pady=(20, 10), sticky='w')
        
        posters_grid = self.settings.get('posters_grid', {})
        ctk.CTkLabel(tab_grids, text="Columns:").grid(row=1, column=0, padx=(20, 5), pady=10, sticky='w')
        self.p_col_var = ctk.StringVar(value=str(posters_grid.get('columns', 2)))
        ctk.CTkEntry(tab_grids, textvariable=self.p_col_var, width=60).grid(row=1, column=1, padx=5, pady=10, sticky='w')
        
        ctk.CTkLabel(tab_grids, text="Rows:").grid(row=1, column=2, padx=(20, 5), pady=10, sticky='w')
        self.p_row_var = ctk.StringVar(value=str(posters_grid.get('rows', 2)))
        ctk.CTkEntry(tab_grids, textvariable=self.p_row_var, width=60).grid(row=1, column=3, padx=5, pady=10, sticky='w')
        
        # Videos
        ctk.CTkLabel(tab_grids, text="Videos Grid", font=ctk.CTkFont(weight="bold", size=16)).grid(row=2, column=0, columnspan=4, padx=20, pady=(20, 10), sticky='w')
        
        videos_grid = self.settings.get('videos_grid', {})
        ctk.CTkLabel(tab_grids, text="Columns:").grid(row=3, column=0, padx=(20, 5), pady=10, sticky='w')
        self.v_col_var = ctk.StringVar(value=str(videos_grid.get('columns', 2)))
        ctk.CTkEntry(tab_grids, textvariable=self.v_col_var, width=60).grid(row=3, column=1, padx=5, pady=10, sticky='w')
        
        ctk.CTkLabel(tab_grids, text="Rows:").grid(row=3, column=2, padx=(20, 5), pady=10, sticky='w')
        self.v_row_var = ctk.StringVar(value=str(videos_grid.get('rows', 3)))
        ctk.CTkEntry(tab_grids, textvariable=self.v_row_var, width=60).grid(row=3, column=3, padx=5, pady=10, sticky='w')
        
        # --- Save Button ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            btn_frame, 
            text="Save Settings", 
            command=self.save_and_close, 
            font=ctk.CTkFont(weight="bold"), 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            height=40
        ).pack(side="right")

    def save_and_close(self):
        self.settings['page_size'] = self.page_size_var.get()
        
        if 'output_formats' not in self.settings:
            self.settings['output_formats'] = {}
        self.settings['output_formats']['pdf'] = self.fmt_pdf_var.get()
        self.settings['output_formats']['docx'] = self.fmt_docx_var.get()
        
        if 'video_thumbs' not in self.settings:
            self.settings['video_thumbs'] = {}
        self.settings['video_thumbs']['enabled'] = self.gen_thumbs_var.get()
        try:
            self.settings['video_thumbs']['frame_number'] = int(self.thumb_frame_var.get())
        except ValueError:
            pass
        
        if 'title_page' not in self.settings:
            self.settings['title_page'] = {}
        self.settings['title_page']['title_text'] = self.title_text_var.get()
        self.settings['title_page']['subtitle_text'] = self.subtitle_text_var.get()
        
        try:
            self.settings['title_page']['title_font_size'] = int(self.title_font_size_var.get())
            self.settings['title_page']['subtitle_font_size'] = int(self.subtitle_font_size_var.get())
        except ValueError:
            pass
            
        if 'images' not in self.settings:
            self.settings['images'] = {}
            
        self.settings['images']['show_title'] = self.show_img_titles_var.get()
            
        try:
            self.settings['images']['title_font_size'] = int(self.img_title_size_var.get())
        except ValueError:
            pass
            
        if 'posters_grid' not in self.settings:
            self.settings['posters_grid'] = {}
        try:
            self.settings['posters_grid']['columns'] = int(self.p_col_var.get())
            self.settings['posters_grid']['rows'] = int(self.p_row_var.get())
        except ValueError:
            pass

        if 'videos_grid' not in self.settings:
            self.settings['videos_grid'] = {}
        try:
            self.settings['videos_grid']['columns'] = int(self.v_col_var.get())
            self.settings['videos_grid']['rows'] = int(self.v_row_var.get())
        except ValueError:
            pass
            
        self.save_callback()
        self.destroy()

if __name__ == "__main__":
    app = PDFGeneratorApp()
    app.mainloop()
