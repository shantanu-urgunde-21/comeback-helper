import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

class ImagePreprocessor:
    """
    Image preprocessing pipeline for handwritten notes.
    Performs shadow removal, contrast enhancement, noise reduction, and deskewing
    to prepare images for layout analysis and OCR extraction.
    """

    def __init__(self, target_dpi: int = 300):
        self.target_dpi = target_dpi

    def preprocess_pil(self, image: Image.Image) -> Image.Image:
        """
        Main entry point: takes a PIL Image of a handwritten note page and returns an optimized PIL Image.
        """
        # Convert PIL Image to OpenCV format (BGR)
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)

        # 1. Remove background shadows & paper noise
        shadow_free = self.remove_shadows(cv_img)

        # 2. Adaptive contrast enhancement
        enhanced = self.enhance_contrast(shadow_free)

        # 3. Deskew image if rotated
        deskewed = self.deskew(enhanced)

        # Convert back to PIL Image
        rgb_img = cv2.cvtColor(deskewed, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_img)

    @staticmethod
    def remove_shadows(img: np.ndarray) -> np.ndarray:
        """
        Removes uneven background lighting and page shadows using morphological dilation.
        """
        rgb_planes = cv2.split(img)
        result_planes = []
        for plane in rgb_planes:
            dilated = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(norm_img)
        return cv2.merge(result_planes)

    @staticmethod
    def enhance_contrast(img: np.ndarray) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L channel of LAB color space.
        """
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    @staticmethod
    def deskew(img: np.ndarray) -> np.ndarray:
        """
        Detects text line orientation angle and deskews image if angle > 0.5 degrees.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return img

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        if abs(angle) < 0.5 or abs(angle) > 15.0:
            return img

        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
