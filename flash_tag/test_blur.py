import cv2
import numpy as np
import os
import sys

# Add parent directory to path to allow absolute imports from flash_tag package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flash_tag.generator import generate_flash_tag
from flash_tag.detector import FlashTagDetector

def apply_motion_blur(image, size=15, angle=45):
    """
    Applies synthetic motion blur to an image.
    """
    k = np.zeros((size, size))
    center = size // 2
    matrix = cv2.getRotationMatrix2D((center, center), angle, 1)
    k[center, :] = 1
    k = cv2.warpAffine(k, matrix, (size, size))
    k = k / np.sum(k)
    return cv2.filter2D(image, -1, k)

def test_system():
    test_cases = [
        {"id": 42, "blur_size": 15, "blur_angle": 30},
        {"id": 123, "blur_size": 35, "blur_angle": 0},  # Horizontal blur
        {"id": 255, "blur_size": 45, "blur_angle": 90}, # Vertical blur
        {"id": 7, "blur_size": 25, "blur_angle": 135}   # Diagonal blur
    ]
    detector = FlashTagDetector()

    for case in test_cases:
        tid = case["id"]
        b_size = case["blur_size"]
        b_angle = case["blur_angle"]
        print(f"\nTesting Tag ID: {tid} | Blur: {b_size}px @ {b_angle}deg")

        # 1. Generate Tag
        pil_img = generate_flash_tag(tid)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_GRAY2BGR)

        # 2. Add Background
        bg = np.ones((1000, 1000, 3), dtype=np.uint8) * 180
        h, w = img.shape[:2]
        yoff, xoff = 250, 250
        bg[yoff:yoff+h, xoff:xoff+w] = img

        # 3. Apply Motion Blur
        blurred = apply_motion_blur(bg, size=b_size, angle=b_angle)

        # 4. Detect
        results = detector.detect(blurred)

        if results:
            detected_id = results[0]['id']
            print(f"Result: SUCCESS (Detected ID: {detected_id})")
            if detected_id != tid:
                print(f"CRITICAL ERROR: ID Mismatch! Expected {tid}, got {detected_id}")
        else:
            print("Result: FAILED (No tag detected)")

if __name__ == "__main__":
    test_system()
