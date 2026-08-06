from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import numpy as np
from PIL import Image
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
    Segments pages into coarse blocks (TEXT_BLOCK, BLOCK_MATH, DIAGRAM).
    Keeps inline math within TEXT_BLOCK to preserve sentence context.
    """

    def __init__(self, min_region_area: int = 500):
        self.min_region_area = min_region_area

    def segment(self, image: Image.Image) -> List[RegionBox]:
        """
        Segments a preprocessed PIL image into an ordered list of RegionBox objects.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding to find connected text/math/diagram regions
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15
        )

        # Morphological dilation to merge nearby words/symbols into coarse block regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 12))
        dilated = cv2.dilate(binary, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        height, width = gray.shape
        total_area = height * width
        raw_boxes = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h

            # Filter out tiny noise contours
            if area < self.min_region_area:
                continue

            # Classify region based on aspect ratio, size, and density heuristic
            aspect_ratio = w / float(h)
            roi_binary = binary[y:y+h, x:x+w]
            ink_density = np.sum(roi_binary > 0) / float(area)

            # Classification heuristics
            if aspect_ratio > 1.2 and w > width * 0.4 and h > 50 and ink_density < 0.25:
                # Wide, low-density region -> Isolated Block Math equation
                rtype = RegionType.BLOCK_MATH
            elif aspect_ratio < 2.5 and w > width * 0.25 and h > height * 0.15 and ink_density > 0.15:
                # Large bounded region -> Diagram / Figure
                rtype = RegionType.DIAGRAM
            else:
                # Default to Text Block (preserving inline math in context)
                rtype = RegionType.TEXT_BLOCK

            crop = image.crop((x, y, x + w, y + h))
            raw_boxes.append(RegionBox(
                box=(x, y, x + w, y + h),
                region_type=rtype,
                confidence=0.9,
                cropped_image=crop
            ))

        # Sort regions in reading order: primary by top coordinate (y), secondary by left (x)
        sorted_boxes = self._sort_reading_order(raw_boxes)
        
        # Fallback: if no regions detected, return full image as TEXT_BLOCK
        if not sorted_boxes:
            sorted_boxes = [RegionBox(
                box=(0, 0, width, height),
                region_type=RegionType.TEXT_BLOCK,
                confidence=1.0,
                cropped_image=image
            )]

        return sorted_boxes

    @staticmethod
    def _sort_reading_order(boxes: List[RegionBox], y_threshold: int = 40) -> List[RegionBox]:
        """
        Sorts bounding boxes into natural reading order (top-to-bottom, left-to-right).
        Groups boxes with similar y coordinates into lines.
        """
        if not boxes:
            return []

        # Sort primarily by ymin
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

        flat_list = [box for line in lines for box in line]
        return flat_list
