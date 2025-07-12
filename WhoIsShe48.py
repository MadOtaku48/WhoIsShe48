#!/usr/bin/env python3
"""
WhoIsShe48
48그룹 멤버들의 얼굴을 인식하고 이름을 표시하는 앱
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pickle
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import glob
from pathlib import Path

class WhoIsShe48:
    def __init__(self, root):
        self.root = root
        self.root.title("WhoIsShe48 - 48 Group Face Recognition")
        self.root.geometry("1200x900")
        
        # Initialize InsightFace
        try:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self.insightface_available = True
        except Exception as e:
            self.insightface_available = False
            messagebox.showerror("InsightFace Error", f"Failed to initialize InsightFace:\n{str(e)}")
        
        # Data
        self.known_face_embeddings = defaultdict(list)
        self.known_face_names = []
        self.current_image = None
        self.labeled_image = None
        self.confidence_threshold = tk.DoubleVar(value=0.45)
        self.show_confidence = tk.BooleanVar(value=True)
        self.font_size = tk.IntVar(value=30)  # Initialize font size variable
        self.current_group = None
        self.members_data = []  # Store full member data
        
        # Color mappings
        self.color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "green": (0, 255, 0),
            "yellow": (255, 255, 0),
            "pink": (255, 105, 180),
            "none": None
        }
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Select group button
        ttk.Button(control_frame, text="Select Group", command=self.select_group).pack(side=tk.LEFT, padx=5)
        
        # Group label
        self.group_label = ttk.Label(control_frame, text="No model loaded")
        self.group_label.pack(side=tk.LEFT, padx=10)
        
        # Select image button
        ttk.Button(control_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT, padx=5)
        
        # Process button
        self.process_button = ttk.Button(control_frame, text="Detect Faces", command=self.process_image, state=tk.DISABLED)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_button = ttk.Button(control_frame, text="Save Labeled Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Confidence threshold
        threshold_frame = ttk.Frame(options_frame)
        threshold_frame.pack(fill=tk.X)
        
        ttk.Label(threshold_frame, text="Confidence Threshold:").pack(side=tk.LEFT, padx=5)
        
        self.threshold_slider = ttk.Scale(
            threshold_frame,
            from_=0.2,
            to=0.8,
            orient=tk.HORIZONTAL,
            variable=self.confidence_threshold,
            length=200,
            command=self.update_threshold_label
        )
        self.threshold_slider.pack(side=tk.LEFT, padx=5)
        
        self.threshold_label = ttk.Label(threshold_frame, text="45%")
        self.threshold_label.pack(side=tk.LEFT, padx=5)
        
        # Show confidence checkbox
        ttk.Checkbutton(options_frame, text="Show confidence scores", variable=self.show_confidence).pack(anchor=tk.W, pady=5)
        
        # Font size adjustment
        font_frame = ttk.Frame(options_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT, padx=5)
        
        self.font_slider = ttk.Scale(
            font_frame,
            from_=15,
            to=60,
            orient=tk.HORIZONTAL,
            variable=self.font_size,
            length=200,
            command=self.update_font_label
        )
        self.font_slider.pack(side=tk.LEFT, padx=5)
        
        self.font_label = ttk.Label(font_frame, text="30")
        self.font_label.pack(side=tk.LEFT, padx=5)
        
        # Language selection (multiple languages can be selected)
        language_frame = ttk.LabelFrame(options_frame, text="Display Languages", padding="5")
        language_frame.pack(fill=tk.X, pady=5)
        
        self.show_japanese = tk.BooleanVar(value=True)
        self.show_korean = tk.BooleanVar(value=False)
        self.show_english = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(language_frame, text="日本語", variable=self.show_japanese).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(language_frame, text="한국어", variable=self.show_korean).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(language_frame, text="English", variable=self.show_english).pack(side=tk.LEFT, padx=5)
        
        # Text Style Options
        style_frame = ttk.LabelFrame(options_frame, text="Text Style", padding="5")
        style_frame.pack(fill=tk.X, pady=5)
        
        # Text position
        position_frame = ttk.Frame(style_frame)
        position_frame.pack(fill=tk.X, pady=2)
        ttk.Label(position_frame, text="Position:").pack(side=tk.LEFT, padx=5)
        
        self.text_position = tk.StringVar(value="above")
        positions = [
            ("Above", "above"),
            ("Below", "below"),
            ("Left", "left"),
            ("Right", "right")
        ]
        for label, value in positions:
            ttk.Radiobutton(position_frame, text=label, variable=self.text_position, 
                          value=value).pack(side=tk.LEFT, padx=3)
        
        # Text color
        color_frame = ttk.Frame(style_frame)
        color_frame.pack(fill=tk.X, pady=2)
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT, padx=5)
        
        self.text_color_var = tk.StringVar(value="White")
        colors = [
            ("White", "white"),
            ("Black", "black"),
            ("Red", "red"),
            ("Blue", "blue"),
            ("Green", "green"),
            ("Yellow", "yellow"),
            ("Pink", "pink")
        ]
        
        self.color_menu = ttk.Combobox(color_frame, textvariable=self.text_color_var, 
                                      values=[c[0] for c in colors], state="readonly", width=10)
        self.color_menu.pack(side=tk.LEFT, padx=5)
        
        # Outline color
        ttk.Label(color_frame, text="Outline:").pack(side=tk.LEFT, padx=5)
        self.outline_color_var = tk.StringVar(value="Pink")
        
        self.outline_menu = ttk.Combobox(color_frame, textvariable=self.outline_color_var, 
                                        values=[c[0] for c in colors] + ["None"], state="readonly", width=10)
        self.outline_menu.pack(side=tk.LEFT, padx=5)
        
        # Image display area
        image_frame = ttk.LabelFrame(main_frame, text="Image", padding="10")
        image_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Zoom controls - pack first so they appear at the top
        zoom_frame = ttk.Frame(image_frame)
        zoom_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Create frame for canvas and scrollbars
        canvas_container = ttk.Frame(image_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars first
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for image with fixed size
        self.canvas = tk.Canvas(canvas_container, bg='gray', width=800, height=600,
                               yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar commands
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="Fit", command=self.zoom_fit, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="10%", command=lambda: self.zoom_to(0.1), width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="25%", command=lambda: self.zoom_to(0.25), width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="50%", command=lambda: self.zoom_to(0.5), width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="75%", command=lambda: self.zoom_to(0.75), width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="100%", command=self.zoom_100, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="150%", command=lambda: self.zoom_to(1.5), width=4).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%", width=10)
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        
        # Initialize zoom level
        self.zoom_level = 1.0
        self.current_display_image = None
        
        
        # Results text
        results_frame = ttk.LabelFrame(main_frame, text="Detection Results", padding="10")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Results text widget with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(text_frame, height=10, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.results_text.yview)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def update_threshold_label(self, value):
        threshold = float(value)
        self.threshold_label.config(text=f"{int(threshold * 100)}%")
    
    def update_font_label(self, value):
        font_size = int(float(value))
        self.font_label.config(text=str(font_size))
    
    def zoom_fit(self):
        """Fit image to canvas"""
        if self.current_display_image:
            self.zoom_level = self.calculate_fit_zoom()
            self.display_image(self.current_display_image)
    
    def zoom_100(self):
        """Reset zoom to 100%"""
        self.zoom_to(1.0)
    
    def zoom_to(self, level):
        """Zoom to specific level"""
        if self.current_display_image:
            self.zoom_level = level
            self.display_image(self.current_display_image)
    
    def calculate_fit_zoom(self):
        """Calculate zoom level to fit image in canvas"""
        if not self.current_display_image:
            return 1.0
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet displayed
            canvas_width = 800
            canvas_height = 600
        
        img_width, img_height = self.current_display_image.size
        
        # Calculate zoom to fit
        zoom_x = canvas_width / img_width
        zoom_y = canvas_height / img_height
        
        return min(zoom_x, zoom_y, 1.0)  # Don't zoom larger than 100% for fit
    
    
    def select_group(self):
        """Select a group and load the most recent model"""
        # Get base directory
        base_dir = Path("/Users/suknamgoong/face/akb48-face-classifier/Groups")
        
        # Find all available groups
        groups = []
        if base_dir.exists():
            for group_dir in base_dir.iterdir():
                if group_dir.is_dir() and not group_dir.name.startswith('.'):
                    # Check if this group has any model files
                    model_files = list(group_dir.glob("*_model_*.pkl"))
                    if model_files:
                        groups.append(group_dir.name)
        
        if not groups:
            messagebox.showerror("Error", "No groups with trained models found!")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Group")
        dialog.geometry("300x400")
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add label
        ttk.Label(dialog, text="Select a group:", padding="10").pack()
        
        # Create listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Add groups to listbox
        for group in sorted(groups):
            listbox.insert(tk.END, group)
        
        # Select first item by default
        if groups:
            listbox.selection_set(0)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_group = listbox.get(selection[0])
                dialog.destroy()
                self.load_group_model(selected_group)
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT)
        
        # Bind double-click
        listbox.bind('<Double-Button-1>', lambda e: on_select())
        
        # Focus the dialog
        dialog.focus()
    
    def load_group_model(self, group_name):
        """Load the most recent model for the selected group"""
        base_dir = Path("/Users/suknamgoong/face/akb48-face-classifier/Groups")
        group_dir = base_dir / group_name
        
        # Store the selected group name
        self.selected_group_name = group_name
        
        # Find all model files for this group
        model_files = list(group_dir.glob(f"{group_name.lower()}_model_*.pkl"))
        
        if not model_files:
            # Try alternative pattern
            model_files = list(group_dir.glob("*_model_*.pkl"))
        
        if not model_files:
            messagebox.showerror("Error", f"No model files found for {group_name}!")
            return
        
        # Sort by modification time and get the most recent
        model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        most_recent_model = model_files[0]
        
        # Load the model
        self.load_model_file(str(most_recent_model))
    
    def load_model_file(self, filename):
        """Load trained face embeddings from a file"""
        if not filename:
            return
        
        try:
            # Load from file
            with open(filename, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restore embeddings - handle both dict and array formats
            embeddings_data = model_data['embeddings']
            
            # Check if it's the new format (numpy array with separate names)
            if isinstance(embeddings_data, np.ndarray) and 'names' in model_data:
                # New format: convert array to dict
                self.known_face_embeddings = defaultdict(list)
                names = model_data['names']
                
                # embeddings_data is shape (n_members, 512) - one embedding per member
                for i, name in enumerate(names):
                    if i < len(embeddings_data):
                        # Get embedding for this member
                        member_embedding = embeddings_data[i]
                        # Store as list for compatibility
                        self.known_face_embeddings[name] = [member_embedding]
                
                self.known_face_names = names
            else:
                # Old format: embeddings is already a dict
                self.known_face_embeddings = defaultdict(list, embeddings_data)
                self.known_face_names = model_data.get('names', list(embeddings_data.keys()))
            
            # Get group info
            if 'group' in model_data:
                self.current_group = model_data['group']['name']
                # Use name as group_id if id is not present
                group_id = model_data['group'].get('id', model_data['group']['name'])
            else:
                # Use the selected group name if model doesn't contain group info
                if hasattr(self, 'selected_group_name'):
                    self.current_group = self.selected_group_name
                    group_id = self.selected_group_name
                else:
                    self.current_group = "Unknown"
                    group_id = ''
            
            # Load members data with multilingual names
            if group_id:
                members_data_path = os.path.join(
                    os.path.dirname(filename), 
                    'members_photos/members_data.json'
                )
                if os.path.exists(members_data_path):
                    with open(members_data_path, 'r', encoding='utf-8') as f:
                        self.members_data = json.load(f)
                        # Create lookup dictionary
                        self.members_lookup = {m['name']: m for m in self.members_data}
                        print(f"Loaded {len(self.members_data)} members with multilingual names")
                        
                        # Create a normalized name mapping for flexible matching
                        self.name_mapping = {}
                        for member in self.members_data:
                            name = member['name']
                            # Store original name
                            self.name_mapping[name] = name
                            # Store without spaces
                            self.name_mapping[name.replace(' ', '')] = name
                            # Store without spaces and with underscore
                            self.name_mapping[name.replace(' ', '_')] = name
                else:
                    print(f"Members data not found at: {members_data_path}")
                    self.members_data = []
                    self.members_lookup = {}
                    self.name_mapping = {}
            else:
                # Initialize empty if no group_id
                self.members_data = []
                self.members_lookup = {}
                self.name_mapping = {}
            
            member_count = model_data.get('member_count', len(self.known_face_names))
            
            self.group_label.config(text=f"{self.current_group}: {member_count} members")
            self.check_can_process()
            
            messagebox.showinfo("Success", 
                f"Model loaded successfully!\n\n"
                f"Group: {self.current_group}\n"
                f"Members: {member_count}\n"
                f"Model: {os.path.basename(filename)}")
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load model:\n{str(e)}")
    
    def select_image(self):
        """Select an image to process"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                # Load and display image
                self.current_image_path = filename
                self.current_image = Image.open(filename)
                
                # Set initial zoom to fit
                self.current_display_image = self.current_image
                self.zoom_level = self.calculate_fit_zoom()
                
                # Display on canvas
                self.display_image(self.current_image)
                
                self.check_can_process()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
    
    def display_image(self, image):
        """Display image on canvas with zoom support"""
        # Store the image for zoom operations
        self.current_display_image = image
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet displayed
            self.root.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        
        # Calculate new size based on zoom level
        img_width, img_height = image.size
        new_width = int(img_width * self.zoom_level)
        new_height = int(img_height * self.zoom_level)
        
        # Resize image
        if self.zoom_level != 1.0:
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            resized_image = image
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Configure scroll region
        self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        # Create image on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Store display ratio for later use (for backward compatibility)
        self.display_ratio = self.zoom_level
    
    def check_can_process(self):
        """Check if we can process an image"""
        can_process = (
            len(self.known_face_embeddings) > 0 and
            self.current_image is not None and
            self.insightface_available
        )
        self.process_button.config(state=tk.NORMAL if can_process else tk.DISABLED)
    
    def process_image(self):
        """Process the image and detect faces"""
        if not self.current_image or not self.insightface_available:
            return
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Processing...\n")
        self.root.update()
        
        try:
            # Convert PIL image to OpenCV format
            img_cv = cv2.cvtColor(np.array(self.current_image), cv2.COLOR_RGB2BGR)
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.app.get(img_rgb)
            
            if not faces:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "No faces detected in the image.")
                return
            
            # Create a copy for labeling
            labeled_img = self.current_image.copy()
            if labeled_img.mode != 'RGB':
                labeled_img = labeled_img.convert('RGB')
            draw = ImageDraw.Draw(labeled_img)
            
            
            # Get base font size from user setting
            base_font_size = self.font_size.get()
            
            # Font paths
            font_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJKkr-Regular.otf"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Regular.ttc"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJKkr-VF.ttf"),
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            
            # Clear results text
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Detected {len(faces)} face(s):\n\n")
            
            # Process each face
            face_results = []
            
            for face_idx, face in enumerate(faces):
                # Get face bounding box
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                
                
                # Get face embedding
                face_embedding = face.normed_embedding
                
                # Find best match
                best_match_name = "Unknown"
                best_confidence = 0
                
                for member_name in self.known_face_names:
                    if member_name in self.known_face_embeddings:
                        member_embeddings = self.known_face_embeddings[member_name]
                        
                        # Calculate similarities
                        similarities = []
                        for known_embedding in member_embeddings:
                            similarity = cosine_similarity(
                                face_embedding.reshape(1, -1),
                                known_embedding.reshape(1, -1)
                            )[0][0]
                            similarities.append(similarity)
                        
                        # Use the best match
                        max_similarity = max(similarities) if similarities else 0
                        
                        if max_similarity > best_confidence:
                            best_confidence = max_similarity
                            best_match_name = member_name
                
                # Check threshold
                threshold = self.confidence_threshold.get()
                if best_confidence < threshold:
                    continue  # Skip unknown faces
                
                # Get display names based on selected languages
                display_names = []
                if hasattr(self, 'members_lookup') and best_match_name in self.members_lookup:
                    member_data = self.members_lookup[best_match_name]
                    
                    
                    # Add names for each selected language
                    if self.show_japanese.get():
                        display_names.append(best_match_name)  # Japanese name is the default
                    
                    if self.show_korean.get() and 'name_ko' in member_data:
                        display_names.append(member_data['name_ko'])
                    
                    if self.show_english.get() and 'name_en' in member_data:
                        display_names.append(member_data['name_en'])
                
                # If no language selected or member not found, use default name
                if not display_names:
                    display_names = [best_match_name]
                
                # Calculate font size based on face size
                face_width = x2 - x1
                face_height = y2 - y1
                face_size = min(face_width, face_height)
                
                # Scale font size based on face size (face_size / 10 is a good ratio)
                scale_factor = face_size / 100  # Adjust divisor as needed
                adjusted_font_size = int(base_font_size * scale_factor)
                adjusted_font_size = max(12, min(adjusted_font_size, 200))  # Clamp between 12 and 200
                
                # Further adjust based on number of languages selected
                num_languages = len(display_names)
                if num_languages > 1:
                    adjusted_font_size = int(adjusted_font_size * 0.8)  # Reduce font size for multiple lines
                
                # Load font with adjusted size for this face
                adjusted_font = None
                for font_path in font_paths:
                    try:
                        if os.path.exists(font_path):
                            adjusted_font = ImageFont.truetype(font_path, adjusted_font_size)
                            break
                    except:
                        continue
                
                if adjusted_font is None:
                    try:
                        adjusted_font = ImageFont.truetype("Helvetica", adjusted_font_size)
                    except:
                        adjusted_font = ImageFont.load_default()
                
                # Calculate text position based on user preference
                line_height = adjusted_font_size + 10
                total_text_height = line_height * num_languages
                position = self.text_position.get()
                
                if position == "above":
                    text_x = (x1 + x2) // 2  # Center of face
                    text_y = y1 - 10 - total_text_height
                    # Make sure text doesn't go above image
                    if text_y < 10:
                        text_y = y2 + 10  # Place below face instead
                    anchor = "mt"  # middle-top
                elif position == "below":
                    text_x = (x1 + x2) // 2  # Center of face
                    text_y = y2 + 10
                    anchor = "mt"  # middle-top
                elif position == "left":
                    text_x = x1 - 10
                    text_y = (y1 + y2) // 2 - (total_text_height // 2)
                    anchor = "rt"  # right-top
                else:  # right
                    text_x = x2 + 10
                    text_y = (y1 + y2) // 2 - (total_text_height // 2)
                    anchor = "lt"  # left-top
                
                
                # Get colors from user preferences
                text_color_name = self.text_color_var.get().lower()
                outline_color_name = self.outline_color_var.get().lower()
                
                text_color = self.color_map.get(text_color_name, (255, 255, 255))
                outline_color = self.color_map.get(outline_color_name, None)
                
                
                # Draw each language on a separate line
                
                for i, name in enumerate(display_names):
                    # Add confidence to first line only
                    if i == 0 and self.show_confidence.get():
                        line_text = f"{name} ({best_confidence:.0%})"
                    else:
                        line_text = name
                    
                    line_y = text_y + (i * line_height)
                    
                    # Draw outline (8 directions) if outline color is specified
                    if outline_color is not None:
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx != 0 or dy != 0:  # Skip center
                                    draw.text((text_x + dx, line_y + dy), line_text, 
                                            font=adjusted_font, fill=outline_color, anchor=anchor)
                    
                    # Draw main text
                    draw.text((text_x, line_y), line_text, font=adjusted_font, fill=text_color, anchor=anchor)
                
                # For results display, join with slash
                display_name = " / ".join(display_names)
                
                # Add to results only if identified
                if best_confidence >= threshold:
                    face_results.append({
                        'index': face_idx + 1,
                        'name': best_match_name,
                        'display_name': display_name,
                        'confidence': best_confidence,
                        'bbox': bbox
                    })
                
                # Add to results text
                if best_confidence >= threshold:
                    self.results_text.insert(tk.END, 
                        f"Face {face_idx + 1}: {display_name} "
                        f"({best_confidence:.0%})\n"
                        f"  Position: ({x1}, {y1}) to ({x2}, {y2})\n\n"
                    )
            
            # Store labeled image
            self.labeled_image = labeled_img
            
            
            # Display labeled image
            self.display_image(self.labeled_image)
            
            # Enable save button
            self.save_button.config(state=tk.NORMAL)
            
            # Add summary
            identified = [r for r in face_results if r['name'] != "Unknown"]
            self.results_text.insert(tk.END, 
                f"\nSummary:\n"
                f"Total faces: {len(faces)}\n"
                f"Identified: {len(identified)}\n"
                f"Unknown: {len(faces) - len(identified)}\n"
            )
            
            if identified:
                self.results_text.insert(tk.END, "\nIdentified members:\n")
                member_counts = {}
                display_names = {}
                for r in identified:
                    member_counts[r['name']] = member_counts.get(r['name'], 0) + 1
                    display_names[r['name']] = r['display_name']
                
                for name, count in sorted(member_counts.items()):
                    display_name = display_names[name]
                    if count > 1:
                        self.results_text.insert(tk.END, f"  {display_name} ({count} faces)\n")
                    else:
                        self.results_text.insert(tk.END, f"  {display_name}\n")
            
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error processing image:\n{str(e)}")
            messagebox.showerror("Error", f"Failed to process image:\n{str(e)}")
    
    def save_image(self):
        """Save the labeled image"""
        if not self.labeled_image:
            return
        
        # Get save filename
        filename = filedialog.asksaveasfilename(
            title="Save Labeled Image",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ],
            initialfile=f"labeled_{os.path.basename(self.current_image_path)}"
        )
        
        if filename:
            try:
                self.labeled_image.save(filename)
                messagebox.showinfo("Success", f"Labeled image saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

def main():
    root = tk.Tk()
    app = WhoIsShe48(root)
    root.mainloop()

if __name__ == "__main__":
    main()