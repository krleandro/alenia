#!/usr/bin/env python3
"""
Renderizador de Mapas Regionais Aproximados de Alenia (Estilo Atlas GRRM).
Recorta e amplia cada continente a partir da base cartográfica oficial,
adiciona estradas reais, trilhas de caravana, rotas marítimas, vilas, minas,
pontes, faróis, oásis, ruínas, moldura de atlas, cartela de título, escala e legenda.
"""
import json
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import render_atlas as ra

ATLAS_PATH = os.path.join(BASE_DIR, "alenia_atlas_data.json")
REG_PATH = os.path.join(BASE_DIR, "alenia_regionais_data.json")

FONT_BOLD = r"C:\Windows\Fonts\palab.ttf"
FONT_REG = r"C:\Windows\Fonts\pala.ttf"
FONT_ITALIC = r"C:\Windows\Fonts\palai.ttf"
FONT_BOLD_ITALIC = r"C:\Windows\Fonts\palabi.ttf"

INK_DARK = (26, 20, 14, 248)
INK_CAPITAL = (42, 22, 10, 250)
INK_REGION = (38, 28, 18, 236)
INK_LIGHT = (240, 232, 212, 248)
INK_SEA = (214, 226, 230, 225)
OUTLINE_DARK = (16, 20, 24, 220)
PARCHMENT = (232, 222, 198, 242)
PARCHMENT_BOX = (232, 223, 202, 226)
GOLD = (182, 140, 62, 245)
CRIMSON = (128, 34, 26, 240)
ROAD_ROYAL = (108, 62, 32, 225)
ROAD_ROYAL_HL = (224, 204, 166, 175)
ROAD_TRAIL = (92, 56, 30, 210)
ROAD_SEA = (215, 228, 232, 175)


def catmull_rom_chain(points, samples_per_seg=18):
    if len(points) < 2:
        return points
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(samples_per_seg):
            t = s / samples_per_seg
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def draw_dashed_polyline(draw, pts, dash_len, gap_len, color, width):
    if len(pts) < 2:
        return
    drawing = True
    rem = dash_len
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        seg_len = math.hypot(dx, dy)
        if seg_len < 1e-6:
            continue
        ux, uy = dx / seg_len, dy / seg_len
        pos = 0.0
        while pos < seg_len:
            step = min(rem, seg_len - pos)
            sx, sy = x1 + ux * pos, y1 + uy * pos
            ex, ey = x1 + ux * (pos + step), y1 + uy * (pos + step)
            if drawing:
                draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
            pos += step
            rem -= step
            if rem <= 1e-4:
                drawing = not drawing
                rem = dash_len if drawing else gap_len


def draw_extra_marker(layer, x, y, mtype, scale=2):
    d = ImageDraw.Draw(layer)
    cx, cy = x * scale, y * scale

    if mtype in ("capital", "citadel", "port", "special", "academy", "observatory", "ruins", "wreck", "hazard", "crag", "outpost", "fort", "city"):
        ra.draw_marker(layer, x, y, mtype, scale=scale)
        return

    if mtype == "village":
        r_glow = 7.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 145))
        r1 = 4.6 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=PARCHMENT, outline=INK_DARK, width=int(1.5 * scale))

    elif mtype == "mine":
        # Crossed pickaxe / dark adamant diamond
        r_glow = 9 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 155))
        s = 6.0 * scale
        d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=INK_DARK, width=int(2.0 * scale))
        d.line([(cx + s, cy - s), (cx - s, cy + s)], fill=INK_DARK, width=int(2.0 * scale))
        r2 = 2.6 * scale
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=GOLD, outline=INK_DARK, width=scale)

    elif mtype == "tower":
        # Tall narrow watchtower / lighthouse rectangle with beacon dot
        r_glow = 9 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 150))
        tw, th = 3.8 * scale, 6.2 * scale
        d.rectangle([cx - tw, cy - th, cx + tw, cy + th], fill=PARCHMENT, outline=INK_DARK, width=int(1.5 * scale))
        d.line([(cx - tw - 2 * scale, cy - th), (cx + tw + 2 * scale, cy - th)], fill=INK_DARK, width=int(1.6 * scale))
        r_b = 2.0 * scale
        d.ellipse([cx - r_b, cy - th - 2.6 * scale, cx + r_b, cy - th + 1.4 * scale], fill=GOLD, outline=INK_DARK, width=scale)

    elif mtype == "bridge":
        # Double parallel bridge bars
        r_glow = 8.5 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 150))
        w, h = 6.2 * scale, 3.2 * scale
        d.rectangle([cx - w, cy - h, cx + w, cy + h], fill=PARCHMENT, outline=INK_DARK, width=int(1.5 * scale))
        d.line([(cx - w - 2 * scale, cy - h - 2 * scale), (cx + w + 2 * scale, cy - h - 2 * scale)], fill=INK_DARK, width=int(1.3 * scale))
        d.line([(cx - w - 2 * scale, cy + h + 2 * scale), (cx + w + 2 * scale, cy + h + 2 * scale)], fill=INK_DARK, width=int(1.3 * scale))

    elif mtype == "oasis":
        # Turquoise water ring in desert
        r_glow = 9 * scale
        d.ellipse([cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow], fill=(234, 224, 200, 150))
        r1 = 5.8 * scale
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=(82, 156, 146, 240), outline=INK_DARK, width=int(1.5 * scale))
        r2 = 2.2 * scale
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(42, 118, 72, 235))


def draw_frame_and_cartouche(img, title, subtitle, scale_leagues, legend_pos, title_pos):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Double engraved antique border
    m1, m2 = 18, 28
    d.rectangle([0, 0, w - 1, m1], fill=(214, 204, 182, 248))
    d.rectangle([0, h - m1, w - 1, h - 1], fill=(214, 204, 182, 248))
    d.rectangle([0, 0, m1, h - 1], fill=(214, 204, 182, 248))
    d.rectangle([w - m1, 0, w - 1, h - 1], fill=(214, 204, 182, 248))

    d.rectangle([m1, m1, w - m1 - 1, h - m1 - 1], outline=INK_DARK, width=4)
    d.rectangle([m2, m2, w - m2 - 1, h - m2 - 1], outline=INK_DARK, width=2)

    # Corner ticks
    for cx, cy in [(m1, m1), (w - m1, m1), (m1, h - m1), (w - m1, h - m1)]:
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD, outline=INK_DARK, width=2)

    # Title cartouche
    f_title = ImageFont.truetype(FONT_BOLD, 34)
    f_sub = ImageFont.truetype(FONT_ITALIC, 19)
    f_leg = ImageFont.truetype(FONT_REG, 17)
    f_leg_b = ImageFont.truetype(FONT_BOLD, 18)

    tb = d.textbbox((0, 0), title, font=f_title)
    sb = d.textbbox((0, 0), subtitle, font=f_sub)
    box_w = max(tb[2] - tb[0], sb[2] - sb[0]) + 64
    box_h = 104

    if title_pos == "bottom_right":
        bx, by = w - m2 - box_w - 22, h - m2 - box_h - 22
    elif title_pos == "bottom_left":
        bx, by = m2 + 22, h - m2 - box_h - 22
    else:
        bx, by = w - m2 - box_w - 22, m2 + 22

    d.rectangle([bx, by, bx + box_w, by + box_h], fill=PARCHMENT_BOX, outline=INK_DARK, width=3)
    d.rectangle([bx + 6, by + 6, bx + box_w - 6, by + box_h - 6], outline=GOLD, width=2)
    tw = tb[2] - tb[0]
    sw = sb[2] - sb[0]
    d.text((bx + (box_w - tw) // 2, by + 16), title, font=f_title, fill=INK_CAPITAL)
    d.line([(bx + 28, by + 58), (bx + box_w - 28, by + 58)], fill=CRIMSON, width=2)
    d.text((bx + (box_w - sw) // 2, by + 66), subtitle, font=f_sub, fill=INK_REGION)

    # Compact antique Legend + Scale bar
    lw, lh = 282, 218
    if legend_pos == "top_left":
        lx, ly = m2 + 20, m2 + 20
    elif legend_pos == "top_right":
        lx, ly = w - m2 - lw - 20, m2 + 20
    else:
        lx, ly = m2 + 20, h - m2 - lh - 20

    d.rectangle([lx, ly, lx + lw, ly + lh], fill=PARCHMENT_BOX, outline=INK_DARK, width=2)
    d.rectangle([lx + 5, ly + 5, lx + lw - 5, ly + lh - 5], outline=GOLD, width=1)
    d.text((lx + 16, ly + 10), "LEGENDA", font=f_leg_b, fill=INK_CAPITAL)
    d.line([(lx + 14, ly + 36), (lx + lw - 14, ly + 36)], fill=INK_DARK, width=1)

    # Legend items
    y0 = ly + 46
    # Estrada Real
    d.line([(lx + 18, y0 + 9), (lx + 56, y0 + 9)], fill=ROAD_ROYAL, width=4)
    d.line([(lx + 18, y0 + 9), (lx + 56, y0 + 9)], fill=ROAD_ROYAL_HL, width=1)
    d.text((lx + 66, y0), "Estrada Real", font=f_leg, fill=INK_DARK)

    # Trilha / Caravana
    y0 += 26
    draw_dashed_polyline(d, [(lx + 18, y0 + 9), (lx + 56, y0 + 9)], 7, 5, ROAD_TRAIL, 3)
    d.text((lx + 66, y0), "Trilha / Caravana", font=f_leg, fill=INK_DARK)

    # Rota Maritima
    y0 += 26
    draw_dashed_polyline(d, [(lx + 18, y0 + 9), (lx + 56, y0 + 9)], 4, 6, (52, 82, 96, 220), 3)
    d.text((lx + 66, y0), "Rota Marítima", font=f_leg, fill=INK_DARK)

    # Cidade / Forte / Vila / Ruina summary
    y0 += 28
    d.ellipse([lx + 24, y0 + 3, lx + 36, y0 + 15], fill=PARCHMENT, outline=INK_DARK, width=2)
    d.ellipse([lx + 28, y0 + 7, lx + 32, y0 + 11], fill=INK_DARK)
    d.text((lx + 44, y0), "Cidade", font=f_leg, fill=INK_DARK)

    d.ellipse([lx + 132, y0 + 4, lx + 142, y0 + 14], fill=PARCHMENT, outline=INK_DARK, width=2)
    d.text((lx + 150, y0), "Vila / Oásis", font=f_leg, fill=INK_DARK)

    y0 += 26
    d.rectangle([lx + 25, y0 + 4, lx + 35, y0 + 14], fill=PARCHMENT, outline=INK_DARK, width=2)
    d.text((lx + 44, y0), "Forte", font=f_leg, fill=INK_DARK)

    for ox, oy in [(137, 4), (132, 12), (142, 12)]:
        d.rectangle([lx + ox - 2, y0 + oy - 2, lx + ox + 2, y0 + oy + 2], fill=INK_DARK)
    d.text((lx + 150, y0), "Ruínas", font=f_leg, fill=INK_DARK)

    # Divider + Scale bar cleanly spaced at bottom of legend
    d.line([(lx + 14, ly + lh - 38), (lx + lw - 14, ly + lh - 38)], fill=(140, 124, 96, 160), width=1)
    sy = ly + lh - 20
    d.line([(lx + 18, sy), (lx + 134, sy)], fill=INK_DARK, width=3)
    for sx in (lx + 18, lx + 76, lx + 134):
        d.line([(sx, sy - 6), (sx, sy + 6)], fill=INK_DARK, width=2)
    d.text((lx + 144, sy - 10), scale_leagues, font=f_leg, fill=INK_CAPITAL)

    return Image.alpha_composite(img, overlay)


def render_all_regionals():
    with open(ATLAS_PATH, "r", encoding="utf-8") as f:
        atlas = json.load(f)
    with open(REG_PATH, "r", encoding="utf-8") as f:
        reg_cfg = json.load(f)

    out_dir = os.path.join(BASE_DIR, reg_cfg["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    # Load full base + custom islands layer so regional maps include Ilha das Safiras, Thanatos & Ravena!
    base_full = Image.open(os.path.join(BASE_DIR, atlas["base_image"])).convert("RGBA")
    islands_full = ra.draw_custom_islands(base_full.size, atlas.get("custom_islands", []))
    master_terrain = Image.alpha_composite(base_full, islands_full)

    # Collect all world-map places + regions to project into each regional crop
    world_cities = atlas.get("cities", [])
    world_landmarks = atlas.get("landmarks", [])
    world_regions = atlas.get("regions", [])

    font_capital = ImageFont.truetype(FONT_BOLD, 34)
    font_citadel = ImageFont.truetype(FONT_BOLD, 28)
    font_city = ImageFont.truetype(FONT_BOLD, 27)
    font_fort = ImageFont.truetype(FONT_BOLD, 23)
    font_landmark = ImageFont.truetype(FONT_REG, 22)
    font_extra = ImageFont.truetype(FONT_REG, 21)
    font_region = ImageFont.truetype(FONT_BOLD_ITALIC, 25)
    font_geo_sub = ImageFont.truetype(FONT_ITALIC, 22)
    font_island = ImageFont.truetype(FONT_ITALIC, 24)
    font_sea = ImageFont.truetype(FONT_ITALIC, 30)

    for rmap in reg_cfg["regions_maps"]:
        rid = rmap["id"]
        x0, y0, x1, y1 = rmap["crop"]
        cw, ch = x1 - x0, y1 - y0

        # Upscale crop smoothly to crisp target width ~2200px preserving aspect ratio
        target_w = 2200
        zoom = target_w / cw
        target_h = int(round(ch * zoom))

        cropped = master_terrain.crop((x0, y0, x1, y1))
        up = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        up = up.filter(ImageFilter.UnsharpMask(radius=1.1, percent=65, threshold=2))

        def proj(gx, gy):
            return (gx - x0) * zoom, (gy - y0) * zoom

        # 1. Roads, Trails & Sea Routes Layer
        road_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(road_layer)
        for rd in rmap.get("roads", []):
            pts = [proj(px, py) for px, py in rd["points"]]
            smooth = catmull_rom_chain(pts, samples_per_seg=22)
            st = rd.get("style", "trail")
            if st == "royal":
                # Subtle dark casing + warm antique road fill
                dr.line(smooth, fill=(44, 28, 16, 175), width=8, joint="curve")
                dr.line(smooth, fill=ROAD_ROYAL, width=5, joint="curve")
                dr.line(smooth, fill=ROAD_ROYAL_HL, width=2, joint="curve")
            elif st == "trail":
                draw_dashed_polyline(dr, smooth, 13, 9, (236, 226, 204, 145), 5)
                draw_dashed_polyline(dr, smooth, 13, 9, ROAD_TRAIL, 3)
            elif st == "sea":
                draw_dashed_polyline(dr, smooth, 8, 11, (22, 32, 38, 145), 5)
                draw_dashed_polyline(dr, smooth, 8, 11, ROAD_SEA, 3)

        # 2. Markers Layer (2x supersampled)
        scale = 2
        marker_hi = Image.new("RGBA", (target_w * scale, target_h * scale), (0, 0, 0, 0))
        halo_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        text_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        dh = ImageDraw.Draw(halo_layer)
        dt = ImageDraw.Draw(text_layer)

        pad = 24
        def in_crop(gx, gy):
            return (x0 + 18) <= gx <= (x1 - 18) and (y0 + 18) <= gy <= (y1 - 18)

        # World regions inside this crop
        for reg in world_regions:
            if not in_crop(reg["x"], reg["y"]):
                continue
            px, py = proj(reg["x"], reg["y"])
            st = reg.get("style", "region_italic")
            light = reg.get("theme") == "light_on_dark" or st == "sea_italic"
            if st == "sea_italic":
                fnt, ink = font_sea, INK_SEA
            elif st == "island_label":
                fnt, ink = font_island, (INK_LIGHT if light else INK_REGION)
            elif st == "geo_sub":
                fnt, ink = font_geo_sub, INK_REGION
            else:
                fnt, ink = font_region, (INK_LIGHT if light else INK_REGION)
            ra.place_label(dt, dh, target_w, target_h, px, py, 0, 0, "center", reg["name"], fnt, ink, light_on_dark=light)

        # Extra local villages, mines, towers, bridges, oases, ruins
        for ex in rmap.get("extra_places", []):
            px, py = proj(ex["x"], ex["y"])
            draw_extra_marker(marker_hi, px, py, ex.get("type", "village"), scale=scale)
            light = ex.get("theme") == "light_on_dark"
            ink = INK_LIGHT if light else INK_DARK
            ra.place_label(
                dt, dh, target_w, target_h,
                px, py, ex.get("dx", 12) * 1.15, ex.get("dy", -2) * 1.15,
                ex.get("label_anchor", "right"), ex["name"], font_extra, ink, light_on_dark=light
            )

        # World landmarks & forts inside this crop
        for lm in world_landmarks:
            if not in_crop(lm["x"], lm["y"]):
                continue
            px, py = proj(lm["x"], lm["y"])
            draw_extra_marker(marker_hi, px, py, lm.get("type", "ruins"), scale=scale)
            light = lm.get("theme") == "light_on_dark"
            ink = INK_LIGHT if light else INK_DARK
            fnt = font_fort if lm.get("type") == "fort" else font_landmark
            ra.place_label(
                dt, dh, target_w, target_h,
                px, py, lm.get("dx", 14) * 1.15, lm.get("dy", -4) * 1.15,
                lm.get("label_anchor", "right"), lm["name"], fnt, ink, light_on_dark=light
            )

        # World cities inside this crop
        for city in world_cities:
            if not in_crop(city["x"], city["y"]):
                continue
            px, py = proj(city["x"], city["y"])
            mtype = city.get("type", "city")
            draw_extra_marker(marker_hi, px, py, mtype, scale=scale)
            if mtype == "capital":
                fnt, disp, ink, uline = font_capital, city["name"].upper(), INK_CAPITAL, CRIMSON
            elif mtype == "citadel":
                fnt, disp, ink, uline = font_citadel, city["name"], INK_DARK, None
            else:
                fnt, disp, ink, uline = font_city, city["name"], INK_DARK, None
            ra.place_label(
                dt, dh, target_w, target_h,
                px, py, city.get("dx", 15) * 1.18, city.get("dy", -3) * 1.18,
                city.get("label_anchor", "right"), disp, fnt, ink, light_on_dark=False, underline_color=uline
            )

        marker_layer = marker_hi.resize((target_w, target_h), Image.Resampling.LANCZOS)
        halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(radius=3.5))

        out = Image.alpha_composite(up, road_layer)
        out = Image.alpha_composite(out, halo_layer)
        out = Image.alpha_composite(out, marker_layer)
        out = Image.alpha_composite(out, text_layer)
        out = draw_frame_and_cartouche(
            out, rmap["title"], rmap["subtitle"],
            rmap["scale_leagues"], rmap["legend_pos"], rmap["title_pos"]
        )

        out_png = os.path.join(out_dir, f"mapa_regional_{rid}.png")
        out_jpg = os.path.join(out_dir, f"mapa_regional_{rid}.jpg")
        out.convert("RGB").save(out_png, optimize=True)
        out.convert("RGB").save(out_jpg, quality=93)
        print(f"[OK] {rid}: {target_w}x{target_h} -> {out_png}")


if __name__ == "__main__":
    render_all_regionals()
