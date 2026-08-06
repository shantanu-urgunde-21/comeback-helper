import numpy as np
from PIL import Image
import cv2

class ImagePreprocessor:
    """
    Image preprocessing pipeline for handwritten STEM notes on ruled/grid notebook paper.
    Removes blue/cyan notebook ruling lines using channel thresholding while keeping ink text sharp.
    """

    def __init__(self, target_dpi: int = 200):
        self.target_dpi = target_dpi

    def preprocess_pil(self, image: Image.Image) -> Image.Image:
        """
        Takes a PIL Image of a handwritten notebook page and returns an optimized image with ruling lines removed.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)

        # 1. Remove blue/cyan notebook ruling lines
        # Blue lines are high in Blue channel, low in Red. Extract Red channel to erase blue lines.
        b, g, r = cv2.split(cv_img)

        # 2. Contrast adjustment on Red channel (where notebook lines disappear)
        # Apply gentle CLAHE to sharpen ink without creating dot noise
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(r)

        # Convert back to 3-channel RGB PIL Image
        rgb_img = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(rgb_img)
