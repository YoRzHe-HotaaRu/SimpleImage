# SimpleImage

A Python-based image processing application with a modern, dark-themed GUI for basic image manipulation operations.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![CustomTkinter](https://img.shields.io/badge/gui-customtkinter-green)
![Pillow](https://img.shields.io/badge/imaging-pillow-orange)

## Features

### Image Operations
- **Transform**: Resize, rotate (90°/180°/270°), flip (horizontal/vertical), crop
- **Adjustments**: Brightness, contrast, saturation, grayscale, invert colors
- **Filters**: Blur, sharpen, edge detection, emboss, posterize

### Application Features
- Modern dark-themed interface
- Zoom and pan with mouse wheel and drag
- Full undo/redo history
- Keyboard shortcuts
- Multiple format support (JPEG, PNG, GIF, BMP, TIFF, WebP)

## Installation

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open image |
| `Ctrl+S` | Save image |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Escape` | Cancel crop |

### Mouse Controls

- **Scroll wheel**: Zoom in/out
- **Click + drag**: Pan image
- **Crop mode**: Click and drag to select area

## Project Structure

```
SimpleImage/
├── core/                    # Core image processing logic
│   ├── __init__.py
│   ├── image_processor.py   # Main processing engine
│   └── operations.py        # Individual operation implementations
├── gui/                     # GUI components
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── image_canvas.py      # Image display and interaction
│   └── controls.py          # Control panels and buttons
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── file_handler.py      # File I/O operations
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Requirements

- Python 3.8+
- customtkinter >= 5.2.0
- Pillow >= 10.0.0

## License

MIT License
