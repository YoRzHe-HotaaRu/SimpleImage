"""
Image Canvas - Zoomable, pannable image display widget.

Provides image rendering with mouse wheel zoom and drag-to-pan.
"""

import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageTk
from typing import Optional, Callable, Tuple


class ImageCanvas(ctk.CTkFrame):
    """
    A canvas widget for displaying and interacting with images.
    
    Features:
    - Mouse wheel zoom
    - Click and drag to pan
    - Fit to window and 100% zoom
    - Crop selection overlay
    """

    def __init__(
        self,
        master,
        bg_color: str = "#1a1a1a",
        checkerboard_color1: str = "#2a2a2a",
        checkerboard_color2: str = "#3a3a3a",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self._bg_color = bg_color
        self._checker1 = checkerboard_color1
        self._checker2 = checkerboard_color2
        
        # Image state
        self._image: Optional[Image.Image] = None
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        self._zoom_level: float = 1.0
        self._min_zoom: float = 0.1
        self._max_zoom: float = 10.0
        
        # Pan state
        self._offset_x: float = 0
        self._offset_y: float = 0
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._is_dragging: bool = False
        
        # Crop selection state
        self._crop_mode: bool = False
        self._crop_start: Optional[Tuple[int, int]] = None
        self._crop_end: Optional[Tuple[int, int]] = None
        self._crop_callback: Optional[Callable[[int, int, int, int], None]] = None
        
        # Create canvas
        self._canvas = Canvas(
            self,
            bg=bg_color,
            highlightthickness=0,
            cursor="crosshair",
        )
        self._canvas.pack(fill="both", expand=True)
        
        # Bind events
        self._canvas.bind("<Configure>", self._on_resize)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self._canvas.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down
        self._canvas.bind("<ButtonPress-1>", self._on_button_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_button_release)
        
        # Draw initial checkerboard
        self.after(10, self._draw_checkerboard)

    @property
    def zoom_level(self) -> float:
        """Current zoom level (1.0 = 100%)."""
        return self._zoom_level

    @property
    def has_image(self) -> bool:
        """Check if an image is loaded."""
        return self._image is not None

    def set_image(self, image: Image.Image) -> None:
        """
        Set the image to display.
        
        Args:
            image: PIL Image to display.
        """
        self._image = image.copy()
        self._fit_to_window()
        self._redraw()

    def clear_image(self) -> None:
        """Clear the current image."""
        self._image = None
        self._photo_image = None
        self._zoom_level = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self._canvas.delete("all")
        self._draw_checkerboard()

    def fit_to_window(self) -> None:
        """Fit image to window size."""
        self._fit_to_window()
        self._redraw()

    def zoom_100(self) -> None:
        """Set zoom to 100%."""
        if self._image:
            self._zoom_level = 1.0
            self._center_image()
            self._redraw()

    def zoom_in(self) -> None:
        """Zoom in by 25%."""
        self._apply_zoom(1.25)

    def zoom_out(self) -> None:
        """Zoom out by 25%."""
        self._apply_zoom(0.8)

    def set_crop_mode(self, enabled: bool, callback: Optional[Callable] = None) -> None:
        """
        Enable or disable crop selection mode.
        
        Args:
            enabled: True to enable crop mode.
            callback: Called with (left, top, right, bottom) when selection made.
        """
        self._crop_mode = enabled
        self._crop_callback = callback
        self._crop_start = None
        self._crop_end = None
        self._canvas.config(cursor="crosshair" if enabled else "fleur")
        self._redraw()

    def _fit_to_window(self) -> None:
        """Calculate zoom to fit image in window."""
        if not self._image:
            return
        
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Calculate zoom to fit
        zoom_x = canvas_width / self._image.width
        zoom_y = canvas_height / self._image.height
        self._zoom_level = min(zoom_x, zoom_y, 1.0) * 0.95  # 5% padding
        
        self._center_image()

    def _center_image(self) -> None:
        """Center the image in the canvas."""
        if not self._image:
            return
        
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        display_width = self._image.width * self._zoom_level
        display_height = self._image.height * self._zoom_level
        
        self._offset_x = (canvas_width - display_width) / 2
        self._offset_y = (canvas_height - display_height) / 2

    def _apply_zoom(self, factor: float, center_x: Optional[int] = None, center_y: Optional[int] = None) -> None:
        """Apply zoom factor around a point."""
        if not self._image:
            return
        
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        # Default to canvas center
        if center_x is None:
            center_x = canvas_width // 2
        if center_y is None:
            center_y = canvas_height // 2
        
        # Calculate new zoom
        old_zoom = self._zoom_level
        new_zoom = old_zoom * factor
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        
        if new_zoom == old_zoom:
            return
        
        # Adjust offset to zoom around cursor
        self._offset_x = center_x - (center_x - self._offset_x) * (new_zoom / old_zoom)
        self._offset_y = center_y - (center_y - self._offset_y) * (new_zoom / old_zoom)
        
        self._zoom_level = new_zoom
        self._redraw()

    def _draw_checkerboard(self) -> None:
        """Draw transparency checkerboard pattern."""
        self._canvas.delete("checkerboard")
        
        width = self._canvas.winfo_width()
        height = self._canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        size = 16
        for y in range(0, height, size):
            for x in range(0, width, size):
                color = self._checker1 if ((x // size) + (y // size)) % 2 == 0 else self._checker2
                self._canvas.create_rectangle(
                    x, y, x + size, y + size,
                    fill=color, outline="", tags="checkerboard"
                )

    def _redraw(self) -> None:
        """Redraw the canvas with current image and state."""
        self._canvas.delete("image")
        self._canvas.delete("crop")
        
        if not self._image:
            return
        
        # Calculate display size
        display_width = int(self._image.width * self._zoom_level)
        display_height = int(self._image.height * self._zoom_level)
        
        if display_width < 1 or display_height < 1:
            return
        
        # Resize image for display
        display_image = self._image.resize(
            (display_width, display_height),
            Image.Resampling.LANCZOS if self._zoom_level < 1 else Image.Resampling.NEAREST
        )
        
        self._photo_image = ImageTk.PhotoImage(display_image)
        
        # Draw image
        self._canvas.create_image(
            self._offset_x,
            self._offset_y,
            image=self._photo_image,
            anchor="nw",
            tags="image"
        )
        
        # Draw crop selection if active
        if self._crop_mode and self._crop_start and self._crop_end:
            self._draw_crop_selection()

    def _draw_crop_selection(self) -> None:
        """Draw crop selection rectangle."""
        if not self._crop_start or not self._crop_end:
            return
        
        x1 = min(self._crop_start[0], self._crop_end[0])
        y1 = min(self._crop_start[1], self._crop_end[1])
        x2 = max(self._crop_start[0], self._crop_end[0])
        y2 = max(self._crop_start[1], self._crop_end[1])
        
        # Draw semi-transparent overlay outside selection
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        # Draw selection rectangle
        self._canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="#00ffff",
            width=2,
            dash=(5, 3),
            tags="crop"
        )
        
        # Draw corner handles
        handle_size = 8
        for x, y in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
            self._canvas.create_rectangle(
                x - handle_size//2, y - handle_size//2,
                x + handle_size//2, y + handle_size//2,
                fill="#00ffff",
                outline="#ffffff",
                tags="crop"
            )

    def _canvas_to_image_coords(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convert canvas coordinates to image coordinates."""
        if not self._image:
            return 0, 0
        
        img_x = int((canvas_x - self._offset_x) / self._zoom_level)
        img_y = int((canvas_y - self._offset_y) / self._zoom_level)
        
        # Clamp to image bounds
        img_x = max(0, min(self._image.width, img_x))
        img_y = max(0, min(self._image.height, img_y))
        
        return img_x, img_y

    def _on_resize(self, event) -> None:
        """Handle canvas resize."""
        self._draw_checkerboard()
        if self._image:
            self._redraw()

    def _on_mousewheel(self, event) -> None:
        """Handle mouse wheel for zoom."""
        if not self._image:
            return
        
        # Get scroll direction
        if hasattr(event, 'delta'):
            factor = 1.1 if event.delta > 0 else 0.9
        else:
            factor = 1.1 if event.num == 4 else 0.9
        
        self._apply_zoom(factor, event.x, event.y)

    def _on_button_press(self, event) -> None:
        """Handle mouse button press."""
        if self._crop_mode and self._image:
            self._crop_start = (event.x, event.y)
            self._crop_end = (event.x, event.y)
        else:
            self._is_dragging = True
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            self._canvas.config(cursor="fleur")

    def _on_drag(self, event) -> None:
        """Handle mouse drag."""
        if self._crop_mode:
            self._crop_end = (event.x, event.y)
            self._redraw()
        elif self._is_dragging:
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            self._offset_x += dx
            self._offset_y += dy
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            self._redraw()

    def _on_button_release(self, event) -> None:
        """Handle mouse button release."""
        if self._crop_mode and self._crop_start and self._crop_end:
            # Convert to image coordinates
            x1, y1 = self._canvas_to_image_coords(self._crop_start[0], self._crop_start[1])
            x2, y2 = self._canvas_to_image_coords(self._crop_end[0], self._crop_end[1])
            
            # Ensure proper order
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            # Callback with crop coordinates
            if self._crop_callback and right > left and bottom > top:
                self._crop_callback(left, top, right, bottom)
        else:
            self._is_dragging = False
            self._canvas.config(cursor="crosshair" if self._crop_mode else "fleur")
