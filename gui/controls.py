"""
Control Panels - UI widgets for image operations.

Provides panels for transforms, adjustments, filters, and history.
"""

import customtkinter as ctk
from typing import Callable, Optional
from functools import partial


class CollapsiblePanel(ctk.CTkFrame):
    """A collapsible panel with header and content area."""

    def __init__(
        self,
        master,
        title: str,
        collapsed: bool = False,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self._collapsed = collapsed
        self._title = title
        
        # Header frame
        self._header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self._header.pack(fill="x", padx=0, pady=0)
        self._header.pack_propagate(False)
        
        # Toggle button
        self._toggle_btn = ctk.CTkButton(
            self._header,
            text=f"{'▸' if collapsed else '▾'} {title}",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            anchor="w",
            command=self._toggle,
        )
        self._toggle_btn.pack(fill="x", expand=True, padx=4, pady=2)
        
        # Content frame
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        if not collapsed:
            self._content.pack(fill="x", padx=8, pady=(0, 8))

    @property
    def content(self) -> ctk.CTkFrame:
        """Get the content frame to add widgets to."""
        return self._content

    def _toggle(self) -> None:
        """Toggle collapsed state."""
        self._collapsed = not self._collapsed
        self._toggle_btn.configure(text=f"{'▸' if self._collapsed else '▾'} {self._title}")
        
        if self._collapsed:
            self._content.pack_forget()
        else:
            self._content.pack(fill="x", padx=8, pady=(0, 8))


class TransformPanel(CollapsiblePanel):
    """Panel for transform operations (resize, rotate, flip, crop)."""

    def __init__(
        self,
        master,
        on_resize: Optional[Callable] = None,
        on_rotate: Optional[Callable] = None,
        on_flip_h: Optional[Callable] = None,
        on_flip_v: Optional[Callable] = None,
        on_crop: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, title="TRANSFORM", **kwargs)
        
        self._on_resize = on_resize
        self._on_rotate = on_rotate
        self._on_flip_h = on_flip_h
        self._on_flip_v = on_flip_v
        self._on_crop = on_crop
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        content = self.content
        
        # Resize section
        resize_frame = ctk.CTkFrame(content, fg_color="transparent")
        resize_frame.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            resize_frame,
            text="Resize %",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(anchor="w")
        
        self._resize_slider = ctk.CTkSlider(
            resize_frame,
            from_=10,
            to=200,
            number_of_steps=19,
            command=self._on_resize_change,
        )
        self._resize_slider.set(100)
        self._resize_slider.pack(fill="x", pady=2)
        
        self._resize_label = ctk.CTkLabel(
            resize_frame,
            text="100%",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self._resize_label.pack(anchor="e")
        
        # Apply resize button
        ctk.CTkButton(
            resize_frame,
            text="Apply Resize",
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#00a896",
            hover_color="#028090",
            command=self._apply_resize,
        ).pack(fill="x", pady=(4, 0))
        
        # Rotate section
        rotate_frame = ctk.CTkFrame(content, fg_color="transparent")
        rotate_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            rotate_frame,
            text="Rotate",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(anchor="w")
        
        rotate_buttons = ctk.CTkFrame(rotate_frame, fg_color="transparent")
        rotate_buttons.pack(fill="x", pady=4)
        
        for angle, text in [(-90, "↺ 90°"), (90, "↻ 90°"), (180, "180°")]:
            ctk.CTkButton(
                rotate_buttons,
                text=text,
                width=60,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color="#2a2a2a",
                hover_color="#3a3a3a",
                command=partial(self._apply_rotate, angle),
            ).pack(side="left", expand=True, fill="x", padx=1)
        
        # Flip section
        flip_frame = ctk.CTkFrame(content, fg_color="transparent")
        flip_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            flip_frame,
            text="Flip",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(anchor="w")
        
        flip_buttons = ctk.CTkFrame(flip_frame, fg_color="transparent")
        flip_buttons.pack(fill="x", pady=4)
        
        ctk.CTkButton(
            flip_buttons,
            text="⇄ Horizontal",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            command=lambda: self._on_flip_h() if self._on_flip_h else None,
        ).pack(side="left", expand=True, fill="x", padx=(0, 2))
        
        ctk.CTkButton(
            flip_buttons,
            text="⇅ Vertical",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            command=lambda: self._on_flip_v() if self._on_flip_v else None,
        ).pack(side="left", expand=True, fill="x", padx=(2, 0))
        
        # Crop button
        self._crop_btn = ctk.CTkButton(
            content,
            text="✂ Crop Selection",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#e63946",
            hover_color="#d62828",
            command=lambda: self._on_crop() if self._on_crop else None,
        )
        self._crop_btn.pack(fill="x", pady=(8, 0))

    def _on_resize_change(self, value: float) -> None:
        self._resize_label.configure(text=f"{int(value)}%")

    def _apply_resize(self) -> None:
        if self._on_resize:
            self._on_resize(int(self._resize_slider.get()))

    def _apply_rotate(self, angle: int) -> None:
        if self._on_rotate:
            self._on_rotate(angle)


class AdjustmentPanel(CollapsiblePanel):
    """
    Panel for color adjustments (brightness, contrast, saturation).
    
    Uses absolute adjustment values from -100 to 100 where 0 means no change.
    All adjustments are applied together from the original image to prevent
    cumulative stacking of effects.
    """

    def __init__(
        self,
        master,
        on_apply_adjustments: Optional[Callable[[int, int, int], None]] = None,
        on_grayscale: Optional[Callable] = None,
        on_invert: Optional[Callable] = None,
        **kwargs
    ):
        """
        Args:
            master: Parent widget.
            on_apply_adjustments: Callback with (brightness, contrast, saturation) values.
            on_grayscale: Callback for grayscale operation.
            on_invert: Callback for invert operation.
        """
        super().__init__(master, title="ADJUSTMENTS", **kwargs)
        
        self._on_apply_adjustments = on_apply_adjustments
        self._on_grayscale = on_grayscale
        self._on_invert = on_invert
        
        self._sliders = {}
        self._create_widgets()

    def _create_widgets(self) -> None:
        content = self.content
        
        # Brightness slider
        self._create_slider(content, "Brightness", "brightness", -100, 100, 0)
        
        # Contrast slider
        self._create_slider(content, "Contrast", "contrast", -100, 100, 0)
        
        # Saturation slider
        self._create_slider(content, "Saturation", "saturation", -100, 100, 0)
        
        # Apply button
        ctk.CTkButton(
            content,
            text="Apply Adjustments",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#00a896",
            hover_color="#028090",
            command=self._apply_adjustments,
        ).pack(fill="x", pady=(8, 4))
        
        # Reset button
        ctk.CTkButton(
            content,
            text="Reset Sliders",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            command=self._reset_sliders,
        ).pack(fill="x", pady=2)
        
        # Quick actions
        quick_frame = ctk.CTkFrame(content, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(8, 0))
        
        ctk.CTkButton(
            quick_frame,
            text="Grayscale",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            command=lambda: self._on_grayscale() if self._on_grayscale else None,
        ).pack(side="left", expand=True, fill="x", padx=(0, 2))
        
        ctk.CTkButton(
            quick_frame,
            text="Invert",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            command=lambda: self._on_invert() if self._on_invert else None,
        ).pack(side="left", expand=True, fill="x", padx=(2, 0))

    def _create_slider(
        self,
        parent,
        label: str,
        key: str,
        from_: int,
        to: int,
        default: int
    ) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            header,
            text=str(default),
            font=ctk.CTkFont(family="Consolas", size=11),
        )
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(
            frame,
            from_=from_,
            to=to,
            number_of_steps=to - from_,
        )
        slider.set(default)
        slider.pack(fill="x", pady=2)
        
        # Update label on change
        slider.configure(command=lambda v, lbl=value_label: lbl.configure(text=f"{int(v)}"))
        
        self._sliders[key] = (slider, value_label, default)

    def _apply_adjustments(self) -> None:
        """Collect all slider values and pass to the callback."""
        brightness = int(self._sliders["brightness"][0].get())
        contrast = int(self._sliders["contrast"][0].get())
        saturation = int(self._sliders["saturation"][0].get())
        
        if self._on_apply_adjustments:
            self._on_apply_adjustments(brightness, contrast, saturation)

    def _reset_sliders(self) -> None:
        """Reset all sliders to their default values."""
        for key, (slider, label, default) in self._sliders.items():
            slider.set(default)
            label.configure(text=str(default))


class FilterPanel(CollapsiblePanel):
    """Panel for filter effects."""

    def __init__(
        self,
        master,
        on_blur: Optional[Callable] = None,
        on_sharpen: Optional[Callable] = None,
        on_edge: Optional[Callable] = None,
        on_emboss: Optional[Callable] = None,
        on_posterize: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, title="FILTERS", **kwargs)
        
        self._callbacks = {
            "blur": on_blur,
            "sharpen": on_sharpen,
            "edge": on_edge,
            "emboss": on_emboss,
            "posterize": on_posterize,
        }
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        content = self.content
        
        filters = [
            ("blur", "Blur", "#5e60ce"),
            ("sharpen", "Sharpen", "#7400b8"),
            ("edge", "Edge Detect", "#6930c3"),
            ("emboss", "Emboss", "#5390d9"),
            ("posterize", "Posterize", "#4ea8de"),
        ]
        
        for key, text, color in filters:
            ctk.CTkButton(
                content,
                text=text,
                height=32,
                font=ctk.CTkFont(size=12),
                fg_color=color,
                hover_color=self._darken_color(color),
                command=partial(self._apply_filter, key),
            ).pack(fill="x", pady=2)

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _apply_filter(self, key: str) -> None:
        callback = self._callbacks.get(key)
        if callback:
            callback()


class HistoryPanel(CollapsiblePanel):
    """Panel for undo/redo controls."""

    def __init__(
        self,
        master,
        on_undo: Optional[Callable] = None,
        on_redo: Optional[Callable] = None,
        on_reset: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, title="HISTORY", **kwargs)
        
        self._on_undo = on_undo
        self._on_redo = on_redo
        self._on_reset = on_reset
        
        self._undo_btn: Optional[ctk.CTkButton] = None
        self._redo_btn: Optional[ctk.CTkButton] = None
        self._status_label: Optional[ctk.CTkLabel] = None
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        content = self.content
        
        # Status label
        self._status_label = ctk.CTkLabel(
            content,
            text="No history",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#666666",
        )
        self._status_label.pack(anchor="w", pady=(0, 8))
        
        # Undo/Redo buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=2)
        
        self._undo_btn = ctk.CTkButton(
            btn_frame,
            text="↶ Undo",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            state="disabled",
            command=lambda: self._on_undo() if self._on_undo else None,
        )
        self._undo_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
        
        self._redo_btn = ctk.CTkButton(
            btn_frame,
            text="↷ Redo",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            state="disabled",
            command=lambda: self._on_redo() if self._on_redo else None,
        )
        self._redo_btn.pack(side="left", expand=True, fill="x", padx=(2, 0))
        
        # Reset button
        ctk.CTkButton(
            content,
            text="Reset to Original",
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#e63946",
            hover_color="#d62828",
            command=lambda: self._on_reset() if self._on_reset else None,
        ).pack(fill="x", pady=(8, 0))

    def update_state(self, undo_count: int, redo_count: int) -> None:
        """Update button states based on history."""
        if self._undo_btn:
            self._undo_btn.configure(
                state="normal" if undo_count > 0 else "disabled"
            )
        
        if self._redo_btn:
            self._redo_btn.configure(
                state="normal" if redo_count > 0 else "disabled"
            )
        
        if self._status_label:
            if undo_count == 0 and redo_count == 0:
                text = "No history"
            else:
                text = f"{undo_count} undo | {redo_count} redo"
            self._status_label.configure(text=text)
