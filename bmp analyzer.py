import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import struct
import os
import io
import random
import json
from typing import List, Tuple, Dict, Set
from PIL import Image, ImageTk

class BMPAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("BMP Binary Analyzer")
        self.root.geometry("1400x900")
        
        self.binary_data = None
        self.file_path = None
        self.preview_image = None
        self.preview_photo = None
        self.display_img_width = 0
        self.display_img_height = 0
        self.replaced_byte_positions = []  # List of positions where bytes were replaced
        
        # Color scheme for different sections
        self.colors = {
            'header': '#FFE6E6',      # Light red - BMP Header
            'dib_header': '#E6F3FF',  # Light blue - DIB Header
            'color_palette': '#E6FFE6', # Light green - Color Palette
            'pixel_data': '#FFF9E6',  # Light yellow - Pixel Data
            'padding': '#F0F0F0',     # Light gray - Padding
            'end_marker': '#FFE6F3',  # Light pink - End marker
            'replaced': '#FFB6C1'     # Light pink - Replaced bytes (steganography)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel for controls and legend
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # File operations
        file_frame = ttk.LabelFrame(left_panel, text="File Operations", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Load BMP File", command=self.load_bmp).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Preview Binary Data", command=self.preview_binary_data).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Export Binary to Image", command=self.export_binary).pack(fill=tk.X, pady=2)
        
        # File info
        self.info_label = ttk.Label(file_frame, text="No file loaded", wraplength=200)
        self.info_label.pack(pady=5)
        
        # Steganography section
        stego_frame = ttk.LabelFrame(left_panel, text="Steganography", padding="10")
        stego_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input string
        ttk.Label(stego_frame, text="Enter string to hide:").pack(anchor=tk.W, pady=(0, 2))
        self.input_text = tk.Text(stego_frame, height=3, wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(stego_frame, text="Embed String in Pixel Data", command=self.embed_string).pack(fill=tk.X, pady=2)
        
        # ADR file operations
        ttk.Button(stego_frame, text="Save Positions to ADR File", command=self.save_adr_file).pack(fill=tk.X, pady=2)
        ttk.Button(stego_frame, text="Load ADR File and Extract", command=self.load_adr_and_extract).pack(fill=tk.X, pady=2)
        
        # Extracted string output
        ttk.Label(stego_frame, text="Extracted string:").pack(anchor=tk.W, pady=(5, 2))
        self.output_text = scrolledtext.ScrolledText(stego_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.X, pady=(0, 5))
        
        # Legend
        legend_frame = ttk.LabelFrame(left_panel, text="Color Legend", padding="10")
        legend_frame.pack(fill=tk.BOTH, expand=True)
        
        legend_items = [
            ('BMP Header', 'header'),
            ('DIB Header', 'dib_header'),
            ('Color Palette', 'color_palette'),
            ('Pixel Data', 'pixel_data'),
            ('Padding', 'padding'),
            ('End Marker', 'end_marker'),
            ('Replaced Bytes', 'replaced')
        ]
        
        for label, key in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            color_box = tk.Label(item_frame, bg=self.colors[key], width=3, height=1, relief=tk.SOLID, borderwidth=1)
            color_box.pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(item_frame, text=label).pack(side=tk.LEFT)
        
        # Right panel for preview and binary display
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Image preview
        preview_frame = ttk.LabelFrame(right_panel, text="Image Preview", padding="10")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Canvas for image preview with scrollbars
        preview_canvas_frame = ttk.Frame(preview_frame)
        preview_canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_canvas_frame.columnconfigure(0, weight=1)
        preview_canvas_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas = tk.Canvas(
            preview_canvas_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        preview_v_scroll = ttk.Scrollbar(preview_canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        preview_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_canvas.configure(yscrollcommand=preview_v_scroll.set)
        
        preview_h_scroll = ttk.Scrollbar(preview_canvas_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        preview_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.preview_canvas.configure(xscrollcommand=preview_h_scroll.set)
        
        # Bind canvas resize to update preview
        self.preview_canvas.bind('<Configure>', self.on_preview_canvas_resize)
        
        # Preview info label
        self.preview_info_label = ttk.Label(preview_frame, text="No image loaded", anchor=tk.CENTER)
        self.preview_info_label.grid(row=1, column=0, pady=(5, 0))
        
        # Binary display
        display_frame = ttk.LabelFrame(right_panel, text="Binary Data", padding="10")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(display_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.NONE,
            font=('Courier', 10),
            bg='white',
            fg='black'
        )
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def load_bmp(self):
        file_path = filedialog.askopenfilename(
            title="Select BMP File",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                self.binary_data = f.read()
            
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.info_label.config(text=f"File: {filename}\nSize: {len(self.binary_data)} bytes")
            self.replaced_byte_positions = []  # Reset replaced positions
            self.analyze_and_display()
            self.update_preview()
            self.status_label.config(text=f"Loaded: {len(self.binary_data)} bytes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def parse_bmp_structure(self) -> List[Tuple[int, int, str]]:
        """Parse BMP file and return list of (start, end, section_type) tuples"""
        if not self.binary_data or len(self.binary_data) < 14:
            return []
        
        sections = []
        
        # BMP Header (14 bytes)
        bmp_header_size = 14
        sections.append((0, bmp_header_size, 'header'))
        
        if len(self.binary_data) < bmp_header_size:
            return sections
        
        # Get DIB header size (at offset 14)
        dib_header_size = struct.unpack('<I', self.binary_data[14:18])[0]
        dib_header_end = 14 + dib_header_size
        sections.append((14, dib_header_end, 'dib_header'))
        
        if len(self.binary_data) < dib_header_end:
            return sections
        
        # Get pixel data offset (at offset 10 in BMP header)
        pixel_data_offset = struct.unpack('<I', self.binary_data[10:14])[0]
        
        # Check if there's a color palette
        # Color palette exists if pixel_data_offset > dib_header_end
        if pixel_data_offset > dib_header_end:
            palette_size = pixel_data_offset - dib_header_end
            sections.append((dib_header_end, pixel_data_offset, 'color_palette'))
        
        # Get image dimensions from DIB header to calculate row padding
        # For BITMAPINFOHEADER (40 bytes), width and height are at offsets 4 and 8
        if dib_header_size >= 40:
            width = struct.unpack('<i', self.binary_data[18:22])[0]
            height = struct.unpack('<i', self.binary_data[22:26])[0]
            bits_per_pixel = struct.unpack('<H', self.binary_data[28:30])[0]
            
            # Calculate row size (with padding to 4-byte boundary)
            row_size = ((width * bits_per_pixel + 31) // 32) * 4
            pixel_data_size = abs(height) * row_size
            
            file_size = len(self.binary_data)
            pixel_data_end = min(pixel_data_offset + pixel_data_size, file_size)
            
            # Pixel data
            if pixel_data_offset < file_size:
                sections.append((pixel_data_offset, pixel_data_end, 'pixel_data'))
            
            # Check for padding/extra data after pixel data
            if pixel_data_end < file_size:
                # Check if there's a recognizable end marker or just padding
                remaining = self.binary_data[pixel_data_end:]
                if len(remaining) <= 4 and all(b == 0 for b in remaining):
                    sections.append((pixel_data_end, file_size, 'padding'))
                else:
                    sections.append((pixel_data_end, file_size, 'end_marker'))
        else:
            # Fallback: treat everything after pixel_data_offset as pixel data
            file_size = len(self.binary_data)
            if pixel_data_offset < file_size:
                sections.append((pixel_data_offset, file_size, 'pixel_data'))
        
        return sections
    
    def format_binary_data(self, data: bytes) -> str:
        """Format binary data as hex string with addresses"""
        lines = []
        bytes_per_line = 16
        
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i+bytes_per_line]
            hex_str = ' '.join(f'{b:02X}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:08X}  {hex_str:<48}  {ascii_str}")
        
        return '\n'.join(lines)
    
    def analyze_and_display(self):
        """Analyze BMP structure and display with highlighting"""
        if not self.binary_data:
            return
        
        self.text_widget.delete(1.0, tk.END)
        
        # Format binary data
        formatted_text = self.format_binary_data(self.binary_data)
        self.text_widget.insert(1.0, formatted_text)
        
        # Parse structure
        sections = self.parse_bmp_structure()
        
        # Apply highlighting by line segments for better performance
        bytes_per_line = 16
        for start, end, section_type in sections:
            start_line = start // bytes_per_line + 1
            end_line = (end - 1) // bytes_per_line + 1
            
            for line_num in range(start_line, end_line + 1):
                # Calculate which bytes in this line belong to this section
                line_start_byte = (line_num - 1) * bytes_per_line
                line_end_byte = line_start_byte + bytes_per_line
                
                # Determine the actual byte range for this section on this line
                section_start_on_line = max(start, line_start_byte)
                section_end_on_line = min(end, line_end_byte)
                
                if section_start_on_line < section_end_on_line:
                    # Calculate column positions for hex portion
                    start_col = 10 + ((section_start_on_line - line_start_byte) * 3)
                    end_col = 10 + ((section_end_on_line - line_start_byte) * 3)
                    
                    # Highlight the hex portion
                    tag_name = f"{section_type}_{line_num}"
                    self.text_widget.tag_add(tag_name, f"{line_num}.{start_col}", f"{line_num}.{end_col}")
                    self.text_widget.tag_config(tag_name, background=self.colors[section_type])
        
        # Highlight replaced bytes (steganography)
        if self.replaced_byte_positions:
            for byte_pos in self.replaced_byte_positions:
                if 0 <= byte_pos < len(self.binary_data):
                    line_num = byte_pos // bytes_per_line + 1
                    byte_in_line = byte_pos % bytes_per_line
                    col_start = 10 + (byte_in_line * 3)
                    col_end = col_start + 2
                    
                    tag_name = f"replaced_{byte_pos}"
                    self.text_widget.tag_add(tag_name, f"{line_num}.{col_start}", f"{line_num}.{col_end}")
                    self.text_widget.tag_config(tag_name, background=self.colors['replaced'])
    
    def export_binary(self):
        """Export binary data from text box back to image file"""
        if not self.binary_data:
            messagebox.showwarning("Warning", "No binary data loaded. Please load a BMP file first.")
            return
        
        # Extract binary data from text box
        extracted_bytes = self.extract_binary_from_text()
        
        if not extracted_bytes:
            messagebox.showerror("Error", "Could not extract binary data from text.")
            return
        
        # Save to file
        output_path = filedialog.asksaveasfilename(
            title="Save Binary as BMP",
            defaultextension=".bmp",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        try:
            with open(output_path, 'wb') as f:
                f.write(extracted_bytes)
            
            messagebox.showinfo("Success", f"Binary data exported to:\n{output_path}")
            self.status_label.config(text=f"Exported: {len(extracted_bytes)} bytes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {str(e)}")
    
    def extract_binary_from_text(self) -> bytes:
        """Extract binary data from the text widget"""
        # Get text from widget
        text_content = self.text_widget.get(1.0, tk.END)
        
        # Extract hex bytes from text
        # Format: "XXXXXXXX  XX XX XX ...  ASCII"
        extracted_bytes = []
        
        for line in text_content.split('\n'):
            if not line.strip():
                continue
            
            # Extract hex portion (between address and ASCII)
            parts = line.split('  ')
            if len(parts) >= 2:
                hex_part = parts[1].strip()
                # Parse hex bytes
                hex_bytes = hex_part.split()
                for hex_byte in hex_bytes:
                    try:
                        byte_val = int(hex_byte, 16)
                        extracted_bytes.append(byte_val)
                    except ValueError:
                        continue
        
        return bytes(extracted_bytes)
    
    def preview_binary_data(self):
        """Preview the image from binary data in the text box"""
        try:
            # Extract binary data from text box
            binary_data = self.extract_binary_from_text()
            
            if not binary_data:
                messagebox.showwarning("Warning", "No binary data found in text box. Please load a BMP file first.")
                return
            
            # Try to load image from binary data
            try:
                img = Image.open(io.BytesIO(binary_data))
                self.preview_image = img.copy()
                
                # Get image dimensions
                width, height = img.size
                
                # Calculate display size (max 400x300 to fit in preview panel)
                max_display_width = 400
                max_display_height = 300
                
                # Maintain aspect ratio
                if width > max_display_width or height > max_display_height:
                    ratio = min(max_display_width / width, max_display_height / height)
                    display_width = int(width * ratio)
                    display_height = int(height * ratio)
                else:
                    display_width = width
                    display_height = height
                
                # Store display dimensions
                self.display_img_width = display_width
                self.display_img_height = display_height
                
                # Resize image for display
                # Use LANCZOS resampling (compatible with both old and new Pillow versions)
                try:
                    # New Pillow versions
                    display_img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Older Pillow versions
                    display_img = img.resize((display_width, display_height), Image.LANCZOS)
                
                # Convert to PhotoImage for tkinter
                self.preview_photo = ImageTk.PhotoImage(display_img)
                
                # Draw the image
                self.draw_preview_image()
                
                # Update info label
                self.preview_info_label.config(
                    text=f"Preview (from binary): {width} × {height} pixels | "
                         f"Display: {display_width} × {display_height} | "
                         f"Mode: {img.mode} | Size: {len(binary_data)} bytes"
                )
                
                self.status_label.config(text=f"Preview updated: {len(binary_data)} bytes")
                
            except Exception as e:
                messagebox.showerror("Preview Error", 
                    f"Could not preview image from binary data.\n\n"
                    f"Error: {str(e)}\n\n"
                    f"The binary data may be corrupted or invalid.\n"
                    f"Make sure the binary data represents a valid BMP file.")
                self.preview_canvas.delete("all")
                self.preview_info_label.config(text=f"Preview error: Invalid or corrupted binary data")
                self.preview_photo = None
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract binary data: {str(e)}")
    
    def on_preview_canvas_resize(self, event=None):
        """Handle canvas resize to recenter image"""
        if self.preview_photo:
            self.draw_preview_image()
    
    def draw_preview_image(self):
        """Draw the preview image on the canvas"""
        if not self.preview_photo:
            return
        
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Get canvas size
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, schedule update
            self.root.after(100, self.draw_preview_image)
            return
        
        # Center the image
        x = (canvas_width - self.display_img_width) // 2
        y = (canvas_height - self.display_img_height) // 2
        
        # Ensure image is within canvas bounds
        x = max(0, x)
        y = max(0, y)
        
        # Set scroll region to allow scrolling if image is larger than canvas
        self.preview_canvas.config(scrollregion=(0, 0, max(canvas_width, self.display_img_width), 
                                                  max(canvas_height, self.display_img_height)))
        
        # Draw image
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
    
    def update_preview(self):
        """Update the image preview panel"""
        if not self.file_path:
            self.preview_canvas.delete("all")
            self.preview_info_label.config(text="No image loaded")
            self.preview_photo = None
            return
        
        try:
            # Load image using PIL
            img = Image.open(self.file_path)
            self.preview_image = img.copy()
            
            # Get image dimensions
            width, height = img.size
            
            # Calculate display size (max 400x300 to fit in preview panel)
            max_display_width = 400
            max_display_height = 300
            
            # Maintain aspect ratio
            if width > max_display_width or height > max_display_height:
                ratio = min(max_display_width / width, max_display_height / height)
                display_width = int(width * ratio)
                display_height = int(height * ratio)
            else:
                display_width = width
                display_height = height
            
            # Store display dimensions
            self.display_img_width = display_width
            self.display_img_height = display_height
            
            # Resize image for display
            # Use LANCZOS resampling (compatible with both old and new Pillow versions)
            try:
                # New Pillow versions
                display_img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            except AttributeError:
                # Older Pillow versions
                display_img = img.resize((display_width, display_height), Image.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.preview_photo = ImageTk.PhotoImage(display_img)
            
            # Draw the image
            self.draw_preview_image()
            
            # Update info label
            self.preview_info_label.config(
                text=f"Dimensions: {width} × {height} pixels | "
                     f"Display: {display_width} × {display_height} | "
                     f"Mode: {img.mode}"
            )
            
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_info_label.config(text=f"Preview error: {str(e)}")
            self.preview_photo = None
            messagebox.showwarning("Preview Warning", f"Could not display image preview: {str(e)}")
    
    def get_pixel_data_range(self) -> Tuple[int, int]:
        """Get the start and end positions of pixel data section"""
        if not self.binary_data or len(self.binary_data) < 14:
            return None, None
        
        # Get pixel data offset (at offset 10 in BMP header)
        pixel_data_offset = struct.unpack('<I', self.binary_data[10:14])[0]
        
        # Get DIB header size
        dib_header_size = struct.unpack('<I', self.binary_data[14:18])[0]
        
        # Calculate pixel data size
        if dib_header_size >= 40:
            width = struct.unpack('<i', self.binary_data[18:22])[0]
            height = struct.unpack('<i', self.binary_data[22:26])[0]
            bits_per_pixel = struct.unpack('<H', self.binary_data[28:30])[0]
            
            # Calculate row size (with padding to 4-byte boundary)
            row_size = ((width * bits_per_pixel + 31) // 32) * 4
            pixel_data_size = abs(height) * row_size
            
            file_size = len(self.binary_data)
            pixel_data_end = min(pixel_data_offset + pixel_data_size, file_size)
            
            return pixel_data_offset, pixel_data_end
        
        return pixel_data_offset, len(self.binary_data)
    
    def embed_string(self):
        """Embed a string into the pixel data by replacing random bytes"""
        if not self.binary_data:
            messagebox.showwarning("Warning", "No binary data loaded. Please load a BMP file first.")
            return
        
        # Get input string
        input_string = self.input_text.get(1.0, tk.END).strip()
        if not input_string:
            messagebox.showwarning("Warning", "Please enter a string to embed.")
            return
        
        # Convert string to bytes
        try:
            string_bytes = input_string.encode('utf-8')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encode string: {str(e)}")
            return
        
        # Get pixel data range
        pixel_start, pixel_end = self.get_pixel_data_range()
        if pixel_start is None or pixel_end is None:
            messagebox.showerror("Error", "Could not determine pixel data range.")
            return
        
        pixel_data_size = pixel_end - pixel_start
        if pixel_data_size < len(string_bytes):
            messagebox.showerror("Error", 
                f"String is too long ({len(string_bytes)} bytes). "
                f"Pixel data only has {pixel_data_size} bytes available.")
            return
        
        # Convert binary_data to bytearray for modification
        data_array = bytearray(self.binary_data)
        
        # Generate random positions within pixel data
        available_positions = list(range(pixel_start, pixel_end))
        random.shuffle(available_positions)
        
        # Store positions and replace bytes in order (preserve character order)
        self.replaced_byte_positions = []
        for i, byte_val in enumerate(string_bytes):
            pos = available_positions[i]
            self.replaced_byte_positions.append(pos)  # Keep in order, don't sort
            data_array[pos] = byte_val
        
        # Update binary data
        self.binary_data = bytes(data_array)
        
        # Update display
        self.analyze_and_display()
        
        # Update status
        self.status_label.config(
            text=f"Embedded {len(string_bytes)} bytes at {len(self.replaced_byte_positions)} positions in pixel data"
        )
        
        messagebox.showinfo("Success", 
            f"Successfully embedded {len(string_bytes)} bytes into pixel data.\n"
            f"Positions: {len(self.replaced_byte_positions)} bytes replaced.")
    
    def save_adr_file(self):
        """Save the positions of replaced bytes to an ADR file"""
        if not self.replaced_byte_positions:
            messagebox.showwarning("Warning", "No replaced bytes to save. Please embed a string first.")
            return
        
        if not self.file_path:
            messagebox.showwarning("Warning", "No file loaded. Cannot determine output filename.")
            return
        
        # Generate ADR filename: photo_name.adr
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        default_filename = f"{base_name}.adr"
        default_dir = os.path.dirname(self.file_path) if os.path.dirname(self.file_path) else "."
        
        output_path = filedialog.asksaveasfilename(
            title="Save ADR File",
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=".adr",
            filetypes=[("ADR files", "*.adr"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        try:
            # Save positions as JSON
            adr_data = {
                'positions': self.replaced_byte_positions,
                'count': len(self.replaced_byte_positions)
            }
            
            with open(output_path, 'w') as f:
                json.dump(adr_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Saved {len(self.replaced_byte_positions)} positions to:\n{output_path}")
            self.status_label.config(text=f"Saved ADR file: {len(self.replaced_byte_positions)} positions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ADR file: {str(e)}")
    
    def load_adr_and_extract(self):
        """Load ADR file and extract the hidden string from binary data"""
        if not self.binary_data:
            messagebox.showwarning("Warning", "No binary data loaded. Please load a BMP file first.")
            return
        
        # Load ADR file
        adr_path = filedialog.askopenfilename(
            title="Load ADR File",
            filetypes=[("ADR files", "*.adr"), ("All files", "*.*")]
        )
        
        if not adr_path:
            return
        
        try:
            with open(adr_path, 'r') as f:
                adr_data = json.load(f)
            
            positions = adr_data.get('positions', [])
            if not positions:
                messagebox.showerror("Error", "ADR file does not contain valid positions.")
                return
            
            # Extract bytes from positions in order (preserves character order)
            extracted_bytes = []
            for pos in positions:
                if 0 <= pos < len(self.binary_data):
                    extracted_bytes.append(self.binary_data[pos])
                else:
                    messagebox.showwarning("Warning", 
                        f"Position {pos} is out of range. Some data may be missing.")
            
            # Convert bytes to string
            try:
                extracted_string = bytes(extracted_bytes).decode('utf-8')
            except UnicodeDecodeError as e:
                messagebox.showerror("Error", 
                    f"Failed to decode extracted bytes as UTF-8: {str(e)}\n"
                    f"Extracted {len(extracted_bytes)} bytes.")
                return
            
            # Display in output text box
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, extracted_string)
            self.output_text.config(state=tk.DISABLED)
            
            # Update replaced positions for highlighting
            self.replaced_byte_positions = positions
            self.analyze_and_display()
            
            self.status_label.config(
                text=f"Extracted {len(extracted_string)} characters from {len(positions)} positions"
            )
            
            messagebox.showinfo("Success", 
                f"Successfully extracted string from {len(positions)} positions.\n"
                f"Length: {len(extracted_string)} characters")
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid ADR file format. Expected JSON.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ADR file: {str(e)}")

def main():
    root = tk.Tk()
    app = BMPAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

