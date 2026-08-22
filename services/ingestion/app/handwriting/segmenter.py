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
    Line & Block Layout Segmenter for handwritten STEM notes.
    Merges word micro-boxes into unified full-line sentence strips and block math equations.
    Prevents over-segmentation artifacts.
    """

    def __init__(self, min_region_area: int = 600):
        self.min_region_area = min_region_area

    def segment(self, image: Image.Image) -> List[RegionBox]:
        """
        Segments a preprocessed PIL image into an ordered list of full-line sentence strips and block math boxes.
        """
        cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        # Otsu thresholding on preprocessed image (r-channel)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Horizontal dilation to merge adjacent words on the same line into full sentence strips
        kw = max(35, int(width * 0.04))
        kh = max(4, int(height * 0.004))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh))
        dilated = cv2.dilate(binary, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw_boxes = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h

            # Filter out tiny noise dots, isolated line fragments, and thin line rules
            if area < self.min_region_area or w < 40 or h < 18:
                continue

            aspect_ratio = w / float(h)
            roi_binary = binary[y:y+h, x:x+w]
            ink_density = np.sum(roi_binary > 0) / float(area)

            # Classify equation vs text line vs diagram
            if aspect_ratio > 2.5 and w > width * 0.3 and h > 35 and ink_density < 0.22:
                rtype = RegionType.BLOCK_MATH
            elif aspect_ratio < 2.0 and w > width * 0.25 and h > height * 0.12 and ink_density > 0.15:
                rtype = RegionType.DIAGRAM
            else:
                rtype = RegionType.TEXT_BLOCK

            crop = image.crop((x, y, x + w, y + h))
            raw_boxes.append((x, y, x + w, y + h, rtype, crop))

        # Merge overlapping or vertically adjacent line boxes on the same line level
        merged_region_boxes = self._merge_adjacent_lines(image, raw_boxes)
        sorted_boxes = self._sort_reading_order(merged_region_boxes)

        if not sorted_boxes:
            # Fallback: single page box
            sorted_boxes = [RegionBox(
                box=(0, 0, width, height),
                region_type=RegionType.TEXT_BLOCK,
                confidence=1.0,
                cropped_image=image
            )]

        return sorted_boxes

    def _merge_adjacent_lines(self, canvas: Image.Image, boxes_data: list) -> List[RegionBox]:
        """
        Merges boxes that belong to the same text line to form continuous sentence crops.
        """
        if not boxes_data:
            return []

        # Sort by ymin
        sorted_raw = sorted(boxes_data, key=lambda b: b[1])
        merged = []

        for x1, y1, x2, y2, rtype, crop in sorted_raw:
            if not merged:
                merged.append([x1, y1, x2, y2, rtype, crop])
                continue

            prev = merged[-1]
            prev_x1, prev_y1, prev_x2, prev_y2, prev_rtype, _ = prev

            # Check vertical overlap / proximity (same line level)
            y_overlap = min(y2, prev_y2) - max(y1, prev_y1)
            y_dist = abs(y1 - prev_y1)

            if (y_overlap > 10 or y_dist < 18) and rtype == prev_rtype and rtype == RegionType.TEXT_BLOCK:
                # Merge into a single line box
                new_x1 = min(prev_x1, x1)
                new_y1 = min(prev_y1, y1)
                new_x2 = max(prev_x2, x2)
                new_y2 = max(prev_y2, y2)
                merged[-1] = [new_x1, new_y1, new_x2, new_y2, rtype, None]
            else:
                merged.append([x1, y1, x2, y2, rtype, crop])

        final_boxes = []
        for bx1, by1, bx2, by2, brtype, bcrop in merged:
            final_crop = bcrop if bcrop is not None else canvas.crop((bx1, by1, bx2, by2))
            final_boxes.append(RegionBox(
                box=(bx1, by1, bx2, by2),
                region_type=brtype,
                confidence=0.9,
                cropped_image=final_crop
            ))

        return final_boxes

    def _sort_reading_order(self, boxes: List[RegionBox]) -> List[RegionBox]:
        """
        Sorts line boxes top-to-bottom.
        """
        if not boxes:
            return []

        sorted_items = sorted(boxes, key=lambda b: b.box[1])
        return sorted_items

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
