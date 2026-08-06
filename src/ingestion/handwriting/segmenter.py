from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw
import cv2

class RegionType(str, Enum):
    TEXT_BLOCK = "text_block"
    BLOCK_MATH = "block_math"
    DIAGRAM = "diagram"

@dataclass
class RegionBox:
    box: Tuple[int, int, int, int]  # (xmin, ymin, xmax, ymax)
    region_type: RegionType
    confidence: float
    cropped_image: Image.Image

class CoarseLayoutSegmenter:
    """
    Performs coarse document layout analysis (DLA) on handwritten note pages.
    Segments pages into coarse blocks (TEXT_BLOCK, BLOCK_MATH, DIAGRAM) and splits
    large text blocks into line-level crops for high-precision TrOCR recognition.
    """

    def __init__(self, min_region_area: int = 400):
        self.min_region_area = min_region_area

    def segment(self, image: Image.Image) -> List[RegionBox]:
        """
        Segments a preprocessed PIL image into an ordered list of line-level and block-level RegionBox objects.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15
        )

        # Scale morphological kernel dynamically based on image resolution
        kw = max(15, int(width * 0.02))
        kh = max(5, int(height * 0.005))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
        dilated = cv2.dilate(binary, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw_boxes = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h

            if area < self.min_region_area or w < 30 or h < 15:
                continue

            aspect_ratio = w / float(h)
            roi_binary = binary[y:y+h, x:x+w]
            ink_density = np.sum(roi_binary > 0) / float(area)

            if aspect_ratio > 3.0 and w > width * 0.35 and h > 40 and ink_density < 0.2:
                rtype = RegionType.BLOCK_MATH
            elif aspect_ratio < 2.0 and w > width * 0.3 and h > height * 0.15 and ink_density > 0.15:
                rtype = RegionType.DIAGRAM
            else:
                rtype = RegionType.TEXT_BLOCK

            crop = image.crop((x, y, x + w, y + h))
            
            # If TEXT_BLOCK is tall (contains multiple lines), split into line strips for TrOCR
            if rtype == RegionType.TEXT_BLOCK and h > 60:
                sub_lines = self._split_text_block_into_lines(crop, x, y)
                raw_boxes.extend(sub_lines)
            else:
                raw_boxes.append(RegionBox(
                    box=(x, y, x + w, y + h),
                    region_type=rtype,
                    confidence=0.9,
                    cropped_image=crop
                ))

        sorted_boxes = self._sort_reading_order(raw_boxes)

        if not sorted_boxes:
            # Fallback: line split full page
            sorted_boxes = self._split_text_block_into_lines(image, 0, 0)

        return sorted_boxes

    @staticmethod
    def draw_annotated_boxes(image: Image.Image, boxes: List[RegionBox]) -> Image.Image:
        """
        Draws bounding box annotations on the page image for step-by-step visual debugging.
        """
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        color_map = {
            RegionType.TEXT_BLOCK: (0, 128, 255),    # Blue
            RegionType.BLOCK_MATH: (255, 0, 128),    # Pink
            RegionType.DIAGRAM: (0, 200, 0)         # Green
        }

        for idx, reg in enumerate(boxes, start=1):
            color = color_map.get(reg.region_type, (255, 255, 0))
            draw.rectangle(reg.box, outline=color, width=2)
            draw.text((reg.box[0] + 4, max(0, reg.box[1] - 12)), f"[{idx}] {reg.region_type.value}", fill=color)

        return annotated

    @staticmethod
    def _split_text_block_into_lines(image: Image.Image, offset_x: int, offset_y: int) -> List[RegionBox]:
        """
        Splits a text block image into line strips using horizontal projection profile.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        row_sums = np.sum(binary > 0, axis=1)
        h, w = binary.shape

        line_boxes = []
        in_line = False
        start_y = 0
        min_line_height = 15

        for y, val in enumerate(row_sums):
            if val > (w * 0.02) and not in_line:
                in_line = True
                start_y = max(0, y - 5)
            elif val <= (w * 0.02) and in_line:
                end_y = min(h, y + 5)
                if (end_y - start_y) >= min_line_height:
                    crop = image.crop((0, start_y, w, end_y))
                    line_boxes.append(RegionBox(
                        box=(offset_x, offset_y + start_y, offset_x + w, offset_y + end_y),
                        region_type=RegionType.TEXT_BLOCK,
                        confidence=0.9,
                        cropped_image=crop
                    ))
                in_line = False

        if in_line and (h - start_y) >= min_line_height:
            crop = image.crop((0, start_y, w, h))
            line_boxes.append(RegionBox(
                box=(offset_x, offset_y + start_y, offset_x + w, offset_y + h),
                region_type=RegionType.TEXT_BLOCK,
                confidence=0.9,
                cropped_image=crop
            ))

        if not line_boxes:
            line_boxes.append(RegionBox(
                box=(offset_x, offset_y, offset_x + w, offset_y + h),
                region_type=RegionType.TEXT_BLOCK,
                confidence=1.0,
                cropped_image=image
            ))

        return line_boxes

    @staticmethod
    def _sort_reading_order(boxes: List[RegionBox], y_threshold: int = 35) -> List[RegionBox]:
        """
        Sorts bounding boxes into natural reading order (top-to-bottom, left-to-right).
        """
        if not boxes:
            return []

        boxes = sorted(boxes, key=lambda b: b.box[1])
        lines: List[List[RegionBox]] = []
        curr_line: List[RegionBox] = [boxes[0]]

        for box in boxes[1:]:
            prev_y = curr_line[-1].box[1]
            if abs(box.box[1] - prev_y) <= y_threshold:
                curr_line.append(box)
            else:
                lines.append(sorted(curr_line, key=lambda b: b.box[0]))
                curr_line = [box]

        if curr_line:
            lines.append(sorted(curr_line, key=lambda b: b.box[0]))

        return [box for line in lines for box in line]
