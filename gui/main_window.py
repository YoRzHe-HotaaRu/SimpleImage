"""
Main Window - Primary application window.

The main GUI container with menu bar, toolbar, sidebar, and canvas.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from pathlib import Path
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    ImageProcessor,
    ResizeOperation,
    RotateOperation,
    FlipOperation,
    CropOperation,
    BrightnessOperation,
    ContrastOperation,
    SaturationOperation,
    GrayscaleOperation,
    InvertOperation,
    BlurOperation,
    SharpenOperation,
    EdgeDetectOperation,
    EmbossOperation,
    PosterizeOperation,
    CompositeAdjustmentOperation,
)
from utils import FileHandler
from gui.image_canvas import ImageCanvas
from gui.controls import TransformPanel, AdjustmentPanel, FilterPanel, HistoryPanel


class MainWindow(ctk.CTk):
    """
    Main application window.
    
    Layout:
    ┌─────────────────────────────────────────────┐
    │ Toolbar                                     │
    ├──────────────────────────────────────┬──────┤
    │                                      │      │
    │                                      │ Side │
    │            Image Canvas              │ bar  │
    │                                      │      │
    │                                      │      │
    ├──────────────────────────────────────┴──────┤
    │ Status Bar                                  │
    └─────────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window setup
        self.title("ClaRity Image Processing")
        self.geometry("1280x800")
        self.minsize(900, 600)
        
        # Configure colors
        self._bg_dark = "#0d0d0d"
        self._bg_panel = "#1a1a1a"
        self._accent = "#00ffff"
        self._accent_secondary = "#ff006e"
        
        self.configure(fg_color=self._bg_dark)
        
        # Initialize processor
        self._processor = ImageProcessor()
        self._processor.set_on_image_changed(self._on_image_changed)
        self._processor.set_on_history_changed(self._on_history_changed)
        
        # Create UI
        self._create_toolbar()
        self._create_main_area()
        self._create_statusbar()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Set window icon
        self._set_icon()

    def _create_toolbar(self) -> None:
        """Create the top toolbar."""
        toolbar = ctk.CTkFrame(
            self,
            height=48,
            fg_color=self._bg_panel,
            corner_radius=0,
        )
        toolbar.pack(fill="x", padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Left section - File operations
        left_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_frame.pack(side="left", padx=8, pady=8)
        
        btn_style = {
            "height": 32,
            "font": ctk.CTkFont(size=12),
            "fg_color": "#2a2a2a",
            "hover_color": "#3a3a3a",
        }
        
        ctk.CTkButton(
            left_frame,
            text="📁 Open",
            width=80,
            command=self._open_file,
            **btn_style,
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            left_frame,
            text="💾 Save",
            width=80,
            command=self._save_file,
            **btn_style,
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            left_frame,
            text="📥 Save As",
            width=80,
            command=self._save_file_as,
            **btn_style,
        ).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkFrame(
            left_frame,
            width=2,
            height=24,
            fg_color="#3a3a3a",
        ).pack(side="left", padx=12)
        
        # Zoom controls
        ctk.CTkButton(
            left_frame,
            text="🔍+",
            width=40,
            command=self._zoom_in,
            **btn_style,
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            left_frame,
            text="🔍-",
            width=40,
            command=self._zoom_out,
            **btn_style,
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            left_frame,
            text="Fit",
            width=50,
            command=self._zoom_fit,
            **btn_style,
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            left_frame,
            text="100%",
            width=50,
            command=self._zoom_100,
            **btn_style,
        ).pack(side="left", padx=2)
        
        # Right section - Undo/Redo
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=8, pady=8)
        
        self._undo_btn = ctk.CTkButton(
            right_frame,
            text="↶ Undo",
            width=70,
            state="disabled",
            command=self._undo,
            **btn_style,
        )
        self._undo_btn.pack(side="left", padx=2)
        
        self._redo_btn = ctk.CTkButton(
            right_frame,
            text="↷ Redo",
            width=70,
            state="disabled",
            command=self._redo,
            **btn_style,
        )
        self._redo_btn.pack(side="left", padx=2)
        
        # Logo and Title
        brand_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        brand_frame.pack(side="left", padx=20)
        
        # Load and display logo
        try:
            assets_dir = Path(__file__).parent.parent / "assets"
            logo_path = assets_dir / "logo.png"
            if logo_path.exists():
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((28, 28), Image.Resampling.LANCZOS)
                self._logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ctk.CTkLabel(
                    brand_frame,
                    image=self._logo_photo,
                    text="",
                )
                logo_label.pack(side="left", padx=(0, 8))
        except Exception:
            pass  # Skip logo if it can't be loaded
        
        title_label = ctk.CTkLabel(
            brand_frame,
            text="ClaRity",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=self._accent,
        )
        title_label.pack(side="left")

    def _create_main_area(self) -> None:
        """Create the main content area with canvas and sidebar."""
        main = ctk.CTkFrame(self, fg_color=self._bg_dark)
        main.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Image canvas (left)
        canvas_frame = ctk.CTkFrame(
            main,
            fg_color=self._bg_panel,
            corner_radius=0,
        )
        canvas_frame.pack(side="left", fill="both", expand=True)
        
        self._canvas = ImageCanvas(
            canvas_frame,
            fg_color=self._bg_panel,
        )
        self._canvas.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Sidebar (right)
        sidebar = ctk.CTkScrollableFrame(
            main,
            width=260,
            fg_color=self._bg_panel,
            corner_radius=0,
        )
        sidebar.pack(side="right", fill="y", padx=0, pady=0)
        
        # Control panels
        self._transform_panel = TransformPanel(
            sidebar,
            fg_color="transparent",
            on_resize=self._resize,
            on_rotate=self._rotate,
            on_flip_h=self._flip_horizontal,
            on_flip_v=self._flip_vertical,
            on_crop=self._start_crop,
        )
        self._transform_panel.pack(fill="x", padx=8, pady=4)
        
        self._adjustment_panel = AdjustmentPanel(
            sidebar,
            fg_color="transparent",
            on_apply_adjustments=self._apply_adjustments,
            on_grayscale=self._apply_grayscale,
            on_invert=self._apply_invert,
        )
        self._adjustment_panel.pack(fill="x", padx=8, pady=4)
        
        self._filter_panel = FilterPanel(
            sidebar,
            fg_color="transparent",
            on_blur=self._apply_blur,
            on_sharpen=self._apply_sharpen,
            on_edge=self._apply_edge,
            on_emboss=self._apply_emboss,
            on_posterize=self._apply_posterize,
        )
        self._filter_panel.pack(fill="x", padx=8, pady=4)
        
        self._history_panel = HistoryPanel(
            sidebar,
            fg_color="transparent",
            on_undo=self._undo,
            on_redo=self._redo,
            on_reset=self._reset_to_original,
        )
        self._history_panel.pack(fill="x", padx=8, pady=4)

    def _create_statusbar(self) -> None:
        """Create the status bar at the bottom."""
        statusbar = ctk.CTkFrame(
            self,
            height=28,
            fg_color=self._bg_panel,
            corner_radius=0,
        )
        statusbar.pack(fill="x", padx=0, pady=0)
        statusbar.pack_propagate(False)
        
        self._status_label = ctk.CTkLabel(
            statusbar,
            text="Ready • Open an image to get started",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#666666",
        )
        self._status_label.pack(side="left", padx=12)
        
        self._zoom_label = ctk.CTkLabel(
            statusbar,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#666666",
        )
        self._zoom_label.pack(side="right", padx=12)

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-Shift-s>", lambda e: self._save_file_as())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-y>", lambda e: self._redo())
        self.bind("<Control-Shift-z>", lambda e: self._redo())
        self.bind("<Escape>", lambda e: self._cancel_crop())

    # =========== File Operations ===========

    def _open_file(self) -> None:
        """Open an image file."""
        path = FileHandler.open_file_dialog()
        if path:
            try:
                self._processor.load_image(path)
                self._update_status(f"Opened: {path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def _save_file(self) -> None:
        """Save to current file."""
        if not self._processor.has_image:
            return
        
        if self._processor.file_path:
            try:
                self._processor.save_image()
                self._update_status(f"Saved: {self._processor.file_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{e}")
        else:
            self._save_file_as()

    def _save_file_as(self) -> None:
        """Save to a new file."""
        if not self._processor.has_image:
            return
        
        initial_name = None
        if self._processor.file_path:
            initial_name = self._processor.file_path.stem + "_edited"
        
        path = FileHandler.save_file_dialog(initial_file=initial_name)
        if path:
            try:
                self._processor.save_image(path)
                self._update_status(f"Saved: {path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    # =========== Zoom Operations ===========

    def _zoom_in(self) -> None:
        self._canvas.zoom_in()
        self._update_zoom_label()

    def _zoom_out(self) -> None:
        self._canvas.zoom_out()
        self._update_zoom_label()

    def _zoom_fit(self) -> None:
        self._canvas.fit_to_window()
        self._update_zoom_label()

    def _zoom_100(self) -> None:
        self._canvas.zoom_100()
        self._update_zoom_label()

    # =========== Transform Operations ===========

    def _resize(self, percentage: int) -> None:
        if not self._processor.has_image:
            return
        try:
            op = ResizeOperation(percentage=percentage)
            self._processor.apply_operation(op)
            self._update_status(f"Resized to {percentage}%")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _rotate(self, angle: int) -> None:
        if not self._processor.has_image:
            return
        try:
            op = RotateOperation(angle)
            self._processor.apply_operation(op)
            self._update_status(f"Rotated {angle}°")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _flip_horizontal(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = FlipOperation(horizontal=True)
            self._processor.apply_operation(op)
            self._update_status("Flipped horizontally")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _flip_vertical(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = FlipOperation(horizontal=False)
            self._processor.apply_operation(op)
            self._update_status("Flipped vertically")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _start_crop(self) -> None:
        if not self._processor.has_image:
            return
        self._canvas.set_crop_mode(True, self._apply_crop)
        self._update_status("Select crop area • Press Escape to cancel")

    def _apply_crop(self, left: int, top: int, right: int, bottom: int) -> None:
        try:
            op = CropOperation(left, top, right, bottom)
            self._processor.apply_operation(op)
            self._update_status(f"Cropped to {right-left}x{bottom-top}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._canvas.set_crop_mode(False)

    def _cancel_crop(self) -> None:
        self._canvas.set_crop_mode(False)
        self._update_status("Crop cancelled")

    # =========== Adjustment Operations ===========

    def _apply_adjustments(self, brightness: int, contrast: int, saturation: int) -> None:
        """
        Apply brightness, contrast, and saturation adjustments from original image.
        
        All adjustments are absolute values from -100 to 100.
        Setting all to 0 resets to the original image.
        """
        if not self._processor.has_image:
            return
        
        # All zeros = reset to original
        if brightness == 0 and contrast == 0 and saturation == 0:
            if self._processor.original_image:
                self._processor.reset_to_original()
                self._update_status("Reset to original")
            return
        
        try:
            op = CompositeAdjustmentOperation(
                self._processor.original_image,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation
            )
            self._processor.apply_operation(op)
            self._update_status(f"Adjustments: B={brightness} C={contrast} S={saturation}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_grayscale(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = GrayscaleOperation()
            self._processor.apply_operation(op)
            self._update_status("Converted to grayscale")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_invert(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = InvertOperation()
            self._processor.apply_operation(op)
            self._update_status("Colors inverted")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========== Filter Operations ===========

    def _apply_blur(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = BlurOperation(radius=2.0)
            self._processor.apply_operation(op)
            self._update_status("Applied blur")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_sharpen(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = SharpenOperation()
            self._processor.apply_operation(op)
            self._update_status("Applied sharpen")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_edge(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = EdgeDetectOperation()
            self._processor.apply_operation(op)
            self._update_status("Applied edge detection")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_emboss(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = EmbossOperation()
            self._processor.apply_operation(op)
            self._update_status("Applied emboss")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_posterize(self) -> None:
        if not self._processor.has_image:
            return
        try:
            op = PosterizeOperation(bits=4)
            self._processor.apply_operation(op)
            self._update_status("Applied posterize")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========== History Operations ===========

    def _undo(self) -> None:
        if self._processor.undo():
            self._update_status("Undo")

    def _redo(self) -> None:
        if self._processor.redo():
            self._update_status("Redo")

    def _reset_to_original(self) -> None:
        if self._processor.reset_to_original():
            self._update_status("Reset to original")

    # =========== Callbacks ===========

    def _on_image_changed(self, image) -> None:
        """Called when image changes."""
        self._canvas.set_image(image)
        self._update_zoom_label()
        
        info = self._processor.get_image_info()
        if info:
            self._update_status(
                f"{info.get('file_name', 'Image')} • "
                f"{info['width']}×{info['height']} • "
                f"{info['mode']}"
            )

    def _on_history_changed(self, undo_count: int, redo_count: int) -> None:
        """Called when history changes."""
        self._undo_btn.configure(state="normal" if undo_count > 0 else "disabled")
        self._redo_btn.configure(state="normal" if redo_count > 0 else "disabled")
        self._history_panel.update_state(undo_count, redo_count)

    def _update_status(self, message: str) -> None:
        """Update status bar message."""
        self._status_label.configure(text=message)

    def _update_zoom_label(self) -> None:
        """Update zoom level display."""
        if self._canvas.has_image:
            zoom = int(self._canvas.zoom_level * 100)
            self._zoom_label.configure(text=f"Zoom: {zoom}%")
        else:
            self._zoom_label.configure(text="")

    def _on_close(self) -> None:
        """Handle window close."""
        self.destroy()

    def _set_icon(self) -> None:
        """Set the window icon."""
        try:
            # Get the assets directory relative to this file
            assets_dir = Path(__file__).parent.parent / "assets"
            icon_path = assets_dir / "logo.png"
            
            if icon_path.exists():
                from PIL import Image, ImageTk
                import tempfile
                
                # Load the PNG image
                icon_image = Image.open(icon_path)
                
                # For Windows, we need to use iconbitmap with an ICO file
                # Create a temporary ICO file
                ico_path = assets_dir / "logo.ico"
                if not ico_path.exists():
                    # Create ICO with multiple sizes for best quality
                    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]
                    icons = []
                    for size in icon_sizes:
                        resized = icon_image.resize(size, Image.Resampling.LANCZOS)
                        icons.append(resized)
                    icons[0].save(ico_path, format='ICO', sizes=icon_sizes)
                
                # Set the icon using iconbitmap (works on Windows)
                self.iconbitmap(str(ico_path))
        except Exception as e:
            # Fallback to iconphoto if iconbitmap fails
            try:
                assets_dir = Path(__file__).parent.parent / "assets"
                icon_path = assets_dir / "logo.png"
                if icon_path.exists():
                    from PIL import Image, ImageTk
                    icon_image = Image.open(icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)
                    self._icon_photo = icon_photo
            except Exception:
                pass  # Silently fail if icon can't be loaded

    def run(self) -> None:
        """Start the application."""
        self.mainloop()
