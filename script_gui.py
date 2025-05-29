import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import shutil
from datetime import datetime
import logging
from pathlib import Path
from PIL import Image
import piexif
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import queue
import platform
import darkdetect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MediaOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media File Organizer")
        
        # Configure scaling for Retina displays
        if platform.system() == 'Darwin':
            self.root.tk.call('tk', 'scaling', 2.0)
        
        # Detect system theme
        self.is_dark_mode = darkdetect.isDark()
        
        # Set color scheme based on theme
        self.colors = self.get_color_scheme()
        
        # Configure window size and background
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors['bg'])
        
        # Main container with padding
        main_frame = tk.Frame(root, padx=20, pady=20, bg=self.colors['bg'])
        main_frame.pack(expand=True, fill='both')
        
        # Directory selection with improved visibility
        dir_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        dir_frame.pack(fill='x', pady=(0, 10))
        
        # Directory label with larger font and bold
        dir_label = tk.Label(dir_frame, 
                           text="Directory:", 
                           font=('SF Pro Display', 13, 'bold'),
                           bg=self.colors['bg'],
                           fg=self.colors['fg'])
        dir_label.pack(side='left', padx=(0, 10))
        
        # Directory entry with enhanced visibility
        entry_frame = tk.Frame(dir_frame, 
                             bg=self.colors['border'],
                             padx=1, 
                             pady=1)
        entry_frame.pack(side='left', fill='x', expand=True, padx=5)
        
        self.dir_entry = tk.Entry(entry_frame, 
                                font=('SF Pro Display', 12),
                                bg=self.colors['input_bg'],
                                fg=self.colors['input_fg'],
                                insertbackground=self.colors['input_fg'])
        self.dir_entry.pack(fill='x', expand=True, ipady=5)
        
        # Browse button with improved styling
        browse_btn = tk.Button(dir_frame, 
                             text="Browse",
                             command=self.browse_directory,
                             font=('SF Pro Display', 12),
                             bg=self.colors['button_bg'],
                             fg=self.colors['button_fg'],
                             activebackground=self.colors['button_active_bg'],
                             activeforeground=self.colors['button_fg'],
                             relief='flat',
                             padx=15,
                             pady=5)
        browse_btn.pack(side='left', padx=(5, 0))
        
        # Options group with improved visibility
        options_frame = tk.LabelFrame(main_frame, 
                                    text="Options",
                                    font=('SF Pro Display', 12, 'bold'),
                                    bg=self.colors['frame_bg'],
                                    fg=self.colors['fg'],
                                    padx=15, pady=10)
        options_frame.pack(fill='x', pady=10)
        
        # Organization structure
        org_frame = tk.Frame(options_frame, bg=self.colors['frame_bg'])
        org_frame.pack(fill='x', pady=5)
        
        tk.Label(org_frame,
                text="Organize by:",
                font=('SF Pro Display', 12),
                bg=self.colors['frame_bg'],
                fg=self.colors['fg']).pack(side='left')
        
        self.organize_var = tk.StringVar(value="date")
        org_options = ["date", "year_month", "year_month_day"]
        option_menu = tk.OptionMenu(org_frame, self.organize_var, *org_options)
        option_menu.configure(font=('SF Pro Display', 12),
                            bg=self.colors['input_bg'],
                            fg=self.colors['input_fg'],
                            activebackground=self.colors['button_active_bg'],
                            activeforeground=self.colors['button_fg'],
                            highlightthickness=1,
                            highlightbackground=self.colors['border'])
        option_menu["menu"].configure(bg=self.colors['input_bg'], 
                                    fg=self.colors['input_fg'])
        option_menu.pack(side='left', padx=5)
        
        # Checkboxes with improved visibility
        self.copy_var = tk.BooleanVar()
        tk.Checkbutton(options_frame,
                      text="Copy files instead of moving",
                      variable=self.copy_var,
                      font=('SF Pro Display', 12),
                      bg=self.colors['frame_bg'],
                      fg=self.colors['fg'],
                      selectcolor=self.colors['checkbox_bg'],
                      activebackground=self.colors['frame_bg'],
                      activeforeground=self.colors['fg']).pack(anchor='w', pady=5)
        
        self.dry_run_var = tk.BooleanVar()
        tk.Checkbutton(options_frame,
                      text="Dry run (preview changes)",
                      variable=self.dry_run_var,
                      font=('SF Pro Display', 12),
                      bg=self.colors['frame_bg'],
                      fg=self.colors['fg'],
                      selectcolor=self.colors['checkbox_bg'],
                      activebackground=self.colors['frame_bg'],
                      activeforeground=self.colors['fg']).pack(anchor='w')
        
        # Progress section
        progress_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        progress_frame.pack(fill='x', pady=10)
        
        self.progress_var = tk.DoubleVar()
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       troughcolor=self.colors['progress_bg'],
                       background=self.colors['progress_bar'],
                       thickness=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          mode='determinate',
                                          style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill='x')
        
        # Status text with improved visibility
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(fill='both', expand=True, pady=10)
        
        # Add scrollbar to status text
        scrollbar = tk.Scrollbar(status_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.status_text = tk.Text(status_frame,
                                 height=15,
                                 font=('SF Pro Display', 12),
                                 bg=self.colors['input_bg'],
                                 fg=self.colors['input_fg'],
                                 insertbackground=self.colors['input_fg'],
                                 relief='solid',
                                 borderwidth=1,
                                 padx=10,
                                 pady=10,
                                 yscrollcommand=scrollbar.set)
        self.status_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.status_text.yview)
        
        # Control buttons with improved styling
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        self.start_button = tk.Button(button_frame,
                                    text="Start Organization",
                                    command=self.start_organization,
                                    font=('SF Pro Display', 12, 'bold'),
                                    bg=self.colors['primary_button_bg'],
                                    fg=self.colors['button_fg'],
                                    activebackground=self.colors['primary_button_active_bg'],
                                    activeforeground=self.colors['button_fg'],
                                    relief='flat',
                                    padx=15,
                                    pady=5)
        self.start_button.pack(side='left', padx=5)
        
        tk.Button(button_frame,
                 text="Clear Log",
                 command=self.clear_log,
                 font=('SF Pro Display', 12),
                 bg=self.colors['button_bg'],
                 fg=self.colors['button_fg'],
                 activebackground=self.colors['button_active_bg'],
                 activeforeground=self.colors['button_fg'],
                 relief='flat',
                 padx=15,
                 pady=5).pack(side='left')
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_queue)

    def get_color_scheme(self):
        if self.is_dark_mode:
            return {
                'bg': '#333333',
                'fg': '#FFFFFF',
                'frame_bg': '#222222',
                'input_bg': '#222222',
                'input_fg': '#FFFFFF',
                'border': '#666666',
                'button_bg': '#666666',
                'button_fg': '#FFFFFF',
                'button_active_bg': '#888888',
                'primary_button_bg': '#0078D4',
                'primary_button_active_bg': '#106EBE',
                'checkbox_bg': '#444444',
                'progress_bg': '#222222',
                'progress_bar': '#0078D4'
            }
        else:
            return {
                'bg': '#F0F0F0',
                'fg': '#000000',
                'frame_bg': '#FFFFFF',
                'input_bg': '#FFFFFF',
                'input_fg': '#000000',
                'border': '#CCCCCC',
                'button_bg': '#E1E1E1',
                'button_fg': '#000000',
                'button_active_bg': '#D1D1D1',
                'primary_button_bg': '#0078D4',
                'primary_button_active_bg': '#106EBE',
                'checkbox_bg': '#FFFFFF',
                'progress_bg': '#E1E1E1',
                'progress_bar': '#0078D4'
            }

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def clear_log(self):
        self.status_text.delete(1.0, tk.END)
        self.progress_var.set(0)

    def log_message(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)

    def check_queue(self):
        try:
            while True:
                message, progress = self.message_queue.get_nowait()
                self.log_message(message)
                if progress is not None:
                    self.progress_var.set(progress)
                self.message_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def start_organization(self):
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory first!")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Selected directory does not exist!")
            return
        
        self.start_button["state"] = "disabled"
        self.progress_var.set(0)
        
        thread = Thread(target=self.process_files,
                       args=(directory,
                             self.organize_var.get(),
                             self.copy_var.get(),
                             self.dry_run_var.get()))
        thread.daemon = True
        thread.start()

    def process_files(self, directory, organize_by, copy, dry_run):
        try:
            files = list(Path(directory).rglob('*'))
            files = [f for f in files if f.is_file()]
            total_files = len(files)
            processed = 0
            
            stats = {'moved': 0, 'skipped': 0, 'errors': 0}
            
            for file_path in files:
                try:
                    if file_path.name.startswith('.'):
                        stats['skipped'] += 1
                        continue

                    creation_date = get_creation_date(str(file_path))
                    dest_path = get_destination_path(str(file_path), directory,
                                                   creation_date, organize_by)

                    if dest_path.exists():
                        dest_path = handle_duplicate(dest_path)

                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    action = "Would move" if dry_run else "Moving"
                    message = f"{action} '{file_path}' to '{dest_path}'"
                    self.message_queue.put((message, (processed / total_files) * 100))

                    if not dry_run:
                        if copy:
                            shutil.copy2(file_path, dest_path)
                        else:
                            shutil.move(file_path, dest_path)
                        stats['moved'] += 1

                except Exception as e:
                    error_msg = f"Error processing {file_path}: {e}"
                    self.message_queue.put((error_msg, None))
                    stats['errors'] += 1

                processed += 1

            summary = "\nOperation completed:\n"
            summary += f"Files processed: {stats['moved']}\n"
            summary += f"Files skipped: {stats['skipped']}\n"
            summary += f"Errors encountered: {stats['errors']}"
            self.message_queue.put((summary, 100))

        except Exception as e:
            self.message_queue.put((f"An error occurred: {e}", None))
        finally:
            self.root.after(0, lambda: setattr(self.start_button, 'state', 'normal'))

def get_creation_date(file_path):
    """Extract creation date from file metadata."""
    try:
        if any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.arw', '.dng', '.heic', '.raw']):
            try:
                img = Image.open(file_path)
                if 'exif' in img.info:
                    exif_dict = piexif.load(img.info['exif'])
                    if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except Exception as e:
                logging.warning(f"Could not read EXIF data from {file_path}: {e}")

        if any(file_path.lower().endswith(ext) for ext in ['.mov', '.mp4', '.avi', '.mkv', '.wmv']):
            try:
                parser = createParser(file_path)
                if parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has('creation_date'):
                        return metadata.get('creation_date')
            except Exception as e:
                logging.warning(f"Could not read video metadata from {file_path}: {e}")

        return datetime.fromtimestamp(os.path.getmtime(file_path))
    except Exception as e:
        logging.error(f"Error getting creation date for {file_path}: {e}")
        return datetime.fromtimestamp(os.path.getmtime(file_path))

def get_destination_path(file_path, base_dir, creation_date, organize_by='date'):
    """Determine the destination path for a file."""
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    if file_ext in ['.mov', '.mp4', '.avi', '.mkv', '.wmv']:
        category = 'videos'
    elif file_ext in ['.jpg', '.jpeg', '.png', '.arw', '.dng', '.heic', '.raw']:
        category = 'photos'
    else:
        category = 'others'

    if organize_by == 'date':
        date_path = creation_date.strftime('%Y-%m-%d')
    elif organize_by == 'year_month':
        date_path = creation_date.strftime('%Y/%m')
    else:  # year_month_day
        date_path = creation_date.strftime('%Y/%m/%d')

    return Path(base_dir) / date_path / category / file_name

def handle_duplicate(dest_path, counter=1):
    """Handle duplicate filenames by adding a counter."""
    while dest_path.exists():
        base_name = dest_path.stem
        if ' (' in base_name:
            base_name = base_name.rsplit(' (', 1)[0]
        new_name = f"{base_name} ({counter}){dest_path.suffix}"
        dest_path = dest_path.parent / new_name
        counter += 1
    return dest_path

if __name__ == '__main__':
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop() 