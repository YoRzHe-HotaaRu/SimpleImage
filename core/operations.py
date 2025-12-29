"""
Image operations module.

Implements the command pattern for image manipulations,
enabling undo/redo functionality.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class Operation(ABC):
    """Abstract base class for all image operations."""

    def __init__(self, name: str):
        self.name = name
        self._backup: Optional[Image.Image] = None

    @abstractmethod
    def execute(self, image: Image.Image) -> Image.Image:
        """Apply the operation to the image and return result."""
        pass

    def backup(self, image: Image.Image) -> None:
        """Store a backup of the image for undo."""
        self._backup = image.copy()

    def restore(self) -> Optional[Image.Image]:
        """Return the backed up image."""
        return self._backup


class ResizeOperation(Operation):
    """Resize image by percentage or to specific dimensions."""

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        percentage: Optional[float] = None,
        maintain_aspect: bool = True,
    ):
        super().__init__("Resize")
        self.width = width
        self.height = height
        self.percentage = percentage
        self.maintain_aspect = maintain_aspect

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        
        if self.percentage is not None:
            new_width = int(image.width * self.percentage / 100)
            new_height = int(image.height * self.percentage / 100)
        elif self.width and self.height:
            if self.maintain_aspect:
                # Calculate to fit within bounds while maintaining aspect
                ratio = min(self.width / image.width, self.height / image.height)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
            else:
                new_width = self.width
                new_height = self.height
        elif self.width:
            ratio = self.width / image.width
            new_width = self.width
            new_height = int(image.height * ratio)
        elif self.height:
            ratio = self.height / image.height
            new_width = int(image.width * ratio)
            new_height = self.height
        else:
            return image

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


class RotateOperation(Operation):
    """Rotate image by specified angle."""

    def __init__(self, angle: float, expand: bool = True):
        super().__init__("Rotate")
        self.angle = angle
        self.expand = expand

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        return image.rotate(self.angle, expand=self.expand, resample=Image.Resampling.BICUBIC)


class FlipOperation(Operation):
    """Flip image horizontally or vertically."""

    def __init__(self, horizontal: bool = True):
        super().__init__("Flip")
        self.horizontal = horizontal

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        if self.horizontal:
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


class CropOperation(Operation):
    """Crop image to specified rectangle."""

    def __init__(self, left: int, top: int, right: int, bottom: int):
        super().__init__("Crop")
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        # Ensure bounds are within image
        left = max(0, min(self.left, image.width))
        top = max(0, min(self.top, image.height))
        right = max(left, min(self.right, image.width))
        bottom = max(top, min(self.bottom, image.height))
        
        return image.crop((left, top, right, bottom))


class BrightnessOperation(Operation):
    """Adjust image brightness."""

    def __init__(self, factor: float):
        """
        Args:
            factor: 0.0 gives black, 1.0 gives original, > 1.0 brightens.
        """
        super().__init__("Brightness")
        self.factor = factor

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(self.factor)


class ContrastOperation(Operation):
    """Adjust image contrast."""

    def __init__(self, factor: float):
        """
        Args:
            factor: 0.0 gives grey, 1.0 gives original, > 1.0 increases contrast.
        """
        super().__init__("Contrast")
        self.factor = factor

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(self.factor)


class SaturationOperation(Operation):
    """Adjust image saturation (color intensity)."""

    def __init__(self, factor: float):
        """
        Args:
            factor: 0.0 gives grayscale, 1.0 gives original, > 1.0 increases saturation.
        """
        super().__init__("Saturation")
        self.factor = factor

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(self.factor)


class GrayscaleOperation(Operation):
    """Convert image to grayscale."""

    def __init__(self):
        super().__init__("Grayscale")

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        # Convert to grayscale and back to RGB for consistency
        return image.convert("L").convert("RGB")


class InvertOperation(Operation):
    """Invert image colors."""

    def __init__(self):
        super().__init__("Invert")

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        # Handle images with alpha channel
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb_image = Image.merge("RGB", (r, g, b))
            inverted = ImageOps.invert(rgb_image)
            r2, g2, b2 = inverted.split()
            return Image.merge("RGBA", (r2, g2, b2, a))
        elif image.mode == "RGB":
            return ImageOps.invert(image)
        else:
            # Convert to RGB, invert, then convert back
            rgb_image = image.convert("RGB")
            return ImageOps.invert(rgb_image)


class BlurOperation(Operation):
    """Apply blur effect to image."""

    def __init__(self, radius: float = 2.0, gaussian: bool = True):
        super().__init__("Blur")
        self.radius = radius
        self.gaussian = gaussian

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        if self.gaussian:
            return image.filter(ImageFilter.GaussianBlur(radius=self.radius))
        else:
            return image.filter(ImageFilter.BoxBlur(radius=self.radius))


class SharpenOperation(Operation):
    """Apply sharpen effect to image."""

    def __init__(self, amount: float = 1.0):
        super().__init__("Sharpen")
        self.amount = amount

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        if self.amount <= 1.0:
            return image.filter(ImageFilter.SHARPEN)
        else:
            # Apply sharpen multiple times for stronger effect
            result = image
            for _ in range(int(self.amount)):
                result = result.filter(ImageFilter.SHARPEN)
            return result


class EdgeDetectOperation(Operation):
    """Apply edge detection filter."""

    def __init__(self):
        super().__init__("Edge Detect")

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        return image.filter(ImageFilter.FIND_EDGES)


class EmbossOperation(Operation):
    """Apply emboss effect to image."""

    def __init__(self):
        super().__init__("Emboss")

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        return image.filter(ImageFilter.EMBOSS)


class PosterizeOperation(Operation):
    """Reduce number of colors in image."""

    def __init__(self, bits: int = 4):
        """
        Args:
            bits: Number of bits to keep per channel (1-8).
        """
        super().__init__("Posterize")
        self.bits = max(1, min(8, bits))

    def execute(self, image: Image.Image) -> Image.Image:
        self.backup(image)
        # Handle images with alpha channel
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb_image = Image.merge("RGB", (r, g, b))
            posterized = ImageOps.posterize(rgb_image, self.bits)
            r2, g2, b2 = posterized.split()
            return Image.merge("RGBA", (r2, g2, b2, a))
        elif image.mode == "RGB":
            return ImageOps.posterize(image, self.bits)
        else:
            rgb_image = image.convert("RGB")
            return ImageOps.posterize(rgb_image, self.bits)
