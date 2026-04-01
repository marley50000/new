import cv2
import numpy as np
import math

class FlashTagDetector:
    def __init__(self):
        self.num_segments = 3 + 16 # 3 sync + 16 data (Manchester)

    def detect(self, image):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        results = []
        # Try a range of block sizes for adaptive thresholding to be extremely robust
        for block_size in [31, 51, 71, 91]:
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, block_size, 10)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if len(cnt) < 5: continue
                hull = cv2.convexHull(cnt)
                if len(hull) < 5: continue # Extra check for fitEllipse
                area = cv2.contourArea(hull)
                if area < 400: continue

                ellipse = cv2.fitEllipse(hull)
                (x, y), (w, h), angle = ellipse

                # Aspect ratio check (be more lenient for extreme blur)
                if min(w, h) / max(w, h) < 0.1: continue

                decoded_id = self.decode_tag(gray, ellipse)
                if decoded_id is not None:
                    duplicate = False
                    for r in results:
                        dist = math.sqrt((r['center'][0]-x)**2 + (r['center'][1]-y)**2)
                        if dist < 30:
                            duplicate = True
                            break
                    if not duplicate:
                        results.append({
                            'id': decoded_id,
                            'center': (int(x), int(y)),
                            'ellipse': ellipse
                        })

        return results

    def decode_tag(self, gray, ellipse):
        (x, y), (w, h), angle = ellipse
        # Sampling radius - use slightly larger sampling area
        a = w / 2 * 0.65
        b = h / 2 * 0.65

        intensities = []
        angle_step = 360 / self.num_segments

        phi = math.radians(angle)
        for i in range(self.num_segments):
            seg_intensities = []
            # Dense sub-sampling per segment
            for sub_angle in np.linspace(-angle_step/2.5, angle_step/2.5, 7):
                theta = math.radians(i * angle_step + sub_angle)
                sx = int(x + a * math.cos(theta) * math.cos(phi) - b * math.sin(theta) * math.sin(phi))
                sy = int(y + a * math.cos(theta) * math.sin(phi) + b * math.sin(theta) * math.cos(phi))

                if 0 <= sy < gray.shape[0] and 0 <= sx < gray.shape[1]:
                    seg_intensities.append(int(gray[sy, sx]))

            if seg_intensities:
                intensities.append(sum(seg_intensities) / len(seg_intensities))
            else:
                intensities.append(127)

        if not intensities: return None

        # Local contrast check
        local_min = min(intensities)
        local_max = max(intensities)
        if local_max - local_min < 15: return None

        adaptive_thresh = (local_min + local_max) / 2
        samples = [1 if val < adaptive_thresh else 0 for val in intensities]

        for shift in range(self.num_segments):
            shifted = samples[shift:] + samples[:shift]
            if shifted[0:3] == [1, 1, 1]:
                data_bits = shifted[3:]
                decoded_bits = ""
                valid = True
                for j in range(0, 16, 2):
                    pair = data_bits[j:j+2]
                    if pair == [0, 1]: decoded_bits += "0"
                    elif pair == [1, 0]: decoded_bits += "1"
                    else:
                        valid = False
                        break
                if valid:
                    return int(decoded_bits, 2)

        return None
