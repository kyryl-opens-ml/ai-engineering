#!/usr/bin/env python3
"""One-off script to generate diagrams for Agent (dynamic) and Business Process (static)."""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Configuration
OUTPUT_DIR = Path(__file__).parent / "images"
AGENT_GIF_PATH = OUTPUT_DIR / "agent-flow.gif"
BP_PNG_PATH = OUTPUT_DIR / "business-process.png"
NUM_FRAMES = 8
FRAME_DURATION_MS = 1000
SCALE = 3  # High resolution scale factor

# Base dimensions (will be multiplied by SCALE)
BASE_WIDTH = 1200
BASE_HEIGHT = 200
PADDING_TOP = 70
PADDING_LEFT = 40

# Colors (RGB)
COLORS = {
    "bg": (241, 245, 249),  # slate-100 - light blue/gray
    "input": (187, 247, 208),  # green-200
    "input_border": (134, 239, 172),  # green-300
    "step": (191, 219, 254),  # blue-200
    "step_border": (147, 197, 253),  # blue-300
    "branch": (233, 213, 255),  # purple-200
    "branch_border": (216, 180, 254),  # purple-300
    "output": (255, 255, 255),  # white
    "output_border": (226, 232, 240),  # slate-200
    "text": (30, 41, 59),  # slate-800
    "text_light": (71, 85, 105),  # slate-600
    "arrow": (148, 163, 184),  # slate-400
    "title": (15, 23, 42),  # slate-900
}

# Box dimensions (base, will be scaled)
BOX_W = 100
BOX_H = 48
BOX_H_SMALL = 38
GAP = 16
ARROW_W = 36
RADIUS = 10


def generate_flow() -> list[dict]:
    """Generate a random agent flow with branches."""
    count = random.randint(4, 6)
    branches = set()
    num_branches = random.randint(1, 2)
    while len(branches) < num_branches and len(branches) < count:
        branches.add(random.randint(0, count - 1))

    return [{"name": f"Step {i + 1}", "branch": i in branches} for i in range(count)]


def draw_box(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    fill_color: tuple,
    border_color: tuple,
    text: str,
    font: ImageFont.FreeTypeFont,
    scale: int,
) -> None:
    """Draw a rounded box with text."""
    radius = RADIUS * scale
    border_width = 2 * scale
    
    # Draw border (slightly larger rounded rect)
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=radius,
        fill=border_color,
    )
    # Draw inner fill
    draw.rounded_rectangle(
        [x + border_width, y + border_width, x + w - border_width, y + h - border_width],
        radius=radius - border_width,
        fill=fill_color,
    )
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = x + (w - text_w) // 2
    text_y = y + (h - text_h) // 2
    draw.text((text_x, text_y), text, fill=COLORS["text"], font=font)


def draw_arrow(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int) -> None:
    """Draw an arrow using lines."""
    arrow_len = 20 * scale
    arrow_head = 8 * scale
    line_width = 2 * scale
    
    # Arrow line
    x_start = x
    x_end = x + arrow_len
    draw.line([(x_start, y), (x_end, y)], fill=COLORS["arrow"], width=line_width)
    
    # Arrow head
    draw.polygon(
        [
            (x_end + arrow_head, y),
            (x_end, y - arrow_head // 2),
            (x_end, y + arrow_head // 2),
        ],
        fill=COLORS["arrow"],
    )


def render_frame(flow: list[dict], scale: int) -> Image.Image:
    """Render a single frame of the agent flow."""
    width = BASE_WIDTH * scale
    height = BASE_HEIGHT * scale
    
    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24 * scale)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16 * scale)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14 * scale)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font = font_title
        font_small = font_title

    # Draw title
    title = "Agent (dynamic)"
    draw.text((PADDING_LEFT * scale, 20 * scale), "Agent", fill=COLORS["title"], font=font_title)
    # Draw "(dynamic)" in lighter color
    title_bbox = draw.textbbox((0, 0), "Agent ", font=font_title)
    draw.text(
        (PADDING_LEFT * scale + title_bbox[2], 20 * scale),
        "(dynamic)",
        fill=COLORS["text_light"],
        font=font_title,
    )

    x = PADDING_LEFT * scale
    y_center = PADDING_TOP * scale + (height - PADDING_TOP * scale) // 2

    box_w = BOX_W * scale
    box_h = BOX_H * scale
    box_h_small = BOX_H_SMALL * scale
    gap = GAP * scale
    arrow_w = ARROW_W * scale

    # Draw Input box
    draw_box(
        draw, x, y_center - box_h // 2, box_w, box_h,
        COLORS["input"], COLORS["input_border"], "Input", font, scale
    )
    x += box_w + gap

    # Draw arrow
    draw_arrow(draw, x, y_center, scale)
    x += arrow_w

    # Draw steps
    for step in flow:
        if step["branch"]:
            # Draw two stacked boxes for branch
            y_top = y_center - box_h_small - 4 * scale
            y_bot = y_center + 4 * scale
            draw_box(
                draw, x, y_top, box_w, box_h_small,
                COLORS["step"], COLORS["step_border"], f"{step['name']}a", font_small, scale
            )
            draw_box(
                draw, x, y_bot, box_w, box_h_small,
                COLORS["branch"], COLORS["branch_border"], f"{step['name']}b", font_small, scale
            )
        else:
            draw_box(
                draw, x, y_center - box_h // 2, box_w, box_h,
                COLORS["step"], COLORS["step_border"], step["name"], font, scale
            )

        x += box_w + gap
        draw_arrow(draw, x, y_center, scale)
        x += arrow_w

    # Draw Output box
    draw_box(
        draw, x, y_center - box_h // 2, box_w, box_h,
        COLORS["output"], COLORS["output_border"], "Output", font, scale
    )

    return img


def render_business_process(scale: int) -> Image.Image:
    """Render the static Business Process diagram."""
    width = BASE_WIDTH * scale
    height = BASE_HEIGHT * scale
    
    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24 * scale)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16 * scale)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font = font_title

    # Draw title - "Business Process" bold, "(static)" lighter
    draw.text((PADDING_LEFT * scale, 20 * scale), "Business Process", fill=COLORS["title"], font=font_title)
    title_bbox = draw.textbbox((0, 0), "Business Process ", font=font_title)
    draw.text(
        (PADDING_LEFT * scale + title_bbox[2], 20 * scale),
        "(static)",
        fill=COLORS["text_light"],
        font=font_title,
    )

    x = PADDING_LEFT * scale
    y_center = PADDING_TOP * scale + (height - PADDING_TOP * scale) // 2

    box_w = BOX_W * scale
    box_h = BOX_H * scale
    gap = GAP * scale
    arrow_w = ARROW_W * scale

    # Static flow: Input → Step 1 → Step 2 → Step 3 → Output
    steps = ["Input", "Step 1", "Step 2", "Step 3", "Output"]
    
    for i, step_name in enumerate(steps):
        # Choose colors based on step type
        if step_name == "Input":
            fill_color = COLORS["input"]
            border_color = COLORS["input_border"]
        elif step_name == "Output":
            fill_color = COLORS["output"]
            border_color = COLORS["output_border"]
        else:
            fill_color = (229, 231, 235)  # gray-200
            border_color = (209, 213, 219)  # gray-300
        
        draw_box(
            draw, x, y_center - box_h // 2, box_w, box_h,
            fill_color, border_color, step_name, font, scale
        )
        x += box_w + gap
        
        # Draw arrow (except after last step)
        if i < len(steps) - 1:
            draw_arrow(draw, x, y_center, scale)
            x += arrow_w

    return img


def main() -> None:
    """Generate all diagrams."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate Business Process PNG
    print("Generating Business Process (static) PNG...")
    bp_img = render_business_process(SCALE)
    bp_img.save(BP_PNG_PATH)
    print(f"  Saved: {BP_PNG_PATH} ({bp_img.width}x{bp_img.height})")
    
    # Generate 3 Agent PNGs for platforms without GIF support
    print("\nGenerating 3 Agent (dynamic) PNGs...")
    for i in range(3):
        flow = generate_flow()
        frame = render_frame(flow, SCALE)
        png_path = OUTPUT_DIR / f"agent-flow-{i + 1}.png"
        frame.save(png_path)
        print(f"  Saved: {png_path} ({len(flow)} steps, {sum(1 for s in flow if s['branch'])} branches)")
    
    # Generate Agent GIF
    print(f"\nGenerating Agent (dynamic) GIF with {NUM_FRAMES} frames...")
    frames = []
    for i in range(NUM_FRAMES):
        flow = generate_flow()
        frame = render_frame(flow, SCALE)
        frames.append(frame)
        print(f"  Frame {i + 1}: {len(flow)} steps, {sum(1 for s in flow if s['branch'])} branches")

    frames[0].save(
        AGENT_GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=False,
    )
    print(f"  Saved: {AGENT_GIF_PATH} ({frames[0].width}x{frames[0].height})")


if __name__ == "__main__":
    main()
