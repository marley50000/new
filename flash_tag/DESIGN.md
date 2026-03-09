# FlashTag Design Specification

FlashTag is a high-speed, motion-blur-robust fiducial marker system designed for indoor navigation in robotics and high-velocity environments.

## Geometry
- **Shape**: Circular. Circular markers are ideal for motion blur because their projection (an ellipse) maintains a reliable centroid and symmetry even when blurred along a vector.
- **Concentric Rings**:
    - **Outer Ring (Locator)**: A thick black ring that serves as the primary detection feature.
    - **Data Rings**: One or more internal rings divided into angular segments (bits).
    - **Orientation Marker**: A specific gap or a distinct segment in one of the rings to determine the rotation of the tag.

## Encoding
- Each data ring is divided into $N$ segments.
- Each segment represents one bit (Black = 0, White = 1).
- Total ID capacity = $2^N$. For 8 segments, we have 256 unique IDs.

## Detection Algorithm
1. **Binarization**: Adaptive thresholding to handle uneven lighting.
2. **Contour Analysis**: Find contours and filter for elliptical shapes using `cv2.fitEllipse`.
3. **Normalization**: Transform the elliptical region into a canonical circular frame.
4. **Radial Sampling**: Sample the intensity at specific angles and radii to decode the bit sequence.
5. **ID Validation**: Use a parity bit or simple checksum for robustness.

## Advantages
- **Fast Scanning**: Ellipse fitting is computationally efficient and robust to moderate blur.
- **Omnidirectional**: Works from various angles (within limits of ellipse deformation).
- **Simplicity**: Easy to print and deploy.
