"""
SimpleImage - Image Processing Application

A Python-based image processing application with a modern GUI
for basic image manipulation operations.

Usage:
    python main.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """Application entry point."""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
