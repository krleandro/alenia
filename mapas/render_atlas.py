import json
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "alenia_atlas_data.json")

FONT_BOLD = r"C:\Windows\Fonts\palab.ttf"
FONT_REG = r"C:\Windows\Fonts\pala.ttf"
FONT_ITALIC = r"C:\Windows\Fonts\palai.ttf"
FONT_BOLD_ITALIC = r"C:\Windows\Fonts\palabi.ttf"

# Antique ink & parchment palette matching GRRM atlas tone
INK_DARK = (26, 20, 14, 245)
INK_CAPITAL = (38, 22, 10, 250)
INK_REGION = (38, 28, 18, 232)
INK_LIGHT = (238, 230, 210, 245)
INK_SEA = (212, 222, 226, 215)
OUTLINE_DARK = (18, 22, 26, 215)
GOLD_ACCENT = (182, 140, 62, 245)
CRIMSON_ACCENT = (128, 34, 26, 235)
PARCHMENT_FILL = (232, 221, 196, 245)
HALO_LIGHT = (235, 226, 205, 190)
HALO_DARK = (18, 24, 30, 185)


def fractal_island_points(cx, cy, rx, ry, rot, rng, steps=44):
    # Generate deterministic organic GRRM-style jagged coastline polygon
    phases = [rng.uniform(0, math.tau) for _ in range(5)]
    amps = [0.16, 0.11, 0.08, 0.05, 0.03]
    freqs = [2, 3, 5, 8, 13]
    pts = []
    cos_r = math.cos(rot)
    sin_r = math.sin(rot)
    for i in range(steps):
        ang = (i / steps) * math.tau
        mod = 1.0
        for f, a, ph in zip(freqs, amps, phases):
            mod += a * math.sin(f * ang + ph)
        lx = rx * mod * math.cos(ang)
        ly = ry * mod * math.sin(ang)
        gx = cx + lx * cos_r - ly * sin_r
        gy = cy + lx * sin_r + ly * cos_r
        pts.append((gx, gy))
    return pts


def draw_custom_islands(base_size, custom_groups):
    w, h = base_size
    scale = 2
    layer_hi = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer_hi)

    for group in custom_groups:
        style = group.get("style", "dark_crag")
        rng = random.Random(group.get("seed", 1))

        if style == "sapphire_forest":
            # Lush emerald/sapphire vivid forest island
            coastal_tint = (146, 178, 168, 95)
            land_base = (126, 146, 102, 248)
            land_inner = (52, 118, 72, 240)
            canopy_colors = [
                (34, 96, 58, 235),
                (44, 118, 72, 230),
                (28, 82, 54, 240),
                (62, 134, 82, 220),
            ]
            shore_ink = (30, 32, 24, 235)
        elif style == "dark_frost":
            # Bleak icy/volcanic outpost (Ilha de Thanatos)
            coastal_tint = (148, 164, 174, 85)
            land_base = (98, 102, 104, 248)
            land_inner = (68, 72, 76, 235)
            canopy_colors = [
                (212, 218, 222, 195),
                (52, 56, 60, 220),
                (172, 180, 186, 180),
            ]
            shore_ink = (26, 28, 30, 240)
        else:
            # Jagged rocky archipelago (Arquipelago Ravena)
            coastal_tint = (138, 156, 164, 85)
            land_base = (128, 122, 106, 248)
            land_inner = (88, 86, 78, 230)
            canopy_colors = [
                (64, 68, 58, 220),
                (104, 98, 86, 210),
                (48, 52, 46, 230),
            ]
            shore_ink = (28, 26, 22, 240)

        for isl in group.get("islands", []):
            cx = isl["cx"] * scale
            cy = isl["cy"] * scale
            rx = isl["rx"] * scale
            ry = isl["ry"] * scale
            rot = isl.get("rot", 0.0)

            # Outer subtle shallow water & antique concentric coastal ripples
            for ring_mul, alpha_mul in [(1.48, 0.35), (1.28, 0.6), (1.14, 0.95)]:
                r_pts = fractal_island_points(cx, cy, rx * ring_mul, ry * ring_mul, rot, random.Random(rng.randint(1, 99999)), steps=44)
                c = (coastal_tint[0], coastal_tint[1], coastal_tint[2], int(coastal_tint[3] * alpha_mul))
                d.polygon(r_pts, fill=c)
                d.line(r_pts + [r_pts[0]], fill=(185, 200, 205, int(65 * alpha_mul)), width=2)

            # Main island silhouette
            pts = fractal_island_points(cx, cy, rx, ry, rot, rng, steps=48)
            d.polygon(pts, fill=land_base)

            # Inner biome fill
            inner_pts = [(cx + (px - cx) * 0.78, cy + (py - cy) * 0.78) for px, py in pts]
            d.polygon(inner_pts, fill=land_inner)

            # Engraved micro-detail: stippled forest canopies / rocky ridges / frost caps
            num_dots = max(14, int((rx * ry) / 145))
            for _ in range(num_dots):
                a = rng.uniform(0, math.tau)
                rad = math.sqrt(rng.uniform(0.0, 0.56))
                lx = rx * rad * math.cos(a)
                ly = ry * rad * math.sin(a)
                cos_r, sin_r = math.cos(rot), math.sin(rot)
                px = cx + lx * cos_r - ly * sin_r
                py = cy + lx * sin_r + ly * cos_r
                col = rng.choice(canopy_colors)
                if style == "sapphire_forest":
                    rr = rng.uniform(4.2, 8.2)
                    d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col, outline=(22, 54, 34, 150), width=1)
                elif style == "dark_frost":
                    rr = rng.uniform(3.5, 7.5)
                    tri = [(px, py - rr), (px + rr * 0.9, py + rr * 0.7), (px - rr * 0.9, py + rr * 0.7)]
                    d.polygon(tri, fill=col, outline=(32, 34, 38, 175))
                else:
                    rr = rng.uniform(3.0, 6.2)
                    tri = [(px, py - rr), (px + rr * 0.85, py + rr * 0.75), (px - rr * 0.85, py + rr * 0.75)]
                    d.polygon(tri, fill=col, outline=(30, 28, 24, 170))

            # Crisp copperplate ink shoreline
            d.line(pts + [pts[0]], fill=shore_ink, width=3, joint="curve")

    return layer_hi.resize((w, h), Image.Resampling.LANCZOS)


def draw_star(draw, cx, cy, r_outer, r_inner, points, fill, outline, width=2):
    coords = []
    for i in range(points * 2):
        angle = math.radians(i * 180 / points - 90)
        r = r_outer if i % 2 == 0 else r_inner
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(coords, fill=fill, outline=outline)
    if width > 1:
        draw.line(coords + [coords[0]], fill=outline, width=width, joint="curve")


def draw_marker(layer, x, y, mtype, scale=2):
    d = ImageDraw.Draw(layer)
    cx, cy = x * scale, y * scale

    if mtype == "capital":
        r_glow = 15 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(236, 226, 202, 165))
        r1 = 11 * scale
        r2 = 8.5 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=2 * scale)
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=GOLD_ACCENT, width=int(1.6 * scale))
        draw_star(d, cx, cy, 6.8 * scale, 2.8 * scale, 5, fill=CRIMSON_ACCENT, outline=INK_DARK, width=scale)

    elif mtype == "citadel":
        r_glow = 10.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 145))
        s = 7.0 * scale
        pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
        d.polygon(pts, fill=PARCHMENT_FILL, outline=INK_DARK)
        d.line(pts + [pts[0]], fill=INK_DARK, width=int(1.7 * scale))
        r_in = 2.6 * scale
        d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=INK_DARK)

    elif mtype == "port":
        r_glow = 9.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 145))
        r1 = 6.8 * scale
        r2 = 3.0 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.6 * scale))
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=INK_DARK)

    elif mtype == "special":
        r_glow = 10.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 155))
        r1 = 7.4 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.6 * scale))
        draw_star(d, cx, cy, 5.0 * scale, 2.1 * scale, 4, fill=INK_DARK, outline=INK_DARK, width=1)

    elif mtype in ("academy", "observatory"):
        # Refined scholarly/astronomical emblem (ring + 4-point compass cross)
        r_glow = 9.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 155))
        r1 = 6.4 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.5 * scale))
        c = 8.2 * scale if mtype == "observatory" else 5.2 * scale
        d.line([(cx - c, cy), (cx + c, cy)], fill=INK_DARK, width=int(1.4 * scale))
        d.line([(cx, cy - c), (cx, cy + c)], fill=INK_DARK, width=int(1.4 * scale))
        r_in = 2.4 * scale
        d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=GOLD_ACCENT, outline=INK_DARK, width=scale)

    elif mtype == "ruins":
        # Classic cartographic 3-stone ruin triad
        r_glow = 10 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 150))
        offsets = [(0, -4.5), (-4.6, 3.6), (4.6, 3.6)]
        s = 2.4 * scale
        for ox, oy in offsets:
            px, py = cx + ox * scale, cy + oy * scale
            d.rectangle([px - s, py - s, px + s, py + s], fill=INK_DARK, outline=PARCHMENT_FILL, width=1)

    elif mtype == "wreck":
        # Antique nautical hazard / shipwreck cross-mark
        r_glow = 9.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(228, 226, 212, 155))
        s = 5.4 * scale
        d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=CRIMSON_ACCENT, width=int(2.0 * scale))
        d.line([(cx + s, cy - s), (cx - s, cy + s)], fill=CRIMSON_ACCENT, width=int(2.0 * scale))
        r_in = 2.2 * scale
        d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=PARCHMENT_FILL, outline=INK_DARK, width=scale)

    elif mtype == "hazard":
        # Dark tar pit / ominous fissure emblem (light rim for dark Incognito background)
        r1 = 6.8 * scale
        r2 = 3.6 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=(28, 24, 22, 235), outline=INK_LIGHT, width=int(1.6 * scale))
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(12, 10, 10, 250))

    elif mtype == "crag":
        # Engraved rocky monolith / peak triangle
        r_glow = 10 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 150))
        s = 7.2 * scale
        tri = [(cx, cy - s), (cx + s * 0.9, cy + s * 0.72), (cx - s * 0.9, cy + s * 0.72)]
        d.polygon(tri, fill=PARCHMENT_FILL, outline=INK_DARK)
        d.line(tri + [tri[0]], fill=INK_DARK, width=int(1.7 * scale))
        tri_in = [(cx, cy - s * 0.45), (cx + s * 0.35, cy + s * 0.38), (cx - s * 0.35, cy + s * 0.38)]
        d.polygon(tri_in, fill=INK_DARK)

    elif mtype == "outpost":
        # Bleak frontier beacon on Ilha de Thanatos
        r1 = 5.6 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.5 * scale))
        r2 = 2.5 * scale
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=CRIMSON_ACCENT)

    elif mtype == "fort":
        # Refined small antique square fort/waystation marker
        r_glow = 8.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 145))
        s = 4.6 * scale
        d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.6 * scale))
        r_in = 1.9 * scale
        d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=INK_DARK)

    else:
        r_glow = 9 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 145))
        r1 = 5.8 * scale
        r2 = 2.7 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT_FILL, outline=INK_DARK, width=int(1.6 * scale))
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=INK_DARK)


def place_label(dt, dh, w, h, x, y, dx, dy, anchor_mode, text, font, ink, light_on_dark=False, underline_color=None):
    is_multiline = "\n" in text
    if is_multiline:
        bbox = dt.multiline_textbbox((0, 0), text, font=font, align="center", spacing=4)
    else:
        bbox = dt.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    if anchor_mode == "right":
        tx = x + dx
        ty = y + dy - th // 2
    elif anchor_mode == "left":
        tx = x + dx - tw
        ty = y + dy - th // 2
    elif anchor_mode == "above":
        tx = x + dx - tw // 2
        ty = y + dy - th
    elif anchor_mode == "below":
        tx = x + dx - tw // 2
        ty = y + dy
    else:  # center
        tx = x + dx - tw // 2
        ty = y + dy - th // 2

    tx = max(68, min(w - 68 - tw, tx))
    ty = max(68, min(h - 68 - th, ty))

    halo = HALO_DARK if light_on_dark else HALO_LIGHT
    stroke_fill = OUTLINE_DARK if light_on_dark else (232, 223, 200, 210)

    for ox in range(-4, 5, 2):
        for oy in range(-4, 5, 2):
            if is_multiline:
                dh.multiline_text((tx + ox, ty + oy), text, font=font, fill=halo, align="center", spacing=4)
            else:
                dh.text((tx + ox, ty + oy), text, font=font, fill=halo)

    if is_multiline:
        dt.multiline_text((tx, ty), text, font=font, fill=ink, align="center", spacing=4, stroke_width=2, stroke_fill=stroke_fill)
    else:
        dt.text((tx, ty), text, font=font, fill=ink, stroke_width=2, stroke_fill=stroke_fill)

    if underline_color is not None and not is_multiline:
        uy = ty + th + 6
        dt.line([(tx, uy), (tx + tw, uy)], fill=underline_color, width=2)


def render():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_path = os.path.join(BASE_DIR, data["base_image"])
    base = Image.open(base_path).convert("RGBA")
    w, h = base.size

    # 1. Custom engraved islands (Ilha das Safiras, Ilha de Thanatos, Arquipelago Ravena)
    island_layer = draw_custom_islands((w, h), data.get("custom_islands", []))

    # 2. Supersampled markers for cities & landmarks
    scale = 2
    marker_hi = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    for city in data.get("cities", []):
        draw_marker(marker_hi, city["x"], city["y"], city.get("type", "city"), scale=scale)
    for lm in data.get("landmarks", []):
        draw_marker(marker_hi, lm["x"], lm["y"], lm.get("type", "ruins"), scale=scale)
    marker_layer = marker_hi.resize((w, h), Image.Resampling.LANCZOS)

    # 3. Typography layers
    halo_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dh = ImageDraw.Draw(halo_layer)
    dt = ImageDraw.Draw(text_layer)

    font_capital = ImageFont.truetype(FONT_BOLD, 30)
    font_citadel = ImageFont.truetype(FONT_BOLD, 24)
    font_city = ImageFont.truetype(FONT_BOLD, 23)
    font_landmark = ImageFont.truetype(FONT_REG, 20)
    font_fort = ImageFont.truetype(FONT_BOLD, 19)
    font_region = ImageFont.truetype(FONT_BOLD_ITALIC, 21)
    font_geo_sub = ImageFont.truetype(FONT_ITALIC, 18)
    font_island = ImageFont.truetype(FONT_ITALIC, 21)
    font_sea = ImageFont.truetype(FONT_ITALIC, 26)

    # Draw regions / seas first (underneath primary city text if near)
    for reg in data.get("regions", []):
        style = reg.get("style", "region_italic")
        light_on_dark = reg.get("theme") == "light_on_dark" or style == "sea_italic"
        if style == "sea_italic":
            font = font_sea
            ink = INK_SEA
        elif style == "island_label":
            font = font_island
            ink = INK_LIGHT if light_on_dark else INK_REGION
        elif style == "geo_sub":
            font = font_geo_sub
            ink = INK_REGION
        else:
            font = font_region
            ink = INK_LIGHT if light_on_dark else INK_REGION

        place_label(
            dt, dh, w, h,
            reg["x"], reg["y"], 0, 0, "center",
            reg["name"], font, ink, light_on_dark=light_on_dark
        )

    # Draw landmarks & forts
    for lm in data.get("landmarks", []):
        light_on_dark = lm.get("theme") == "light_on_dark"
        ink = INK_LIGHT if light_on_dark else INK_DARK
        lfont = font_fort if lm.get("type") == "fort" else font_landmark
        place_label(
            dt, dh, w, h,
            lm["x"], lm["y"], lm.get("dx", 14), lm.get("dy", -4),
            lm.get("label_anchor", "right"),
            lm["name"], lfont, ink, light_on_dark=light_on_dark
        )

    # Draw cities
    for city in data.get("cities", []):
        mtype = city.get("type", "city")
        if mtype == "capital":
            font = font_capital
            display = city["name"].upper()
            ink = INK_CAPITAL
            underline = CRIMSON_ACCENT
        elif mtype == "citadel":
            font = font_citadel
            display = city["name"]
            ink = INK_DARK
            underline = None
        else:
            font = font_city
            display = city["name"]
            ink = INK_DARK
            underline = None

        place_label(
            dt, dh, w, h,
            city["x"], city["y"], city.get("dx", 14), city.get("dy", -4),
            city.get("label_anchor", "right"),
            display, font, ink, light_on_dark=False, underline_color=underline
        )

    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(radius=3.5))

    out = Image.alpha_composite(base, island_layer)
    out = Image.alpha_composite(out, halo_layer)
    out = Image.alpha_composite(out, marker_layer)
    out = Image.alpha_composite(out, text_layer)

    out_png = os.path.join(BASE_DIR, data["output_image"])
    out_jpg = os.path.join(BASE_DIR, data["output_jpg"])
    out.convert("RGB").save(out_png, optimize=True)
    out.convert("RGB").save(out_jpg, quality=94)

    total = len(data.get("cities", [])) + len(data.get("landmarks", [])) + len(data.get("regions", []))
    print(f"Rendered {total} labels & {len(data.get('custom_islands', []))} island groups -> {out_png} ({w}x{h})")


if __name__ == "__main__":
    render()
