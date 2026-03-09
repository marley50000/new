import math
from PIL import Image, ImageDraw

def generate_flash_tag(tag_id, size=500):
    """
    Generates a FlashTag with Manchester encoding for robustness.
    Sync: 111 (Black, Black, Black)
    Data: 8 bits encoded as 16 segments (0->01, 1->10)
    Total segments: 3 + 16 = 19
    """
    img = Image.new('L', (size, size), color=255)
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = size // 2 - 10

    # Outer Locator Ring
    draw.ellipse([center - radius, center - radius, center + radius, center + radius], fill=0)
    inner_radius = int(radius * 0.85)
    draw.ellipse([center - inner_radius, center - inner_radius, center + inner_radius, center + inner_radius], fill=255)

    # Data Ring
    data_outer = int(radius * 0.75)
    data_inner = int(radius * 0.50)

    # Manchester Encoding
    binary_id = format(tag_id % 256, '08b')
    segments = [1, 1, 1] # Sync
    for bit in binary_id:
        if bit == '0':
            segments.extend([0, 1]) # 0 -> White, Black
        else:
            segments.extend([1, 0]) # 1 -> Black, White

    num_segments = len(segments)
    angle_step = 360 / num_segments

    for i, val in enumerate(segments):
        start_angle = i * angle_step - angle_step/2
        end_angle = (i + 1) * angle_step - angle_step/2
        color = 0 if val == 1 else 255
        draw.pieslice([center - data_outer, center - data_outer, center + data_outer, center + data_outer],
                      start=start_angle, end=end_angle, fill=color)

    # Center
    draw.ellipse([center - data_inner, center - data_inner, center + data_inner, center + data_inner], fill=255)

    return img

if __name__ == "__main__":
    import sys
    tid = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"tag_{tid}.png"
    tag_img = generate_flash_tag(tid)
    tag_img.save(output_path)
    print(f"Generated Manchester-encoded FlashTag with ID {tid} at {output_path}")
