"""
File Handler - Utilities for file operations.

Provides file dialog helpers and path validation.
"""

from pathlib import Path
from typing import Optional, Tuple
from tkinter import filedialog
import os


class FileHandler:
    """
    Handles file I/O operations and dialogs.
    """

    # File type definitions for dialogs
    IMAGE_FILETYPES = [
        ("All Images", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.webp"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("GIF", "*.gif"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
        ("WebP", "*.webp"),
        ("All Files", "*.*"),
    ]

    SAVE_FILETYPES = [
        ("JPEG", "*.jpg"),
        ("PNG", "*.png"),
        ("GIF", "*.gif"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff"),
        ("WebP", "*.webp"),
    ]

    @classmethod
    def open_file_dialog(
        cls,
        title: str = "Open Image",
        initial_dir: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Open a file dialog to select an image.
        
        Args:
            title: Dialog title.
            initial_dir: Initial directory to open.
            
        Returns:
            Path to selected file, or None if cancelled.
        """
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir,
            filetypes=cls.IMAGE_FILETYPES,
        )
        
        if file_path:
            return Path(file_path)
        return None

    @classmethod
    def save_file_dialog(
        cls,
        title: str = "Save Image",
        initial_dir: Optional[str] = None,
        initial_file: Optional[str] = None,
        default_extension: str = ".png",
    ) -> Optional[Path]:
        """
        Open a save dialog to choose save location.
        
        Args:
            title: Dialog title.
            initial_dir: Initial directory.
            initial_file: Suggested filename.
            default_extension: Default file extension.
            
        Returns:
            Path to save to, or None if cancelled.
        """
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        
        file_path = filedialog.asksaveasfilename(
            title=title,
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=default_extension,
            filetypes=cls.SAVE_FILETYPES,
        )
        
        if file_path:
            return Path(file_path)
        return None

    @staticmethod
    def validate_path(path: str | Path) -> Tuple[bool, str]:
        """
        Validate that a path exists and is readable.
        
        Args:
            path: Path to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        path = Path(path)
        
        if not path.exists():
            return False, f"File not found: {path}"
        
        if not path.is_file():
            return False, f"Not a file: {path}"
        
        if not os.access(path, os.R_OK):
            return False, f"Cannot read file: {path}"
        
        return True, ""

    @staticmethod
    def get_unique_path(path: str | Path) -> Path:
        """
        Get a unique file path by adding a number suffix if needed.
        
        Args:
            path: Desired path.
            
        Returns:
            Unique path that doesn't exist.
        """
        path = Path(path)
        
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    @staticmethod
    def get_file_size_str(path: str | Path) -> str:
        """
        Get human-readable file size.
        
        Args:
            path: Path to file.
            
        Returns:
            Size string like "1.5 MB".
        """
        path = Path(path)
        if not path.exists():
            return "Unknown"
        
        size = path.stat().st_size
        
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        
        return f"{size:.1f} TB"
