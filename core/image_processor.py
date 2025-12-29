"""
Image Processor - Main engine for image manipulation.

Handles image loading, saving, and orchestrates operations
with undo/redo support.
"""

from pathlib import Path
from typing import Optional, List, Callable
from PIL import Image
from .operations import Operation


class ImageProcessor:
    """
    Central image processing engine.
    
    Manages the current image state and provides undo/redo
    functionality through a history stack.
    """

    # Supported image formats
    SUPPORTED_FORMATS = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".gif": "GIF",
        ".bmp": "BMP",
        ".tiff": "TIFF",
        ".tif": "TIFF",
        ".webp": "WEBP",
    }

    def __init__(self, max_history: int = 50):
        """
        Initialize the image processor.
        
        Args:
            max_history: Maximum number of undo steps to keep.
        """
        self._current_image: Optional[Image.Image] = None
        self._original_image: Optional[Image.Image] = None
        self._file_path: Optional[Path] = None
        
        # Undo/redo stacks
        self._history: List[Image.Image] = []
        self._redo_stack: List[Image.Image] = []
        self._max_history = max_history
        
        # Callbacks for UI updates
        self._on_image_changed: Optional[Callable[[Image.Image], None]] = None
        self._on_history_changed: Optional[Callable[[int, int], None]] = None

    @property
    def current_image(self) -> Optional[Image.Image]:
        """Get the current image."""
        return self._current_image

    @property
    def original_image(self) -> Optional[Image.Image]:
        """Get the original (unmodified) image."""
        return self._original_image

    @property
    def file_path(self) -> Optional[Path]:
        """Get the current file path."""
        return self._file_path

    @property
    def has_image(self) -> bool:
        """Check if an image is loaded."""
        return self._current_image is not None

    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 0

    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    @property
    def history_count(self) -> int:
        """Get number of undo steps available."""
        return len(self._history)

    @property
    def redo_count(self) -> int:
        """Get number of redo steps available."""
        return len(self._redo_stack)

    def set_on_image_changed(self, callback: Callable[[Image.Image], None]) -> None:
        """Set callback for when image changes."""
        self._on_image_changed = callback

    def set_on_history_changed(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for when history changes (undo_count, redo_count)."""
        self._on_history_changed = callback

    def _notify_image_changed(self) -> None:
        """Notify listeners that image has changed."""
        if self._on_image_changed and self._current_image:
            self._on_image_changed(self._current_image)

    def _notify_history_changed(self) -> None:
        """Notify listeners that history has changed."""
        if self._on_history_changed:
            self._on_history_changed(self.history_count, self.redo_count)

    def _push_history(self) -> None:
        """Push current state to history stack."""
        if self._current_image:
            self._history.append(self._current_image.copy())
            # Clear redo stack when new action is performed
            self._redo_stack.clear()
            # Limit history size
            while len(self._history) > self._max_history:
                self._history.pop(0)
            self._notify_history_changed()

    def load_image(self, file_path: str | Path) -> bool:
        """
        Load an image from file.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            True if successful, False otherwise.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {suffix}")
        
        try:
            image = Image.open(path)
            # Convert to RGB if necessary (except for images with alpha)
            if image.mode not in ("RGB", "RGBA"):
                if image.mode == "P" and "transparency" in image.info:
                    image = image.convert("RGBA")
                else:
                    image = image.convert("RGB")
            
            # Clear history when loading new image
            self._history.clear()
            self._redo_stack.clear()
            
            self._current_image = image
            self._original_image = image.copy()
            self._file_path = path
            
            self._notify_image_changed()
            self._notify_history_changed()
            return True
            
        except Exception as e:
            raise IOError(f"Failed to load image: {e}")

    def save_image(self, file_path: Optional[str | Path] = None, quality: int = 95) -> bool:
        """
        Save the current image to file.
        
        Args:
            file_path: Path to save to. Uses original path if not specified.
            quality: JPEG quality (1-100).
            
        Returns:
            True if successful, False otherwise.
        """
        if not self._current_image:
            raise ValueError("No image to save")
        
        path = Path(file_path) if file_path else self._file_path
        if not path:
            raise ValueError("No file path specified")
        
        suffix = path.suffix.lower()
        format_name = self.SUPPORTED_FORMATS.get(suffix)
        
        if not format_name:
            raise ValueError(f"Unsupported image format: {suffix}")
        
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare save options
            save_kwargs = {}
            if format_name == "JPEG":
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
                # Convert RGBA to RGB for JPEG
                image_to_save = self._current_image
                if image_to_save.mode == "RGBA":
                    background = Image.new("RGB", image_to_save.size, (255, 255, 255))
                    background.paste(image_to_save, mask=image_to_save.split()[3])
                    image_to_save = background
                image_to_save.save(path, format=format_name, **save_kwargs)
            elif format_name == "PNG":
                save_kwargs["optimize"] = True
                self._current_image.save(path, format=format_name, **save_kwargs)
            else:
                self._current_image.save(path, format=format_name)
            
            self._file_path = path
            return True
            
        except Exception as e:
            raise IOError(f"Failed to save image: {e}")

    def apply_operation(self, operation: Operation) -> bool:
        """
        Apply an operation to the current image.
        
        Args:
            operation: The operation to apply.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self._current_image:
            raise ValueError("No image loaded")
        
        try:
            # Save current state for undo
            self._push_history()
            
            # Execute operation
            self._current_image = operation.execute(self._current_image)
            
            self._notify_image_changed()
            return True
            
        except Exception as e:
            # Restore from history on failure
            if self._history:
                self._current_image = self._history.pop()
            raise RuntimeError(f"Operation failed: {e}")

    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            True if successful, False if nothing to undo.
        """
        if not self._history:
            return False
        
        # Save current state to redo stack
        if self._current_image:
            self._redo_stack.append(self._current_image.copy())
        
        # Restore previous state
        self._current_image = self._history.pop()
        
        self._notify_image_changed()
        self._notify_history_changed()
        return True

    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if successful, False if nothing to redo.
        """
        if not self._redo_stack:
            return False
        
        # Save current state to history
        if self._current_image:
            self._history.append(self._current_image.copy())
        
        # Restore from redo stack
        self._current_image = self._redo_stack.pop()
        
        self._notify_image_changed()
        self._notify_history_changed()
        return True

    def reset_to_original(self) -> bool:
        """
        Reset image to original (when loaded).
        
        Returns:
            True if successful, False if no original.
        """
        if not self._original_image:
            return False
        
        self._push_history()
        self._current_image = self._original_image.copy()
        
        self._notify_image_changed()
        return True

    def get_image_info(self) -> dict:
        """Get information about the current image."""
        if not self._current_image:
            return {}
        
        return {
            "width": self._current_image.width,
            "height": self._current_image.height,
            "mode": self._current_image.mode,
            "format": self._current_image.format,
            "file_path": str(self._file_path) if self._file_path else None,
            "file_name": self._file_path.name if self._file_path else None,
        }

    @classmethod
    def get_supported_extensions(cls) -> tuple:
        """Get tuple of supported file extensions for file dialogs."""
        return tuple(cls.SUPPORTED_FORMATS.keys())
