#!/usr/bin/env python3
"""Reproducible high-DPI PNG + vector SVG generator for all 16 Task D Final Handoff figures.

Reads strictly from verified CSV/JSON tables in ./tables/ (exported from immutable
audited G2 v2 design-3.1 JSON artifacts). Produces zero synthetic experimental data.

Usage:
    python3 docs/research/final-handoff/task-d/tables/generate_figures.py
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

TABLES_DIR = Path(__file__).resolve().parent
FIGURES_DIR = TABLES_DIR.parent / "figures"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# Academic colorblind-friendly palette
C_BG = "#FFFFFF"
C_PANEL = "#F8FAFC"
C_BORDER = "#CBD5E1"
C_GRID = "#E2E8F0"
C_INK = "#0F172A"
C_MUTED = "#475569"
C_NAVY = "#1B4965"
C_STEEL = "#457B9D"
C_TEAL = "#2A9D8F"
C_GREEN = "#15803D"
C_AMBER = "#D97706"
C_CORAL = "#DC2626"
C_PURPLE = "#6D28D9"
C_SLATE = "#64748B"
C_LIGHT_BLUE = "#E0F2FE"
C_LIGHT_TEAL = "#CCFBF1"
C_LIGHT_AMBER = "#FEF3C7"
C_LIGHT_RED = "#FEE2E2"
C_LIGHT_GREEN = "#DCFCE7"
C_LIGHT_PURPLE = "#EDE9FE"
C_LIGHT_SLATE = "#F1F5F9"


def load_csv(name: str) -> list[dict[str, str]]:
    with (TABLES_DIR / name).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_json(name: str) -> dict:
    return json.loads((TABLES_DIR / name).read_text(encoding="utf-8"))


class DualCanvas:
    """Simultaneous 2x-supersampled 300-DPI PNG + crisp vector SVG renderer."""

    def __init__(self, width: int = 1600, height: int = 980, scale: int = 2) -> None:
        self.w = width
        self.h = height
        self.s = scale
        self.img = Image.new("RGB", (width * scale, height * scale), C_BG)
        self.draw = ImageDraw.Draw(self.img)
        self.svg_lines: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{C_BG}"/>',
        ]
        self._font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def _font(self, size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
        path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REG)
        key = (path, size * self.s)
        if key not in self._font_cache:
            self._font_cache[key] = ImageFont.truetype(path, size * self.s)
        return self._font_cache[key]

    def text_width(self, txt: str, size: int = 14, bold: bool = False, mono: bool = False) -> float:
        bbox = self.draw.textbbox((0, 0), txt, font=self._font(size, bold, mono))
        return (bbox[2] - bbox[0]) / self.s

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str | None = None,
        stroke: str | None = None,
        stroke_w: float = 1.5,
        radius: float = 0.0,
    ) -> None:
        s = self.s
        box = [round(x * s), round(y * s), round((x + w) * s), round((y + h) * s)]
        if radius > 0:
            self.draw.rounded_rectangle(
                box,
                radius=round(radius * s),
                fill=fill,
                outline=stroke,
                width=max(1, round(stroke_w * s)) if stroke else 0,
            )
        else:
            self.draw.rectangle(
                box,
                fill=fill,
                outline=stroke,
                width=max(1, round(stroke_w * s)) if stroke else 0,
            )
        attrs = [
            f'x="{x:.1f}"',
            f'y="{y:.1f}"',
            f'width="{w:.1f}"',
            f'height="{h:.1f}"',
            f'fill="{fill if fill else "none"}"',
        ]
        if stroke:
            attrs.append(f'stroke="{stroke}" stroke-width="{stroke_w:.1f}"')
        if radius > 0:
            attrs.append(f'rx="{radius:.1f}" ry="{radius:.1f}"')
        self.svg_lines.append("  <rect " + " ".join(attrs) + "/>")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = C_BORDER,
        width: float = 1.5,
        dashed: bool = False,
    ) -> None:
        s = self.s
        if not dashed:
            self.draw.line(
                [(x1 * s, y1 * s), (x2 * s, y2 * s)],
                fill=color,
                width=max(1, round(width * s)),
            )
        else:
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist > 0:
                dash, gap = 8.0, 5.0
                pos = 0.0
                dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
                while pos < dist:
                    end = min(pos + dash, dist)
                    self.draw.line(
                        [
                            ((x1 + dx * pos) * s, (y1 + dy * pos) * s),
                            ((x1 + dx * end) * s, (y1 + dy * end) * s),
                        ],
                        fill=color,
                        width=max(1, round(width * s)),
                    )
                    pos += dash + gap
        dash_attr = ' stroke-dasharray="8,5"' if dashed else ""
        self.svg_lines.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width:.1f}"{dash_attr}/>'
        )

    def arrow(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = C_NAVY,
        width: float = 2.0,
        head: float = 10.0,
        dashed: bool = False,
    ) -> None:
        ang = math.atan2(y2 - y1, x2 - x1)
        bx = x2 - head * math.cos(ang)
        by = y2 - head * math.sin(ang)
        self.line(x1, y1, bx, by, color=color, width=width, dashed=dashed)
        left = (
            x2 - head * math.cos(ang - 0.45),
            y2 - head * math.sin(ang - 0.45),
        )
        right = (
            x2 - head * math.cos(ang + 0.45),
            y2 - head * math.sin(ang + 0.45),
        )
        s = self.s
        self.draw.polygon(
            [(x2 * s, y2 * s), (left[0] * s, left[1] * s), (right[0] * s, right[1] * s)],
            fill=color,
        )
        pts = f"{x2:.1f},{y2:.1f} {left[0]:.1f},{left[1]:.1f} {right[0]:.1f},{right[1]:.1f}"
        self.svg_lines.append(f'  <polygon points="{pts}" fill="{color}"/>')

    def circle(
        self,
        cx: float,
        cy: float,
        r: float,
        fill: str = C_NAVY,
        stroke: str | None = None,
        stroke_w: float = 1.5,
    ) -> None:
        s = self.s
        self.draw.ellipse(
            [(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s],
            fill=fill,
            outline=stroke,
            width=max(1, round(stroke_w * s)) if stroke else 0,
        )
        st = f' stroke="{stroke}" stroke-width="{stroke_w:.1f}"' if stroke else ""
        self.svg_lines.append(
            f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{st}/>'
        )

    def text(
        self,
        x: float,
        y: float,
        txt: str,
        size: int = 14,
        color: str = C_INK,
        bold: bool = False,
        mono: bool = False,
        anchor: str = "start",
    ) -> None:
        s = self.s
        font = self._font(size, bold, mono)
        tw = self.text_width(txt, size, bold, mono)
        if anchor == "middle":
            px = x - tw / 2.0
        elif anchor == "end":
            px = x - tw
        else:
            px = x
        self.draw.text((px * s, y * s), txt, font=font, fill=color)
        fam = "DejaVu Sans Mono, monospace" if mono else "DejaVu Sans, Noto Sans, sans-serif"
        weight = ' font-weight="bold"' if bold else ""
        # SVG baseline roughly y + 0.82 * size for DejaVuSans top alignment match
        sy = y + size * 0.88
        self.svg_lines.append(
            f'  <text x="{x:.1f}" y="{sy:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}"{weight}>{html.escape(txt)}</text>'
        )

    def wrap_text(
        self,
        x: float,
        y: float,
        txt: str,
        max_w: float,
        size: int = 13,
        color: str = C_INK,
        bold: bool = False,
        line_h: float | None = None,
        anchor: str = "start",
        max_lines: int = 10,
    ) -> float:
        words = txt.split()
        lines: list[str] = []
        cur = ""
        for w in words:
            cand = f"{cur} {w}".strip()
            if self.text_width(cand, size, bold) <= max_w or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        lh = line_h if line_h is not None else size * 1.35
        for i, ln in enumerate(lines[:max_lines]):
            self.text(x, y + i * lh, ln, size=size, color=color, bold=bold, anchor=anchor)
        return y + min(len(lines), max_lines) * lh

    def badge(
        self,
        x: float,
        y: float,
        txt: str,
        bg: str,
        fg: str,
        size: int = 12,
        pad_x: float = 9.0,
        pad_y: float = 4.0,
        anchor: str = "start",
    ) -> float:
        tw = self.text_width(txt, size, bold=True)
        bw = tw + 2 * pad_x
        bh = size + 2 * pad_y + 2
        rx = x if anchor == "start" else (x - bw / 2.0 if anchor == "middle" else x - bw)
        self.rect(rx, y, bw, bh, fill=bg, stroke=fg, stroke_w=1.2, radius=6)
        self.text(rx + bw / 2.0, y + pad_y, txt, size=size, color=fg, bold=True, anchor="middle")
        return bw

    def header(self, title: str, subtitle: str) -> None:
        self.rect(0, 0, self.w, 86, fill=C_NAVY)
        self.rect(0, 86, self.w, 4, fill=C_TEAL)
        self.text(36, 16, title, size=23, color="#FFFFFF", bold=True)
        self.text(36, 52, subtitle, size=14, color="#E0F2FE")

    def footer(self, source: str, limitation: str) -> None:
        fy = self.h - 54
        self.line(36, fy, self.w - 36, fy, color=C_BORDER, width=1.0)
        self.text(36, fy + 8, f"Nguồn / Evidence: {source}", size=11, color=C_MUTED, bold=True)
        self.text(36, fy + 26, f"Phạm vi & Giới hạn: {limitation}", size=11, color=C_MUTED)

    def save(self, stem: str) -> None:
        self.svg_lines.append("</svg>")
        svg_path = FIGURES_DIR / f"{stem}.svg"
        png_path = FIGURES_DIR / f"{stem}.png"
        svg_path.write_text("\n".join(self.svg_lines) + "\n", encoding="utf-8")
        out_img = self.img.resize((self.w, self.h), Image.Resampling.LANCZOS)
        out_img.save(png_path, format="PNG", dpi=(300, 300), optimize=True)


def status_style(st: str) -> tuple[str, str]:
    st_u = st.upper()
    if any(k in st_u for k in ("GO / PASS", "COMPLETE_WITH_SCOPE")):
        return (C_LIGHT_TEAL, C_TEAL)
    if st_u in ("COMPLETE", "PASS", "GO"):
        return (C_LIGHT_GREEN, C_GREEN)
    if "SURVEY" in st_u:
        return (C_LIGHT_BLUE, C_NAVY)
    if "PIVOT" in st_u:
        return (C_LIGHT_PURPLE, C_PURPLE)
    if "HOLD" in st_u or "ADVISOR" in st_u:
        return (C_LIGHT_AMBER, C_AMBER)
    if "NO-GO" in st_u or "NO_GO" in st_u or "REFUTED" in st_u:
        return (C_LIGHT_RED, C_CORAL)
    return (C_LIGHT_SLATE, C_SLATE)


# ---------------------------------------------------------------------------
# Figure 01: Research Timeline (4 Eras, 12 Milestones)
# ---------------------------------------------------------------------------
def build_fig01() -> None:
    rows = load_csv("table01_research_timeline.csv")
    c = DualCanvas(1700, 1020)
    c.header(
        "Hình 1 · Tiến trình Nghiên cứu Task D qua 4 Kỷ nguyên (2026-10-01 → 2026-11-25)",
        "Mốc chính từ PipeANN đến G2. Các giai đoạn khảo sát và thực nghiệm có thời gian chồng lấn.",
    )
    era_colors = {
        "Kỷ nguyên 1: Nền tảng & PipeANN": (C_LIGHT_BLUE, C_NAVY),
        "Kỷ nguyên 2: Khảo sát 3 Cụm & E0–E3": (C_LIGHT_PURPLE, C_PURPLE),
        "Kỷ nguyên 3: R86 A×D (P0–P4, H1–H3)": (C_LIGHT_AMBER, C_AMBER),
        "Kỷ nguyên 4: G1/G2 R90 design-3.1": (C_LIGHT_TEAL, C_TEAL),
    }
    eras = list(era_colors.keys())
    col_w = 392
    gap = 20
    start_x = 36
    top_y = 115

    for ei, era in enumerate(eras):
        ex = start_x + ei * (col_w + gap)
        bg, fg = era_colors[era]
        c.rect(ex, top_y, col_w, 825, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
        c.rect(ex, top_y, col_w, 50, fill=fg, radius=10)
        c.rect(ex, top_y + 38, col_w, 12, fill=fg)
        c.text(ex + col_w / 2, top_y + 15, era, size=14, color="#FFFFFF", bold=True, anchor="middle")
        if ei < len(eras) - 1:
            c.arrow(ex + col_w + 2, top_y + 25, ex + col_w + gap - 2, top_y + 25, color=C_NAVY, width=2.5, head=9)

        erows = [r for r in rows if r["era"] == era]
        card_h = 170 if len(erows) == 4 else 225
        for ri, r in enumerate(erows):
            cy = top_y + 66 + ri * (card_h + 20)
            s_bg, s_fg = status_style(r["status"])
            c.rect(ex + 16, cy, col_w - 32, card_h, fill="#FFFFFF", stroke=s_fg, stroke_w=2.0, radius=8)
            c.text(ex + 28, cy + 14, f"#{r['idx']}  •  {r['date']}", size=12, color=C_MUTED, bold=True)
            c.badge(ex + col_w - 26, cy + 10, r["status"], bg=s_bg, fg=s_fg, size=11, anchor="end")
            c.wrap_text(ex + 28, cy + 44, r["milestone"], max_w=col_w - 56, size=15, color=C_INK, bold=True)
            c.line(ex + 28, cy + 94, ex + col_w - 28, cy + 94, color=C_GRID, width=1.0)
            c.wrap_text(ex + 28, cy + 106, r["detail"], max_w=col_w - 56, size=13, color=C_MUTED, line_h=20)
            if ri < len(erows) - 1:
                c.arrow(ex + col_w / 2, cy + card_h + 2, ex + col_w / 2, cy + card_h + 18, color=C_SLATE, width=2.0, head=7)

    c.footer(
        "TASK_D_RESEARCH_TIMELINE.md (a0916db) • tables/table01_research_timeline.csv",
        "Hai lượt HOLD G2 OFF (design-3 #1, design-3.1 run1 #120) được cô lập tuyệt đối khỏi run2; G3 vẫn NOT_OPENED.",
    )
    c.save("fig01_research_timeline")


# ---------------------------------------------------------------------------
# Figure 02: 3-Cluster Parallel ANN Taxonomy & D01-D10
# ---------------------------------------------------------------------------
def build_fig02() -> None:
    rows = load_csv("table02_taxonomy_d01_d10.csv")
    c = DualCanvas(1680, 980)
    c.header(
        "Hình 2 · Hệ phân loại 3 Cụm Song song hóa ANN (D01–D10) & Trạng thái Thực nghiệm Task D",
        "Tách bạch theo tài nguyên phần cứng (CPU / CPU–SSD / GPU) và trục trực giao Inter-query (D10)",
    )
    clusters = [
        ("Cụm 1: CPU Multi-core", "Trọng tâm thực nghiệm Task D (E0–E3, P2, B1+A1)", C_NAVY, C_LIGHT_BLUE, ["D01", "D02", "D03"]),
        ("Cụm 2: CPU–SSD Pipeline", "Baseline PipeANN (#32) + Survey LAANN/DiskANN", C_TEAL, C_LIGHT_TEAL, ["D04", "D05", "D06", "D07", "D08"]),
        ("Cụm 3: GPU Data Parallelism", "SURVEY_COMPLETE (0 benchmark native GPU)", C_PURPLE, C_LIGHT_PURPLE, ["D09"]),
    ]
    by_code = {r["code"]: r for r in rows}

    # Top root node
    c.rect(520, 108, 640, 56, fill=C_INK, radius=10)
    c.text(840, 121, "TASK D — PARALLEL EXECUTION & SCHEDULING FOR ANN", size=16, color="#FFFFFF", bold=True, anchor="middle")
    c.text(840, 143, "Tách biệt Algorithmic Dependency vs Implementation Bottleneck (Work–Span–Cost)", size=12, color="#CBD5E1", anchor="middle")

    col_xs = [36, 584, 1132]
    col_w = 512
    box_y = 200
    box_h = 540

    for idx, (cname, csub, fg, bg, codes) in enumerate(clusters):
        cx = col_xs[idx]
        c.arrow(840, 164, cx + col_w / 2, box_y - 2, color=fg, width=2.2, head=9)
        c.rect(cx, box_y, col_w, box_h, fill=C_PANEL, stroke=fg, stroke_w=2.0, radius=10)
        c.rect(cx, box_y, col_w, 58, fill=fg, radius=10)
        c.rect(cx, box_y + 46, col_w, 12, fill=fg)
        c.text(cx + col_w / 2, box_y + 10, cname, size=16, color="#FFFFFF", bold=True, anchor="middle")
        c.text(cx + col_w / 2, box_y + 34, csub, size=12, color="#F8FAFC", anchor="middle")

        item_h = 84 if len(codes) == 5 else (130 if len(codes) == 3 else 220)
        gap = 12 if len(codes) == 5 else 18
        for j, code in enumerate(codes):
            r = by_code[code]
            iy = box_y + 72 + j * (item_h + gap)
            c.rect(cx + 14, iy, col_w - 28, item_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.4, radius=7)
            c.badge(cx + 24, iy + 10, code, bg=bg, fg=fg, size=12)
            c.text(cx + 84, iy + 13, r["mechanism"], size=13, color=C_INK, bold=True)
            c.text(cx + 24, iy + 40, f"Đại diện: {r['representative']}  |  Pha: {r['phase']}", size=11, color=C_MUTED)
            c.wrap_text(cx + 24, iy + 58, f"Trạng thái: {r['status']}", max_w=col_w - 48, size=11, color=fg, bold=True)
            if code == "D09":
                c.line(cx + 24, iy + 96, cx + col_w - 24, iy + 96, color=C_GRID, width=1.0)
                c.wrap_text(
                    cx + 24,
                    iy + 110,
                    "Nội dung đã khảo sát: WarpSelect (register queues, warp ballot/shuffle), Exact GEMM + fused selection, IVFADC PQ LUT shared-memory, two-pass top-k, Multi-GPU sharding/replication, CAGRA & FusionANNS. Phép đo A×D được thiết kế cho CPU.",
                    max_w=col_w - 48,
                    size=12,
                    color=C_MUTED,
                    line_h=19,
                )
        if idx == 1:
            c.text(cx + col_w / 2, box_y + box_h - 18, "* Lưu ý: D05, D06, D07 là 3 cơ chế phối hợp trong cùng hệ thống PipeANN (OSDI '25).", size=11, color=C_MUTED, anchor="middle")

    # Orthogonal D10 bar at bottom
    d10 = by_code["D10"]
    c.rect(36, 764, 1608, 132, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=2.0, radius=10)
    c.badge(56, 780, "D10 · TRỤC XUYÊN SUỐT (ORTHOGONAL)", bg="#FFFFFF", fg=C_AMBER, size=13)
    c.text(390, 784, "Inter-query Concurrency & Global Resource Control (CPU / SSD / GPU Serving)", size=15, color=C_INK, bold=True)
    c.wrap_text(
        56,
        820,
        f"Bản chất: D10 không loại trừ D03/D05/D09 — nhiều truy vấn có thể chạy đồng thời trên cùng hệ thống đa lõi, SSD hay GPU. Bằng chứng Task D: Issue #32 PipeANN SIFT10M ghi nhận T16 giảm -13.36% QPS và tăng P99.9 lên 83.55 ms so với T8; chiến dịch G2 v2 cố định jobs=1 nên concurrent multi-query serving (D10) còn OPEN.",
        max_w=1568,
        size=13,
        color=C_INK,
        line_h=20,
    )

    c.footer(
        "HỆ THỐNG TASK D.pdf • Task D Google Sheets (02_TAXONOMY) • tables/table02_taxonomy_d01_d10.csv",
        "Cụm 2 (LAANN/scheduler mới) và Cụm 3 (GPU) dừng ở SURVEY_COMPLETE; chỉ Cụm 1 (B1+A1) và PipeANN baseline (#32) có benchmark native.",
    )
    c.save("fig02_parallel_ann_taxonomy")


# ---------------------------------------------------------------------------
# Figure 03: Prior Art Comparison Table/Visual
# ---------------------------------------------------------------------------
def build_fig03() -> None:
    rows = load_csv("table03_prior_art_comparison.csv")
    c = DualCanvas(1720, 960)
    c.header(
        "Hình 3 · Ma trận So sánh Prior Art trong 3 Cụm Parallel ANN & Định vị Task D B1+A1",
        "Đối chiếu đúng pha (BUILD vs SEARCH), cơ chế đồng bộ, đánh đổi và ranh giới bằng chứng (PAPER vs D-OBS)",
    )
    cols = [
        ("Công trình", "system", 175),
        ("Cụm", "cluster", 105),
        ("Pha", "phase", 130),
        ("Cơ chế song song", "parallelism", 240),
        ("Đồng bộ", "sync_mech", 190),
        ("Đánh đổi / Giới hạn chính", "key_tradeoff", 390),
        ("Nhãn bằng chứng & Phạm vi", "scope_note", 418),
    ]
    x0, y0 = 36, 114
    hdr_h = 46
    row_h = 70
    tot_w = sum(w for _, _, w in cols)

    # Header
    c.rect(x0, y0, tot_w, hdr_h, fill=C_NAVY, radius=6)
    cx = x0
    for title, _, w in cols:
        c.text(cx + 10, y0 + 14, title, size=13, color="#FFFFFF", bold=True)
        cx += w

    for i, r in enumerate(rows):
        ry = y0 + hdr_h + i * row_h
        is_self = r["system"].startswith("Task D")
        bg = C_LIGHT_TEAL if is_self else ("#FFFFFF" if i % 2 == 0 else C_PANEL)
        stroke = C_TEAL if is_self else C_GRID
        c.rect(x0, ry, tot_w, row_h, fill=bg, stroke=stroke, stroke_w=2.0 if is_self else 1.0)
        cx = x0
        for _, key, w in cols:
            is_first = key == "system"
            col_color = C_NAVY if (is_first or is_self) else C_INK
            if key == "scope_note" and "PAPER" in r[key]:
                col_color = C_MUTED
            if key == "scope_note" and "D-OBS" in r[key]:
                col_color = C_GREEN
            c.wrap_text(
                cx + 10,
                ry + 12,
                r[key],
                max_w=w - 18,
                size=12,
                color=col_color,
                bold=(is_first or is_self),
                line_h=17,
                max_lines=3,
            )
            if cx > x0:
                c.line(cx, ry, cx, ry + row_h, color=C_GRID, width=0.8)
            cx += w

    c.footer(
        "Task D Sheets (01_PAPERS) • H3_NOVELTY_AND_PRIOR_ART_AUDIT.md • tables/table03_prior_art_comparison.csv",
        "PAPER chỉ mô tả cơ chế công bố; OBS ở dòng PipeANN là phép đo Issue #32, D-OBS ở dòng B1+A1 là G2 R90.",
    )
    c.save("fig03_prior_art_comparison")


# ---------------------------------------------------------------------------
# Figure 04: Research Gap -> Hypothesis -> Experiment -> Decision
# ---------------------------------------------------------------------------
def build_fig04() -> None:
    rows = load_csv("table04_workflow_decisions.csv")
    c = DualCanvas(1680, 960)
    c.header(
        "Hình 4 · Chu trình Nghiên cứu: Research Gap → Giả thuyết → Thực nghiệm → Quyết định",
        "Chứng minh cách các kết quả âm có kiểm soát trực tiếp sàng lọc và dẫn tới tối ưu đường cơ sở B1+A1 trên G2 v2",
    )
    col_defs = [
        ("Giai đoạn", 220, C_NAVY, C_LIGHT_BLUE),
        ("1. Research Gap", 315, C_STEEL, "#FFFFFF"),
        ("2. Giả thuyết (Falsifiable)", 340, C_PURPLE, "#FFFFFF"),
        ("3. Thực nghiệm / Đối chứng", 355, C_AMBER, "#FFFFFF"),
        ("4. Quyết định (Gate Verdict)", 340, C_TEAL, "#FFFFFF"),
    ]
    y_hdr = 112
    x_pos = [36]
    for _, w, _, _ in col_defs[:-1]:
        x_pos.append(x_pos[-1] + w + 10)

    for idx, (label, w, fg, _) in enumerate(col_defs):
        c.rect(x_pos[idx], y_hdr, w, 44, fill=fg, radius=7)
        c.text(x_pos[idx] + w / 2, y_hdr + 13, label, size=14, color="#FFFFFF", bold=True, anchor="middle")
        if idx in (1, 2, 3):
            c.arrow(x_pos[idx] + w + 1, y_hdr + 22, x_pos[idx + 1] - 1, y_hdr + 22, color=C_INK, width=2.0, head=7)

    row_h = 128
    gap_y = 18
    keys = ["stage", "gap", "hypothesis", "experiment", "decision"]
    for i, r in enumerate(rows):
        ry = y_hdr + 62 + i * (row_h + gap_y)
        is_last = i == len(rows) - 1
        for ci, k in enumerate(keys):
            w = col_defs[ci][1]
            if ci == 0:
                fill = C_TEAL if is_last else C_NAVY
                c.rect(x_pos[ci], ry, w, row_h, fill=fill, radius=8)
                c.wrap_text(x_pos[ci] + 14, ry + 36, r[k], max_w=w - 28, size=14, color="#FFFFFF", bold=True, line_h=21)
            elif ci == 4:
                bg, fg = (C_LIGHT_GREEN, C_GREEN) if is_last else (C_LIGHT_RED if "NO-GO" in r[k] else C_LIGHT_PURPLE, C_CORAL if "NO-GO" in r[k] else C_PURPLE)
                c.rect(x_pos[ci], ry, w, row_h, fill=bg, stroke=fg, stroke_w=2.0, radius=8)
                c.wrap_text(x_pos[ci] + 14, ry + 24, r[k], max_w=w - 28, size=13, color=C_INK, bold=True, line_h=20)
            else:
                c.rect(x_pos[ci], ry, w, row_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.4, radius=8)
                c.wrap_text(x_pos[ci] + 14, ry + 26, r[k], max_w=w - 28, size=13, color=C_INK, line_h=20)
            if ci < 4:
                c.arrow(x_pos[ci] + w + 1, ry + row_h / 2, x_pos[ci + 1] - 1, ry + row_h / 2, color=C_SLATE, width=2.0, head=7)
        if i < len(rows) - 1:
            c.arrow(x_pos[0] + 110, ry + row_h + 1, x_pos[0] + 110, ry + row_h + gap_y - 1, color=C_NAVY, width=2.5, head=7)

    c.footer(
        "TASK_D_FINAL_RESEARCH_SYNTHESIS.md • ORIGINAL_PROPOSAL_FINAL_REASSESSMENT.md • tables/table04_workflow_decisions.csv",
        "E0 là mô hình, E2 dừng nhiệt, TP-CG chuyển hướng trước P5, overlap dừng sau screening. B1+A1 được đánh giá bằng cặp ON/OFF trên R90.",
    )
    c.save("fig04_research_workflow_decisions")


# ---------------------------------------------------------------------------
# Figure 05: Baseline BSP Multi-Walker Architecture (P2SearchSession)
# ---------------------------------------------------------------------------
def build_fig05() -> None:
    c = DualCanvas(1680, 960)
    c.header(
        "Hình 5 · Kiến trúc Baseline Multi-Walker BSP (P2SearchSession, p=2, S=16, beam=432)",
        "Trích trực tiếp từ mã nguồn đóng băng research/task_da/search_common/p2_engine.hpp (commit f2cd634)",
    )
    # Stage 0: Entry expansion
    c.rect(48, 114, 1584, 96, fill=C_LIGHT_BLUE, stroke=C_NAVY, stroke_w=2.0, radius=10)
    c.badge(68, 128, "KHỞI TẠO TUẦN TỰ (Worker 0)", bg=C_NAVY, fg="#FFFFFF", size=12)
    c.text(310, 132, "next_query_epoch() [uint16_t; xóa mảng khi quay vòng] → Mở rộng đỉnh entry → Khởi tạo global_best_vec_ (sorted vector, cap = B = 432)", size=14, color=C_INK, bold=True)
    c.text(68, 168, "Mảng toàn cục dùng chung (chỉ đọc trong pha song song): Graph CSR (offsets/edges) • Vectors float32 • settled_epoch_[n] • global_expanded_epoch_[n]", size=13, color=C_MUTED)

    c.arrow(840, 210, 840, 248, color=C_NAVY, width=2.5, head=9)

    # Outer superstep box
    c.rect(48, 250, 1584, 620, fill=C_PANEL, stroke=C_STEEL, stroke_w=2.0, radius=12)
    c.badge(72, 264, "VÒNG LẶP SUPERSTEP BSP (~14.87 vòng/truy vấn trên R90 b432)", bg=C_STEEL, fg="#FFFFFF", size=13)

    # Dispatch bar
    c.rect(72, 306, 1536, 78, fill="#FFFFFF", stroke=C_NAVY, stroke_w=1.8, radius=8)
    c.text(92, 318, "1. PHÂN PHÁT HẠT GIỐNG & PHÁT TÍN HIỆU (Worker 0 → work_seq_.store(next_seq, release))", size=14, color=C_NAVY, bold=True)
    c.text(92, 346, "Baseline full frontier: quét toàn bộ global_best_vec_ (≤432), gom mọi đỉnh chưa expand vào active_frontier_, chia round-robin i % p cho init_seeds của từng worker.", size=13, color=C_INK)

    # Two parallel worker lanes
    c.arrow(440, 384, 440, 418, color=C_TEAL, width=2.5, head=9)
    c.arrow(1240, 384, 1240, 418, color=C_TEAL, width=2.5, head=9)

    for wi, wx, cpu in [(0, 72, "CPU 0 (CCX 0)"), (1, 872, "CPU 2 (CCX 0)")]:
        c.rect(wx, 420, 736, 224, fill="#FFFFFF", stroke=C_TEAL, stroke_w=2.0, radius=10)
        c.rect(wx, 420, 736, 40, fill=C_TEAL, radius=10)
        c.rect(wx, 448, 736, 12, fill=C_TEAL)
        c.text(wx + 20, 431, f"2. WORKER {wi} · alignas(64) WorkerState · Ghim {cpu}", size=14, color="#FFFFFF", bold=True)
        steps_txt = [
            "• Nạp init_seeds vào std::set<Hit> local_pending (Baseline: tối đa B/2 = 216 đỉnh)",
            "• Lặp tối đa S = 16 bước (steps < sync_interval_ && !local_pending.empty()):",
            "   1) Pop đỉnh tốt nhất u → ghi vào local_expanded",
            "   2) Duyệt láng giềng v: bỏ qua nếu settled_epoch_[v]==q_epoch || local_seen.contains_or_insert(v)",
            "   3) Tính squared_l2(v, q) bằng double (float64); loại sớm nếu hit >= global_worst",
            "   4) Nếu lọt local_top (cỡ B): chèn local_top, local_pending và local_discovered",
            "• Ghi done_seq.store(next_seq, release) (Worker 1) / tiếp tục barrier (Worker 0)",
        ]
        for si, line in enumerate(steps_txt):
            c.text(wx + 18, 472 + si * 23, line, size=12, color=C_INK if si < 2 else C_MUTED, bold=(si < 2))

    # Barrier & single-writer merge
    c.arrow(440, 644, 440, 682, color=C_AMBER, width=2.5, head=9)
    c.arrow(1240, 644, 1240, 682, color=C_AMBER, width=2.5, head=9)

    c.rect(72, 684, 1536, 166, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=2.0, radius=10)
    c.text(92, 698, "3. HÀNG RÀO SPIN-WAIT & PHA HỢP NHẤT ĐƠN LUỒNG (Single-Writer Merge trên Worker 0 — Không cần Mutex)", size=14, color=C_AMBER, bold=True)
    c.wrap_text(
        92,
        728,
        "• Worker 0 spin-wait (cpu_relax ≤2048 lần, rồi yield) chờ Worker 1 đặt done_seq == next_seq.\n"
        "• Cập nhật mảng toàn cục: đánh dấu global_expanded_epoch_[u] = q_epoch; ở baseline đánh dấu settled_epoch_[v] cho local_expanded và local_discovered (NÚT CỔ CHAI B1: đỉnh bị loại bởi global_worst sẽ bị tính lại L2 ở các vòng sau!).\n"
        "• Sắp xếp & loại trùng merge_scratch_, trộn tuyến tính O(B + M_r) với global_best_vec_ giữ top-B.\n"
        "• Dựng lại toàn bộ active_frontier_ (NÚT CỔ CHAI A1: duyệt hết B phần tử & nạp lại tới 216 seed/worker vào std::set).",
        max_w=1496,
        size=13,
        color=C_INK,
        line_h=24,
    )
    # Loopback arrow
    c.line(1608, 760, 1622, 760, color=C_NAVY, width=2.2)
    c.line(1622, 760, 1622, 345, color=C_NAVY, width=2.2)
    c.arrow(1622, 345, 1608, 345, color=C_NAVY, width=2.2, head=8)

    c.footer(
        "research/task_da/search_common/p2_engine.hpp (commit f2cd634) • TASK_D_B1_A1_TECHNICAL_EXPLANATION.md",
        "Đúng đắn kiến trúc chứng minh từ mã nguồn; hình mô tả cấu hình G2 v2 (p=2, CPU [0,2] cùng CCX0, S=16, beam=432).",
    )
    c.save("fig05_baseline_multiwalker_arch")


# ---------------------------------------------------------------------------
# Figure 06: B1 (barrier_all_evaled) Before / After
# ---------------------------------------------------------------------------
def build_fig06() -> None:
    c = DualCanvas(1680, 940)
    c.header(
        "Hình 6 · Cơ chế B1 (VisitedPolicy::kBarrierAllEvaled) — So sánh Trước & Sau",
        "Worker ghi lại các ID đã tính L2. Tại barrier, worker 0 công bố các ID để vòng sau tránh tính lại.",
    )
    # Left panel: BEFORE
    c.rect(36, 114, 780, 740, fill=C_PANEL, stroke=C_CORAL, stroke_w=2.0, radius=10)
    c.rect(36, 114, 780, 52, fill=C_CORAL, radius=10)
    c.rect(36, 154, 780, 12, fill=C_CORAL)
    c.text(426, 129, "TRƯỚC B1 · Baseline (kBaseline)", size=16, color="#FFFFFF", bold=True, anchor="middle")

    steps_before = [
        ("Vòng r · Worker tính L2(v, q)", "Đỉnh v nằm ngoài ngưỡng global_worst (hit ≥ global_worst, so cặp khoảng cách và ID)\n→ bị loại sớm (continue), KHÔNG vào local_discovered.", C_LIGHT_SLATE, C_SLATE),
        ("Hàng rào cuối vòng r", "Worker 0 CHỈ đánh dấu settled_epoch_[x] = q_epoch\ncho x ∈ local_discovered ∪ local_expanded.\n⇒ settled_epoch_[v] VẪN KHÁC q_epoch!", C_LIGHT_RED, C_CORAL),
        ("Vòng r+1, r+2, ...", "Láng giềng khác lại trỏ tới cùng đỉnh v.\nKiểm tra settled_epoch_[v] != q_epoch → KHÔNG CHẶN ĐƯỢC!\n→ Tính lại squared_l2(v, q) nhiều lần vô ích!", C_LIGHT_RED, C_CORAL),
        ("Baseline trên sáu graph R90 (counters test ON)", "Duplicate L2 = 3,712.81 / query (16.30% tổng L2)\nTotal L2 = 22,776.97 / query • Already-seen = 3,293.25 / q", "#FFFFFF", C_CORAL),
    ]
    for i, (t, desc, bg, fg) in enumerate(steps_before):
        sy = 186 + i * 164
        c.rect(64, sy, 724, 134, fill=bg, stroke=fg, stroke_w=1.8, radius=8)
        c.text(84, sy + 14, t, size=14, color=fg if fg != C_SLATE else C_INK, bold=True)
        for li, line in enumerate(desc.split("\n")):
            c.text(84, sy + 44 + li * 25, line, size=13, color=C_INK)
        if i < 3:
            c.arrow(426, sy + 134, 426, sy + 162, color=C_CORAL, width=2.4, head=8)

    # Right panel: AFTER
    c.rect(864, 114, 780, 740, fill=C_PANEL, stroke=C_TEAL, stroke_w=2.0, radius=10)
    c.rect(864, 114, 780, 52, fill=C_TEAL, radius=10)
    c.rect(864, 154, 780, 12, fill=C_TEAL)
    c.text(1254, 129, "SAU B1 · Barrier All-Evaluated (kBarrierAllEvaled)", size=16, color="#FFFFFF", bold=True, anchor="middle")

    steps_after = [
        ("Vòng r · Worker tính L2(v, q)", "Ngay sau squared_l2(v, q), ghi nhận v vào buffer riêng:\nws.local_newly_evaled.push_back(v) — kể cả đỉnh bị loại!\n(Không dùng atomic, không chia sẻ ghi trong pha song song.)", C_LIGHT_BLUE, C_NAVY),
        ("Hàng rào cuối vòng r (Single-Writer)", "Trước khi vào vòng r+1, Worker 0 duyệt local_newly_evaled\nvà đánh dấu settled_epoch_[v] = q_epoch cho 100% đỉnh đã tính L2.", C_LIGHT_TEAL, C_TEAL),
        ("Vòng r+1, r+2, ... · Tính bất biến toán học", "v bị chặn ngay ở O(1) (settled_epoch_[v] == q_epoch).\nVì global_worst giảm đơn điệu, đỉnh từng bị loại KHÔNG BAO GIỜ\ncó thể lọt lại global_best ⇒ Quỹ đạo & Top-10 BIT-EXACT 100%.", C_LIGHT_GREEN, C_GREEN),
        ("Đo baseline so với B1+A1 (counters test ON, sáu graph R90)", "Duplicate L2: 3,712.81 → 928.77 / q (-74.98%, chỉ còn trùng nội vòng)\nTotal L2: 22,776.97 → 19,992.93 / q (-12.22%) • Unique L2: Δ = 0", "#FFFFFF", C_GREEN),
    ]
    for i, (t, desc, bg, fg) in enumerate(steps_after):
        sy = 186 + i * 164
        c.rect(892, sy, 724, 134, fill=bg, stroke=fg, stroke_w=1.8, radius=8)
        c.text(912, sy + 14, t, size=14, color=fg, bold=True)
        for li, line in enumerate(desc.split("\n")):
            c.text(912, sy + 44 + li * 25, line, size=13, color=C_INK)
        if i < 3:
            c.arrow(1254, sy + 134, 1254, sy + 162, color=C_TEAL, width=2.4, head=8)

    c.arrow(818, 480, 862, 480, color=C_NAVY, width=3.0, head=11)

    c.footer(
        "p2_engine.hpp (L453–455, L844–848) • TASK_D_B1_A1_TECHNICAL_EXPLANATION.md • audit_results.json (c79e45a3...)",
        "Còn lại 928.77 dup L2/q (~4.65% tổng L2) là trùng nội vòng giữa 2 worker trong cùng superstep — không thể triệt tiêu bởi barrier mà không thêm atomic.",
    )
    c.save("fig06_b1_before_after")


# ---------------------------------------------------------------------------
# Figure 07: A1 (incremental frontier) Before / After
# ---------------------------------------------------------------------------
def build_fig07() -> None:
    c = DualCanvas(1680, 940)
    c.header(
        "Hình 7 · Cơ chế A1 (FrontierMode::kIncremental) — So sánh Trước & Sau",
        "Mỗi worker nhận tối đa S hạt giống theo thứ tự ưu tiên trong bộ máy BSP cố định.",
    )
    # Left panel: BEFORE
    c.rect(36, 114, 780, 740, fill=C_PANEL, stroke=C_CORAL, stroke_w=2.0, radius=10)
    c.rect(36, 114, 780, 52, fill=C_CORAL, radius=10)
    c.rect(36, 154, 780, 12, fill=C_CORAL)
    c.text(426, 129, "TRƯỚC A1 · Full Frontier Rebuild (kFull)", size=16, color="#FFFFFF", bold=True, anchor="middle")

    # Visual array diagram before
    c.rect(64, 186, 724, 182, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.5, radius=8)
    c.text(84, 200, "global_best_vec_ (kích thước B = 432, chỉ lưu Hit):", size=13, color=C_NAVY, bold=True)
    # Draw cells representing 432 elements
    for k in range(18):
        bx = 84 + k * 37
        fill = C_LIGHT_SLATE if k < 6 else C_LIGHT_RED
        c.rect(bx, 232, 33, 36, fill=fill, stroke=C_SLATE if k < 6 else C_CORAL, stroke_w=1.2, radius=4)
        c.text(bx + 16.5, 243, "E" if k < 6 else "U", size=11, color=C_MUTED if k < 6 else C_CORAL, bold=True, anchor="middle")
    c.text(84, 278, "E = đã expand (phải tra ngẫu nhiên global_expanded_epoch_[id] cỡ 2 MiB)", size=12, color=C_MUTED)
    c.text(84, 300, "U = chưa expand → sao chép TOÀN BỘ sang active_frontier_ (có thể tới 432 đỉnh!)", size=12, color=C_CORAL, bold=True)
    c.text(84, 324, "Không phân biệt trường hợp merge_scratch_ rỗng hay khác rỗng — luôn quét hết B.", size=12, color=C_MUTED)

    c.arrow(426, 368, 426, 398, color=C_CORAL, width=2.4, head=8)
    c.rect(64, 400, 724, 210, fill=C_LIGHT_RED, stroke=C_CORAL, stroke_w=1.8, radius=8)
    c.text(84, 414, "Phân phát thừa & chi phí cấp phát nút cây đỏ-đen (std::set):", size=14, color=C_CORAL, bold=True)
    c.wrap_text(
        84,
        444,
        "• Mỗi worker nhận tới B / p = 216 hạt giống vào init_seeds.\n"
        "• Đầu mỗi superstep, mỗi worker chèn cả ≤216 đỉnh vào std::set<Hit> local_pending (cấp phát heap từng node, độ phức tạp O((B/p) log(B/p))).\n"
        "• NHƯNG vòng lặp while(steps < S) CHỈ pop tối đa S = 16 đỉnh tốt nhất!\n"
        "• Khoảng ~200 đỉnh xếp hạng sau hoàn toàn KHÔNG BAO GIỜ được pop trong vòng đó nhưng vẫn tốn chi phí chèn/hủy cây đỏ-đen mỗi vòng.",
        max_w=684,
        size=13,
        color=C_INK,
        line_h=24,
    )

    c.arrow(426, 610, 426, 640, color=C_CORAL, width=2.4, head=8)
    c.rect(64, 642, 724, 186, fill="#FFFFFF", stroke=C_CORAL, stroke_w=1.8, radius=8)
    c.text(84, 658, "Độ phức tạp mỗi superstep (Baseline):", size=14, color=C_INK, bold=True)
    c.text(84, 690, "• Quét lại toàn bộ B + tra ngẫu nhiên global_expanded_epoch_[id]: O(B)", size=13, color=C_INK)
    c.text(84, 718, "• Dựng std::set local_pending trên mỗi worker: O((B/p) · log(B/p))", size=13, color=C_CORAL, bold=True)
    c.text(84, 746, "• Với B=432, p=2, S=16: nạp tới 216 seed/worker (~13.5× mức tối đa S=16!)", size=13, color=C_MUTED)
    c.text(84, 774, "• Trên R86 A3 (B≈970): nạp tới ~485 seed/worker (~30× mức S=16!)", size=13, color=C_MUTED)

    # Right panel: AFTER
    c.rect(864, 114, 780, 740, fill=C_PANEL, stroke=C_TEAL, stroke_w=2.0, radius=10)
    c.rect(864, 114, 780, 52, fill=C_TEAL, radius=10)
    c.rect(864, 154, 780, 12, fill=C_TEAL)
    c.text(1254, 129, "SAU A1 · Incremental Frontier (kIncremental)", size=16, color="#FFFFFF", bold=True, anchor="middle")

    c.rect(892, 186, 724, 182, fill="#FFFFFF", stroke=C_TEAL, stroke_w=1.5, radius=8)
    c.text(912, 200, "global_best_flat_ lưu FlatEntry { Hit hit; uint8_t expanded; }:", size=13, color=C_NAVY, bold=True)
    for k in range(18):
        bx = 912 + k * 37
        if k < 6:
            fill, st, lbl = C_LIGHT_SLATE, C_SLATE, "1"
        elif k < 10:
            fill, st, lbl = C_LIGHT_GREEN, C_GREEN, "0*"
        else:
            fill, st, lbl = "#FFFFFF", C_BORDER, "0"
        c.rect(bx, 232, 33, 36, fill=fill, stroke=st, stroke_w=1.5 if lbl == "0*" else 1.1, radius=4)
        c.text(bx + 16.5, 243, lbl, size=11, color=st if lbl != "0" else C_MUTED, bold=True, anchor="middle")
    c.text(912, 278, "Con trỏ first_unexp (bỏ qua tiền tố đã expand) & prev_last_disp (chỉ tra epoch ≤ prev_last_disp)", size=12, color=C_NAVY, bold=True)
    c.text(912, 300, "0* = Tối đa max_dispatch = p × S = 32 hạt giống tốt nhất được đẩy trực tiếp vào init_seeds", size=12, color=C_GREEN, bold=True)
    c.text(912, 324, "Nhánh nhanh khi merge_scratch_.empty(): bắt đầu từ first_unexp, dừng sớm ngay khi đủ p×S.", size=12, color=C_MUTED)

    c.arrow(1254, 368, 1254, 398, color=C_TEAL, width=2.4, head=8)
    c.rect(892, 400, 724, 210, fill=C_LIGHT_TEAL, stroke=C_TEAL, stroke_w=1.8, radius=8)
    c.text(912, 414, "Chứng minh bất biến chính xác (Bit-Exact Equivalence):", size=14, color=C_NAVY, bold=True)
    c.wrap_text(
        912,
        444,
        "• Tập hạt giống ban đầu của worker w được cấp theo thứ tự tăng dần khoảng cách.\n"
        "• Mỗi bước chỉ pop phần tử nhỏ nhất trong local_pending và chạy tối đa S = 16 bước.\n"
        "• Mọi phần tử đứng ở hạng ≥ S (từ thứ 17 trở đi) trong init_seeds KHÔNG THỂ NÀO đứng trước cả S phần tử tốt hơn đã nạp sẵn (mọi láng giềng mới chèn thêm chỉ làm vị trí của chúng lùi sâu hơn).\n"
        "⇒ Giới hạn init_seeds ở tối đa S = 16 đỉnh/worker bảo toàn 100% quỹ đạo và Top-10!",
        max_w=684,
        size=13,
        color=C_INK,
        line_h=24,
    )

    c.arrow(1254, 610, 1254, 640, color=C_TEAL, width=2.4, head=8)
    c.rect(892, 642, 724, 186, fill="#FFFFFF", stroke=C_GREEN, stroke_w=1.8, radius=8)
    c.text(912, 658, "Độ phức tạp mỗi superstep (Sau A1) & Hiệu ứng đo:", size=14, color=C_GREEN, bold=True)
    c.text(912, 690, "• Dựng std::set local_pending: O(S · log S) thay vì O((B/p) · log(B/p))", size=13, color=C_GREEN, bold=True)
    c.text(912, 718, "• Không còn mảng trung gian active_frontier_; giảm số lần tra mảng epoch; PMU chưa đo", size=13, color=C_INK)
    c.text(912, 746, "• B1+A1 cùng hoạt động: giảm -6.033% mean latency OFF (p=2, S=16, b432)", size=13, color=C_NAVY, bold=True)
    c.text(912, 774, "• ON merge_time tăng 35.89 µs/q; dispatch nay nằm trong cửa sổ đo merge.", size=12, color=C_AMBER, bold=True)

    c.arrow(818, 480, 862, 480, color=C_NAVY, width=3.0, head=11)

    c.footer(
        "p2_engine.hpp (L691–709, L900–976) • TASK_D_B1_A1_TECHNICAL_EXPLANATION.md",
        "Độ phức tạp phân tích dưới giả định B > p·S và tìm kiếm BSP; G2 v2 đo hiệu ứng tổng hợp B1+A1 (không tách riêng B1/A1 trên R90).",
    )
    c.save("fig07_a1_before_after")


# ---------------------------------------------------------------------------
# Figure 08: G2 v2 design-3.1 Experimental Design 2x2 & Safety Gates
# ---------------------------------------------------------------------------
def build_fig08() -> None:
    c = DualCanvas(1680, 960)
    c.header(
        "Hình 8 · Thiết kế Thực nghiệm 2×2 & Quy trình Kiểm soát Cổng G2 v2 (design-3.1)",
        "Protocol AXD-G2-V2-3A-20261123 • MS-Turing-1M (v2_test_10000) • 6 đồ thị R90 P0A v1.3 • Ryzen 5 PRO 4650U",
    )
    # Left: 2x2 factorial design matrix
    c.rect(36, 114, 830, 500, fill=C_PANEL, stroke=C_NAVY, stroke_w=2.0, radius=10)
    c.text(56, 130, "MA TRẬN NHÂN TỐ 2 × 2 (TASK A BUILD × TASK D SEARCH)", size=15, color=C_NAVY, bold=True)
    c.text(56, 154, "6 đồ thị cố định R90 v1.3 (C160/K1024/N2, SEED=555) × 2 chính sách Search × 12 block cân bằng", size=12, color=C_MUTED)

    # Headers for 2x2
    c.rect(250, 190, 290, 48, fill=C_STEEL, radius=6)
    c.text(395, 205, "Task D: Baseline (flat+full)", size=13, color="#FFFFFF", bold=True, anchor="middle")
    c.rect(556, 190, 290, 48, fill=C_TEAL, radius=6)
    c.text(701, 205, "Task D: B1+A1 (bar_all+inc)", size=13, color="#FFFFFF", bold=True, anchor="middle")

    c.rect(56, 250, 180, 160, fill=C_NAVY, radius=6)
    c.text(146, 294, "Task A: Stock", size=14, color="#FFFFFF", bold=True, anchor="middle")
    c.text(146, 318, "3 graphs (r1–r3)", size=12, color="#E0F2FE", anchor="middle")
    c.text(146, 342, "BUILD: 42.257 s", size=12, color="#FEF3C7", bold=True, anchor="middle")
    c.text(146, 362, "(Host A, 4T)", size=11, color="#CBD5E1", anchor="middle")

    c.rect(56, 426, 180, 160, fill=C_NAVY, radius=6)
    c.text(146, 470, "Task A: Fast v2", size=14, color="#FFFFFF", bold=True, anchor="middle")
    c.text(146, 494, "3 graphs (r1–r3)", size=12, color="#E0F2FE", anchor="middle")
    c.text(146, 518, "BUILD: 33.793 s", size=12, color="#CCFBF1", bold=True, anchor="middle")
    c.text(146, 538, "(-20.03%, Host A)", size=11, color="#CBD5E1", anchor="middle")

    cells_info = [
        (250, 250, "Ô 1: stock_base", "36 tiến trình OFF • 3 ON test", "Mean: 3619.87 µs | QPS: 276.24", "R@10: 0.992050 | Mốc tham chiếu", "#FFFFFF", C_BORDER),
        (556, 250, "Ô 2: stock_opt", "36 tiến trình OFF • 3 ON test", "Mean: 3401.51 µs (-6.032%)", "Bit-exact R@10 | QPS: 293.97", C_LIGHT_BLUE, C_STEEL),
        (250, 426, "Ô 3: fast_base", "36 tiến trình OFF • 3 ON test", "Mean: 3619.54 µs (−0.33 µs vs Stock)", "Gate B PASS | QPS: 276.26", C_LIGHT_SLATE, C_SLATE),
        (556, 426, "Ô 4: fast_opt (Tổ hợp A×D)", "36 tiến trình OFF • 3 ON test", "Mean: 3401.14 µs (-6.034%)", "Tương tác: +0.037 µs (CI qua 0)", C_LIGHT_TEAL, C_TEAL),
    ]
    for cx, cy, t, l1, l2, l3, bg, st in cells_info:
        c.rect(cx, cy, 290, 160, fill=bg, stroke=st, stroke_w=2.0, radius=8)
        c.text(cx + 16, cy + 16, t, size=14, color=C_NAVY, bold=True)
        c.text(cx + 16, cy + 48, l1, size=12, color=C_MUTED)
        c.text(cx + 16, cy + 78, l2, size=13, color=C_INK, bold=True)
        c.text(cx + 16, cy + 110, l3, size=12, color=C_GREEN if "opt" in t else C_MUTED, bold=("opt" in t))

    # Bottom left: Balance & Guard controls
    c.rect(36, 634, 830, 246, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.8, radius=10)
    c.text(56, 650, "KIỂM SOÁT CÂN BẰNG, NHIỄU & CÔ LẬP HOLD (design-3.1)", size=14, color=C_NAVY, bold=True)
    controls = [
        "• Cân bằng 12 block × 6 graph × 2 policy = 144 tiến trình OFF (72 cặp liền kề: 36 AB + 36 BA).",
        "• Mỗi đồ thị xuất hiện đúng 2 lần tại mỗi vị trí block 0..5 để cân bằng thứ tự chạy theo thời gian.",
        "• Giới hạn nhiễu CPU theo topology CCX: Workers [0..3] ≤ 0.010 | CCX0 [0..5] ≤ 0.020 | Host [0..11] ≤ 0.025.",
        "• Thực tế run2: max Workers = 0.0055, CCX0 = 0.0075, Host = 0.0070; Tctl max = 78.5°C (< 95°C); AC = 1.",
        "• Môi trường sạch: systemd multi-user.target + prepare_quiet_tty_env.sh; khôi phục đầy đủ sau chạy.",
        "• Cô lập tuyệt đối 2 lượt HOLD lịch sử (design-3 #1 KeyError; run1 #120 firmware-notifier): 0/144 receipt trùng.",
    ]
    for ci, txt in enumerate(controls):
        c.text(56, 682 + ci * 30, txt, size=12, color=C_INK)

    # Right: Gate pipeline
    c.rect(892, 114, 752, 766, fill=C_PANEL, stroke=C_TEAL, stroke_w=2.0, radius=10)
    c.text(914, 130, "QUY TRÌNH CỔNG PHÊ DUYỆT & KIỂM TOÁN ĐỘC LẬP", size=15, color=C_TEAL, bold=True)
    gates = [
        ("Cổng 0 · Freeze & Qualification (900s)", "Manifest design-3.1 (29/29 SHA) • Qual #2 PASS: 853/853 (10s) & 848/848 (15s), 0 hard failures.", "QUALIFICATION_PASS", C_LIGHT_GREEN, C_GREEN),
        ("Cổng 1 · Quality ON (18/18, beam=432)", "20,000 truy vấn duy nhất (10k test + 10k val) • Gate A (min LCB95 = 0.991188 > 0.990) & Gate B (±0.0005) PASS • 120,000 cặp ON (60k test + 60k val so với Stage 5); 0 sai lệch.", "QUALITY_GATE_PASS", C_LIGHT_GREEN, C_GREEN),
        ("Cổng 2 · Owner Approval (OFF_AB)", "Ký phê duyệt design3_1_off_approval_run2.json (SHA edbe6e98..., quota 10,800s, scope OFF_AB).", "APPROVAL_PASS", C_LIGHT_BLUE, C_NAVY),
        ("Cổng 3 · Performance OFF (144/144)", "Thời gian 7,987.18 s • 1,440,000 bản ghi OFF không có trường counters • 144/144 bit-exact digest parity • 1,299/1,299 BUNDLE.sha256 • NO_HOLD_JSON.", "GO_A + GO_B", C_LIGHT_TEAL, C_TEAL),
        ("Cổng 4 · Independent Final Audit & Archive", "Replay độc lập 100% số liệu & 20k bootstrap: max_stat_diff = 0.0, 0 discrepancies • PRIVATE Release 9/9 SHA-256 verified.", "AUDIT_PASS", C_LIGHT_GREEN, C_GREEN),
    ]
    for gi, (gt, gd, gstat, gbg, gfg) in enumerate(gates):
        gy = 174 + gi * 138
        c.rect(914, gy, 708, 114, fill="#FFFFFF", stroke=gfg, stroke_w=1.8, radius=8)
        c.text(932, gy + 12, gt, size=14, color=C_INK, bold=True)
        c.badge(1604, gy + 10, gstat, bg=gbg, fg=gfg, size=11, anchor="end")
        c.wrap_text(932, gy + 44, gd, max_w=672, size=12, color=C_MUTED, line_h=19)
        if gi < len(gates) - 1:
            c.arrow(1268, gy + 114, 1268, gy + 136, color=C_NAVY, width=2.4, head=8)

    c.footer(
        "AXD_G2_V2_DESIGN3_1_FINAL_AUDIT.md • AXD_G2_V2_DESIGN3_1_FREEZE_MANIFEST.json (bc897419...)",
        "Phạm vi EXPLORATORY_HOST_SPECIFIC • graph_population_ci = NOT_ESTIMABLE • Chưa đo p=1/4, jobs>1 hay single-host end-to-end.",
    )
    c.save("fig08_g2_experimental_design_2x2")


# ---------------------------------------------------------------------------
# Figure 09: Mean Latency OFF & 4 CI Families Forest Plot
# ---------------------------------------------------------------------------
def build_fig09() -> None:
    arms = load_csv("table05_g2_2x2_arms_summary.csv")
    cis = load_csv("table06_ci_families.csv")
    c = DualCanvas(1680, 940)
    c.header(
        "Hình 9 · Độ trễ Mean OFF (Host D) và So sánh 4 Họ Khoảng Tin Cậy (95% CI)",
        "G2 v2 design-3.1 run2 (144/144 OFF) • MS-Turing-1M (v2_test_10000) • p=2, S=16, beam=432, jobs=1 • Ryzen 5 PRO 4650U",
    )

    # Panel A (Left): Mean Latency Bars (Base vs B1+A1 across Stock, Fast, Pooled)
    px, py, pw, ph = 52, 126, 700, 710
    c.rect(px, py, pw, ph, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(px + 20, py + 16, "A. Độ trễ trung bình OFF theo nhánh (µs/truy vấn)", size=16, color=C_NAVY, bold=True)
    c.text(px + 20, py + 40, "Thấp hơn là tốt hơn • Fast trừ Stock: −0.33 µs ở baseline, −0.37 µs ở B1+A1", size=12, color=C_MUTED)

    # Legend
    c.rect(px + 420, py + 68, 16, 16, fill=C_STEEL, radius=3)
    c.text(px + 444, py + 68, "Baseline", size=12, color=C_INK, bold=True)
    c.rect(px + 540, py + 68, 16, 16, fill=C_TEAL, radius=3)
    c.text(px + 564, py + 68, "B1+A1 (Opt)", size=12, color=C_INK, bold=True)

    # Plot axes (y from 3000 to 3800 µs — clearly labeled truncated axis with break mark!)
    ax_x, ax_y, ax_w, ax_h = px + 88, py + 110, 580, 500
    y_min, y_max = 3000.0, 3800.0
    c.rect(ax_x, ax_y, ax_w, ax_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.2)
    for tick in range(3000, 3801, 100):
        ty = ax_y + ax_h - (tick - y_min) / (y_max - y_min) * ax_h
        c.line(ax_x, ty, ax_x + ax_w, ty, color=C_GRID, width=1.0)
        c.text(ax_x - 10, ty - 7, f"{tick}", size=11, color=C_MUTED, anchor="end")
    c.text(px + 18, ax_y + 10, "µs/q", size=12, color=C_MUTED, bold=True)
    c.text(ax_x, ax_y + ax_h + 55, "Trục tung bắt đầu từ 3000 µs để nhìn rõ độ chênh -218.4 µs", size=11, color=C_AMBER, bold=True)

    by_id = {r["arm_id"]: r for r in arms}
    groups = [
        ("Stock\n(3 graphs)", float(by_id["stock_base"]["mean_us"]), float(by_id["stock_opt"]["mean_us"]), "-6.032%"),
        ("Fast v2\n(3 graphs)", float(by_id["fast_base"]["mean_us"]), float(by_id["fast_opt"]["mean_us"]), "-6.034%"),
        ("Gộp 6 Graphs\n(Primary)", float(by_id["overall_base"]["mean_us"]), float(by_id["overall_opt"]["mean_us"]), "-6.033%"),
    ]
    bw = 66
    for gi, (glabel, vbase, vopt, dpct) in enumerate(groups):
        gx = ax_x + 56 + gi * 184
        h_b = (vbase - y_min) / (y_max - y_min) * ax_h
        h_o = (vopt - y_min) / (y_max - y_min) * ax_h
        c.rect(gx, ax_y + ax_h - h_b, bw, h_b, fill=C_STEEL, stroke=C_NAVY, stroke_w=1.2, radius=4)
        c.rect(gx + bw + 14, ax_y + ax_h - h_o, bw, h_o, fill=C_TEAL, stroke=C_NAVY, stroke_w=1.2, radius=4)
        c.text(gx + bw / 2, ax_y + ax_h - h_b - 22, f"{vbase:.2f}", size=12, color=C_NAVY, bold=True, anchor="middle")
        c.text(gx + bw + 14 + bw / 2, ax_y + ax_h - h_o - 22, f"{vopt:.2f}", size=12, color=C_TEAL, bold=True, anchor="middle")
        c.badge(gx + bw + 7, ax_y + ax_h - h_b - 54, dpct, bg=C_LIGHT_GREEN, fg=C_GREEN, size=12, anchor="middle")
        for li, ln in enumerate(glabel.split("\n")):
            c.text(gx + bw + 7, ax_y + ax_h + 12 + li * 17, ln, size=12, color=C_INK, bold=(li == 0), anchor="middle")

    # Panel B (Right): Forest Plot of 4 CI Families + Graph Population NOT_ESTIMABLE
    qx, qy, qw, qh = 782, 126, 846, 710
    c.rect(qx, qy, qw, qh, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(qx + 20, qy + 16, "B. Phân biệt 4 Họ Khoảng Tin Cậy 95% (Mức giảm Latency %)", size=16, color=C_NAVY, bold=True)
    c.text(qx + 20, qy + 40, "Ước lượng điểm: 6.033% (1.0642×) • Ngưỡng GO tiền đăng ký θ = 3.0% (vượt >2× ngưỡng)", size=12, color=C_MUTED)

    fx, fy, fw, fh = qx + 250, qy + 92, 560, 490
    x_min, x_max = 2.5, 6.6
    c.rect(fx, fy, fw, fh, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.2)
    for tick in [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]:
        tx = fx + (tick - x_min) / (x_max - x_min) * fw
        c.line(tx, fy, tx, fy + fh, color=C_GRID, width=1.0)
        c.text(tx, fy + fh + 10, f"{tick:.1f}%", size=11, color=C_MUTED, anchor="middle")
    c.text(fx + fw / 2, fy + fh + 32, "Mức giảm Geo Mean Latency OFF (%)", size=12, color=C_INK, bold=True, anchor="middle")

    # Pre-registered threshold theta = 3.0%
    th_x = fx + (3.0 - x_min) / (x_max - x_min) * fw
    c.line(th_x, fy, th_x, fy + fh, color=C_CORAL, width=2.2, dashed=True)
    c.badge(th_x + 6, fy + 10, "Ngưỡng GO: θ = 3.0%", bg=C_LIGHT_RED, fg=C_CORAL, size=11)

    # Point estimate vertical line
    pt_x = fx + (6.033151 - x_min) / (x_max - x_min) * fw
    c.line(pt_x, fy, pt_x, fy + fh - 95, color=C_TEAL, width=1.6, dashed=True)

    colors_ci = [C_NAVY, C_STEEL, C_PURPLE, C_TEAL, C_CORAL]
    for i, r in enumerate(cis):
        ry = fy + 76 + i * 92
        c.text(fx - 14, ry - 14, r["ci_family"], size=13, color=C_CORAL if r["status"] == "NOT_ESTIMABLE" else C_INK, bold=True, anchor="end")
        c.wrap_text(fx - 14, ry + 6, r["scope"], max_w=228, size=10, color=C_MUTED, anchor="end", line_h=14, max_lines=2)
        if r["status"] == "ESTIMATED":
            lo = float(r["low_pct"])
            hi = float(r["high_pct"])
            pt = float(r["point_pct"])
            x_lo = fx + (lo - x_min) / (x_max - x_min) * fw
            x_hi = fx + (hi - x_min) / (x_max - x_min) * fw
            x_pt = fx + (pt - x_min) / (x_max - x_min) * fw
            col = colors_ci[i]
            # Draw visibly clear whisker + caps
            c.line(x_lo, ry, x_hi, ry, color=col, width=4.0)
            c.line(x_lo, ry - 9, x_lo, ry + 9, color=col, width=2.5)
            c.line(x_hi, ry - 9, x_hi, ry + 9, color=col, width=2.5)
            c.circle(x_pt, ry, 6.5, fill=col, stroke="#FFFFFF", stroke_w=1.5)
            c.text(x_lo - 12, ry - 8, f"[{lo:.3f}%, {hi:.3f}%]", size=12, color=col, bold=True, anchor="end")
        else:
            c.rect(fx + 20, ry - 20, fw - 40, 40, fill=C_LIGHT_RED, stroke=C_CORAL, stroke_w=1.8, radius=6)
            c.text(fx + fw / 2, ry - 8, "NOT_ESTIMABLE — 6 đồ thị chung SEED=555 (không suy rộng quần thể)", size=12, color=C_CORAL, bold=True, anchor="middle")

    # Zoom inset note
    c.rect(qx + 20, qy + 622, qw - 40, 70, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=1.4, radius=8)
    c.wrap_text(
        qx + 34,
        qy + 634,
        "Lưu ý thống kê bắt buộc: Block-t đo độ lặp qua block, query-only lấy mẫu lại query, joint lấy mẫu lại cả hai. Sáu đồ thị giữ cố định trong mọi CI.",
        max_w=qw - 68,
        size=12,
        color=C_INK,
        line_h=19,
    )

    c.footer(
        "axd-g2-v2-off-design3_1_run2-analysis.json (f0a35394...) • audit_results.json • tables/table05 & table06",
        "Verdict: GO_A_FIXED_COHORT • EXPLORATORY_HOST_SPECIFIC • Không suy rộng sang p=4, host khác hay dataset khác.",
    )
    c.save("fig09_mean_latency_and_cis")


# ---------------------------------------------------------------------------
# Figure 10: Latency Quantiles (Mean, P50, P95, P99)
# ---------------------------------------------------------------------------
def build_fig10() -> None:
    rows = load_csv("table07_latency_quantiles.csv")
    c = DualCanvas(1600, 920)
    c.header(
        "Hình 10 · Phân bố Độ trễ Truy vấn OFF: Mean, P50, P95 và P99 (µs/truy vấn)",
        "G2 v2 design-3.1 run2 (144/144 OFF, gộp 6 đồ thị R90 v1.3) • MS-Turing-1M • Ryzen 5 PRO 4650U, p=2, S=16, b432, jobs=1",
    )
    ax_x, ax_y, ax_w, ax_h = 130, 155, 1390, 595
    y_min, y_max = 0.0, 4800.0
    c.rect(ax_x, ax_y, ax_w, ax_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.5)

    # Legend
    c.rect(1120, 112, 18, 18, fill=C_STEEL, radius=3)
    c.text(1146, 113, "Baseline (72 OFF proc)", size=13, color=C_INK, bold=True)
    c.rect(1340, 112, 18, 18, fill=C_TEAL, radius=3)
    c.text(1366, 113, "B1+A1 (72 OFF proc)", size=13, color=C_INK, bold=True)

    for tick in range(0, 4801, 600):
        ty = ax_y + ax_h - (tick - y_min) / (y_max - y_min) * ax_h
        c.line(ax_x, ty, ax_x + ax_w, ty, color=C_GRID, width=1.0)
        c.text(ax_x - 14, ty - 7, f"{tick}", size=12, color=C_MUTED, anchor="end")
    c.text(22, ax_y + ax_h / 2 - 24, "Độ trễ", size=13, color=C_INK, bold=True)
    c.text(22, ax_y + ax_h / 2 - 4, "(µs/q)", size=13, color=C_MUTED)

    bw = 98
    slot = ax_w / len(rows)
    for i, r in enumerate(rows):
        cx = ax_x + slot * (i + 0.5)
        vb = float(r["base_us"])
        vo = float(r["opt_us"])
        dp = float(r["change_pct"])
        hb = vb / y_max * ax_h
        ho = vo / y_max * ax_h
        c.rect(cx - bw - 10, ax_y + ax_h - hb, bw, hb, fill=C_STEEL, stroke=C_NAVY, stroke_w=1.4, radius=5)
        c.rect(cx + 10, ax_y + ax_h - ho, bw, ho, fill=C_TEAL, stroke=C_NAVY, stroke_w=1.4, radius=5)
        c.text(cx - bw / 2 - 10, ax_y + ax_h - hb - 24, f"{vb:.1f}", size=13, color=C_NAVY, bold=True, anchor="middle")
        c.text(cx + bw / 2 + 10, ax_y + ax_h - ho - 24, f"{vo:.1f}", size=13, color=C_TEAL, bold=True, anchor="middle")
        c.badge(cx, ax_y + ax_h - hb - 58, f"{dp:+.2f}% ({float(r['delta_us']):+.1f} µs)", bg=C_LIGHT_GREEN, fg=C_GREEN, size=12, anchor="middle")
        c.text(cx, ax_y + ax_h + 14, r["metric"], size=15, color=C_INK, bold=True, anchor="middle")
        c.text(cx, ax_y + ax_h + 38, r["pre_reg_bound"], size=11, color=C_MUTED, anchor="middle")

    c.footer(
        "audit_results.json (overall_secondary, tail_log_upper) • tables/table07_latency_quantiles.csv",
        "Đuôi P95/P99 đều CẢI THIỆN (giảm -4.22% / -4.09%, biên trên -3.87% / -3.78% xa dưới trần +5% / +10%); đây là single-stream latency (jobs=1), không phải serving tail dưới tải đồng thời.",
    )
    c.save("fig10_latency_quantiles_p50_p95_p99")


# ---------------------------------------------------------------------------
# Figure 11: Single-Stream Batch QPS (jobs=1)
# ---------------------------------------------------------------------------
def build_fig11() -> None:
    rows = load_csv("table08_qps_by_arm.csv")
    c = DualCanvas(1600, 900)
    c.header(
        "Hình 11 · Thông lượng của một luồng truy vấn QPS_wall (jobs=1, Host D — Measured OFF)",
        "G2 v2 design-3.1 run2 (144/144 OFF) • MS-Turing-1M (v2_test_10000) • p=2, S=16, beam=432 • Cao hơn là tốt hơn",
    )
    ax_x, ax_y, ax_w, ax_h = 140, 165, 1020, 560
    y_min, y_max = 0.0, 340.0
    c.rect(ax_x, ax_y, ax_w, ax_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.5)

    for tick in range(0, 341, 50):
        ty = ax_y + ax_h - tick / y_max * ax_h
        c.line(ax_x, ty, ax_x + ax_w, ty, color=C_GRID, width=1.0)
        c.text(ax_x - 14, ty - 7, f"{tick}", size=12, color=C_MUTED, anchor="end")
    c.text(44, ax_y + ax_h / 2 - 14, "QPS_wall", size=13, color=C_INK, bold=True)
    c.text(44, ax_y + ax_h / 2 + 8, "(q/s, jobs=1)", size=11, color=C_MUTED)

    bw = 96
    slot = ax_w / len(rows)
    for i, r in enumerate(rows):
        cx = ax_x + slot * (i + 0.5)
        vb = float(r["base_qps"])
        vo = float(r["opt_qps"])
        gp = float(r["gain_pct"])
        hb = vb / y_max * ax_h
        ho = vo / y_max * ax_h
        c.rect(cx - bw - 10, ax_y + ax_h - hb, bw, hb, fill=C_STEEL, stroke=C_NAVY, stroke_w=1.4, radius=5)
        c.rect(cx + 10, ax_y + ax_h - ho, bw, ho, fill=C_TEAL, stroke=C_NAVY, stroke_w=1.4, radius=5)
        c.text(cx - bw / 2 - 10, ax_y + ax_h - hb - 24, f"{vb:.2f}", size=13, color=C_NAVY, bold=True, anchor="middle")
        c.text(cx + bw / 2 + 10, ax_y + ax_h - ho - 24, f"{vo:.2f}", size=13, color=C_TEAL, bold=True, anchor="middle")
        c.badge(cx, ax_y + ax_h - ho - 60, f"+{gp:.2f}%", bg=C_LIGHT_GREEN, fg=C_GREEN, size=13, anchor="middle")
        c.text(cx, ax_y + ax_h + 16, r["arm"], size=14, color=C_INK, bold=True, anchor="middle")

    # Side callout box
    c.rect(1196, 165, 368, 560, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(1216, 185, "CHÚ GIẢI & RANH GIỚI ĐO", size=14, color=C_NAVY, bold=True)
    c.rect(1216, 224, 18, 18, fill=C_STEEL, radius=3)
    c.text(1244, 224, "Baseline (flat + full)", size=13, color=C_INK, bold=True)
    c.rect(1216, 254, 18, 18, fill=C_TEAL, radius=3)
    c.text(1244, 254, "B1+A1 (bar_all + inc)", size=13, color=C_INK, bold=True)
    c.line(1216, 290, 1544, 290, color=C_GRID, width=1.2)
    c.wrap_text(
        1216,
        306,
        "1. Định nghĩa QPS_wall: 10,000 / batch_wall_s đo trên batch truy vấn tuần tự (jobs = 1, 2 worker xử lý cùng 1 truy vấn).\n\n"
        "2. Mức tăng đồng đều trên cả hai nhánh:\n   • Stock: 276.24 → 293.97 (+6.42%)\n   • Fast v2: 276.26 → 294.00 (+6.42%)\n   • Gộp 6 graph: 276.25 → 293.99 (+6.42%)\n\n"
        "3. Lưu ý tài nguyên: Peak RSS giữ phẳng (871,696 → 871,705 KiB, +9.4 KiB; 72/72 PASS). Process CPU-s (toàn cửa sổ tiến trình, gồm ~3.9 s load/warmup/JSONL) giảm 76.12 → 70.74 s (-7.07%).",
        max_w=328,
        size=12,
        color=C_INK,
        line_h=19,
    )
    c.rect(1216, 620, 328, 86, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=1.5, radius=8)
    c.wrap_text(
        1228,
        632,
        "Cảnh báo: QPS_wall (jobs=1) là tốc độ xử lý một luồng truy vấn, KHÔNG PHẢI concurrent multi-query serving throughput (D10).",
        max_w=304,
        size=12,
        color=C_INK,
        bold=True,
        line_h=19,
    )

    c.footer(
        "audit_results.json (cells_2x2, overall_secondary) • tables/table08_qps_by_arm.csv",
        "Chỉ áp dụng cho cấu hình p=2, S=16, beam=432, jobs=1 trên AMD Ryzen 5 PRO 4650U; không so trực tiếp với QPS 1-luồng AVX-512 của Host A.",
    )
    c.save("fig11_qps_comparison")


# ---------------------------------------------------------------------------
# Figure 12: Duplicate L2 & Total L2 Decomposition (Quality ON 18/18)
# ---------------------------------------------------------------------------
def build_fig12() -> None:
    rows = load_csv("table09_on_l2_counters.csv")
    by_k = {r["counter"]: r for r in rows}
    c = DualCanvas(1680, 940)
    c.header(
        "Hình 12 · Cơ chế Cắt giảm Phép tính Khoảng cách L2 & Bảo toàn 1-đổi-1 (Quality ON 18/18)",
        "Giá trị kiểm toán chính xác từ audit_results.json (MS-Turing-1M, 6 đồ thị R90 v1.3, beam=432, p=2, S=16)",
    )
    # Panel A: Stacked Total L2 = Unique L2 + Duplicate L2
    px, py, pw, ph = 48, 124, 780, 724
    c.rect(px, py, pw, ph, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(px + 20, py + 16, "A. Phân rã Tổng số phép tính L2 / truy vấn", size=16, color=C_NAVY, bold=True)
    c.text(px + 20, py + 40, "Unique L2 giữ bất biến (Δ = 0); Duplicate L2 giảm -74.98% → Total L2 giảm -12.22%", size=12, color=C_MUTED)

    ax_x, ax_y, ax_w, ax_h = px + 96, py + 108, 636, 480
    y_max = 26000.0
    c.rect(ax_x, ax_y, ax_w, ax_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.2)
    for tick in range(0, 26001, 5000):
        ty = ax_y + ax_h - tick / y_max * ax_h
        c.line(ax_x, ty, ax_x + ax_w, ty, color=C_GRID, width=1.0)
        c.text(ax_x - 10, ty - 7, f"{tick:,}", size=11, color=C_MUTED, anchor="end")

    uniq = float(by_k["unique_distance_evaluations"]["base_mean"])
    dup_b = float(by_k["duplicate_distance_evaluations"]["base_mean"])
    dup_o = float(by_k["duplicate_distance_evaluations"]["opt_mean"])
    tot_b = float(by_k["distance_evaluations"]["base_mean"])
    tot_o = float(by_k["distance_evaluations"]["opt_mean"])

    for bi, (lbl, dval, tval, cx) in enumerate([
        ("Baseline (flat+full)", dup_b, tot_b, ax_x + 175),
        ("B1+A1 (bar_all+inc)", dup_o, tot_o, ax_x + 455),
    ]):
        bw = 150
        hu = uniq / y_max * ax_h
        hd = dval / y_max * ax_h
        # Unique bottom segment
        c.rect(cx - bw / 2, ax_y + ax_h - hu, bw, hu, fill=C_NAVY, stroke="#FFFFFF", stroke_w=1.5)
        # Duplicate top segment
        c.rect(cx - bw / 2, ax_y + ax_h - hu - hd, bw, hd, fill=C_CORAL if bi == 0 else C_AMBER, stroke="#FFFFFF", stroke_w=1.5)
        c.text(cx, ax_y + ax_h - hu / 2 - 8, "Unique L2", size=12, color="#FFFFFF", bold=True, anchor="middle")
        c.text(cx, ax_y + ax_h - hu / 2 + 10, f"{uniq:,.1f}", size=13, color="#E0F2FE", bold=True, anchor="middle")
        if hd > 34:
            c.text(cx, ax_y + ax_h - hu - hd / 2 - 7, f"Dup: {dval:,.1f}", size=12, color="#FFFFFF", bold=True, anchor="middle")
        else:
            c.text(cx + bw / 2 + 10, ax_y + ax_h - hu - hd / 2 - 8, f"Dup: {dval:,.1f}", size=12, color=C_AMBER, bold=True)
        c.text(cx, ax_y + ax_h - hu - hd - 26, f"Total: {tval:,.1f}", size=14, color=C_INK, bold=True, anchor="middle")
        c.text(cx, ax_y + ax_h + 14, lbl, size=14, color=C_INK, bold=True, anchor="middle")

    c.badge(ax_x + 455, ax_y + 18, "Total L2: -2,784.04 (-12.22%)", bg=C_LIGHT_GREEN, fg=C_GREEN, size=13, anchor="middle")

    # Legend inside panel A bottom
    c.rect(px + 96, py + 640, 16, 16, fill=C_NAVY, radius=3)
    c.text(px + 120, py + 640, "Unique L2 (19,064.16, Δ=0)", size=12, color=C_INK)
    c.rect(px + 340, py + 640, 16, 16, fill=C_CORAL, radius=3)
    c.text(px + 364, py + 640, "Dup L2 Base (3,712.81)", size=12, color=C_INK)
    c.rect(px + 540, py + 640, 16, 16, fill=C_AMBER, radius=3)
    c.text(px + 564, py + 640, "Dup L2 B1+A1 (928.77)", size=12, color=C_INK)
    c.text(px + 96, py + 676, "Bất biến quỹ đạo (Δ=0): expansions = 456.68 | sync_rounds = 14.87 | neighbor_attempts = 26,069.22", size=12, color=C_MUTED, bold=True)

    # Panel B: 1-to-1 conservation (Already-seen jump) + Why -12.22% L2 -> -6.03% OFF
    qx, qy, qw, qh = 856, 124, 776, 724
    c.rect(qx, qy, qw, qh, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(qx + 20, qy + 16, "B. Chuyển dịch 1-đổi-1 (Already-Seen) & Liên hệ Độ trễ OFF", size=16, color=C_NAVY, bold=True)
    c.text(qx + 20, qy + 40, "Đỉnh từng bị tính lại L2 nay bị chặn ở O(1) qua settled_epoch_ (Δ = ±2,784.04/q)", size=12, color=C_MUTED)

    bx_x, bx_y, bx_w, bx_h = qx + 96, qy + 94, 636, 260
    c.rect(bx_x, bx_y, bx_w, bx_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.2)
    b_max = 7500.0
    for tick in [0, 2000, 4000, 6000]:
        ty = bx_y + bx_h - tick / b_max * bx_h
        c.line(bx_x, ty, bx_x + bx_w, ty, color=C_GRID, width=1.0)
        c.text(bx_x - 10, ty - 7, f"{tick:,}", size=11, color=C_MUTED, anchor="end")

    as_b = float(by_k["already_seen_attempts"]["base_mean"])
    as_o = float(by_k["already_seen_attempts"]["opt_mean"])
    pairs = [
        ("Duplicate L2 / q", dup_b, dup_o, "-2,784.04 (-74.98%)", C_CORAL, C_TEAL),
        ("Already-Seen / q", as_b, as_o, "+2,784.04 (+84.54%)", C_STEEL, C_NAVY),
    ]
    for pi, (plbl, v1, v2, ptxt, c1, c2) in enumerate(pairs):
        pxc = bx_x + 165 + pi * 310
        h1, h2 = v1 / b_max * bx_h, v2 / b_max * bx_h
        c.rect(pxc - 72, bx_y + bx_h - h1, 64, h1, fill=c1, radius=4)
        c.rect(pxc + 8, bx_y + bx_h - h2, 64, h2, fill=c2, radius=4)
        c.text(pxc - 40, bx_y + bx_h - h1 - 20, f"{v1:,.1f}", size=11, color=c1, bold=True, anchor="middle")
        c.text(pxc + 40, bx_y + bx_h - h2 - 20, f"{v2:,.1f}", size=11, color=c2, bold=True, anchor="middle")
        c.badge(pxc, bx_y + 12, ptxt, bg=C_LIGHT_TEAL if pi == 0 else C_LIGHT_BLUE, fg=C_NAVY, size=11, anchor="middle")
        c.text(pxc, bx_y + bx_h + 10, plbl, size=13, color=C_INK, bold=True, anchor="middle")

    # Explanation box: Why -74.98% dup L2 -> -12.22% total L2 -> -6.03% OFF latency
    c.rect(qx + 28, qy + 398, qw - 56, 304, fill="#FFFFFF", stroke=C_NAVY, stroke_w=1.6, radius=8)
    c.text(qx + 46, qy + 414, "TẠI SAO GIẢM 74.98% DUPLICATE L2 NHƯNG LATENCY CHỈ GIẢM 6.03%?", size=13, color=C_NAVY, bold=True)
    bullets = [
        "1. Duplicate L2 chỉ chiếm 16.30% tổng L2 ban đầu (3,712.8 / 22,777.0) ⇒ giảm 74.98% phần trùng chỉ tương ứng giảm 12.22% tổng số phép tính L2.",
        "2. Định luật Amdahl: Thời gian truy vấn OFF không chỉ có phép tính L2, mà còn gồm duyệt CSR, truy cập bộ nhớ ngẫu nhiên (cache/DRAM), quản lý std::set, spin-wait barrier và pha merge đơn luồng.",
        "3. Truy cập lại một đỉnh có thể tận dụng cache. Tỷ lệ cache hit và chi phí riêng mỗi phép tính L2 chưa được đo.",
        "4. B1 ghi các ID để công bố tại barrier. A1 đưa dispatch vào merge. Thời gian merge ON 348.5 → 384.4 µs/q có ranh giới đo khác nhau giữa hai policy.",
    ]
    cy = qy + 446
    for btxt in bullets:
        cy = c.wrap_text(qx + 46, cy, btxt, max_w=qw - 92, size=12, color=C_INK, line_h=18) + 10

    c.footer(
        "audit_results.json (quality_mechanism, 18/18 ON, 100% parity) • tables/table09_on_l2_counters.csv",
        "Đính chính minh bạch erratum #1: dùng số chính xác 19,064.16 / 3,712.81 / 928.77 từ audit_results.json thay cho số làm tròn ghi tay trong bản tường thuật cũ. PMU NOT_MEASURED.",
    )
    c.save("fig12_duplicate_and_total_l2")


# ---------------------------------------------------------------------------
# Figure 13: Per-Graph R90 Results (6/6 Graphs + LOO Stability)
# ---------------------------------------------------------------------------
def build_fig13() -> None:
    rows = load_csv("table10_per_graph_r90.csv")
    c = DualCanvas(1680, 940)
    c.header(
        "Hình 13 · Độ ổn định Theo từng Đồ thị R90 P0A v1.3 (6/6 Graphs + Leave-One-Out)",
        "Mọi đồ thị Stock r1–r3 & Fast r1–r3 đều đạt giảm latency ~6.00%–6.08% (xa trên ngưỡng 3.0%) và Recall@10 ≥ 0.99197",
    )
    # Left forest plot
    fx, fy, fw, fh = 220, 148, 760, 620
    x_min, x_max = 5.6, 6.4
    c.rect(fx, fy, fw, fh, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.5)
    for tick in [5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4]:
        tx = fx + (tick - x_min) / (x_max - x_min) * fw
        c.line(tx, fy, tx, fy + fh, color=C_GRID, width=1.0)
        c.text(tx, fy + fh + 12, f"{tick:.1f}%", size=11, color=C_MUTED, anchor="middle")
    c.text(fx + fw / 2, fy + fh + 38, "Mức giảm Geo Mean Latency OFF theo từng đồ thị (% ± 95% CI, df=11)", size=13, color=C_INK, bold=True, anchor="middle")

    # Pooled mean line & LOO band
    loo_lo = min(float(r["loo_reduction_pct"]) for r in rows)
    loo_hi = max(float(r["loo_reduction_pct"]) for r in rows)
    x_loo1 = fx + (loo_lo - x_min) / (x_max - x_min) * fw
    x_loo2 = fx + (loo_hi - x_min) / (x_max - x_min) * fw
    c.rect(x_loo1, fy, x_loo2 - x_loo1, fh, fill=C_LIGHT_TEAL)
    x_mean = fx + (6.033151 - x_min) / (x_max - x_min) * fw
    c.line(x_mean, fy, x_mean, fy + fh, color=C_TEAL, width=2.2, dashed=True)
    c.badge(x_mean, fy + 10, f"Gộp 6 graph: 6.033% | LOO: [{loo_lo:.3f}%, {loo_hi:.3f}%]", bg=C_LIGHT_TEAL, fg=C_NAVY, size=11, anchor="middle")

    # Separator between Stock and Fast
    c.line(fx, fy + 332, fx + fw, fy + 332, color=C_BORDER, width=1.4, dashed=True)
    c.text(fx + 14, fy + 52, "NHÁNH STOCK (3 graphs)", size=12, color=C_NAVY, bold=True)
    c.text(fx + 14, fy + 344, "NHÁNH FAST v2 (3 graphs)", size=12, color=C_TEAL, bold=True)

    for i, r in enumerate(rows):
        ry = fy + (98 + i * 80 if i < 3 else 390 + (i - 3) * 80)
        col = C_NAVY if r["arm"] == "Stock" else C_TEAL
        red = float(r["geo_reduction_pct"])
        lo = float(r["geo_ci95_low_pct"])
        hi = float(r["geo_ci95_high_pct"])
        x_pt = fx + (red - x_min) / (x_max - x_min) * fw
        x_lo = fx + (lo - x_min) / (x_max - x_min) * fw
        x_hi = fx + (hi - x_min) / (x_max - x_min) * fw
        c.text(fx - 16, ry - 8, r["graph"], size=13, color=col, bold=True, anchor="end", mono=True)
        c.line(x_lo, ry, x_hi, ry, color=col, width=3.5)
        c.line(x_lo, ry - 9, x_lo, ry + 9, color=col, width=2.2)
        c.line(x_hi, ry - 9, x_hi, ry + 9, color=col, width=2.2)
        c.circle(x_pt, ry, 7.0, fill=col, stroke="#FFFFFF", stroke_w=1.5)
        c.text(x_hi + 10, ry - 8, f"{red:.3f}% [{lo:.3f}, {hi:.3f}]", size=11, color=col, bold=True)

    # Right compact table of exact per-graph stats
    tx, ty, tw, th = 1010, 148, 634, 620
    c.rect(tx, ty, tw, th, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(tx + 18, ty + 16, "CHI TIẾT TỪNG ĐỒ THỊ R90 v1.3 (12 BLOCK / GRAPH)", size=14, color=C_NAVY, bold=True)
    tcols = [
        ("Graph", 126),
        ("Recall@10", 88),
        ("Base (µs)", 86),
        ("Opt (µs)", 86),
        ("QPS Opt", 78),
        ("Dup L2", 74),
        ("LOO %", 68),
    ]
    hy = ty + 52
    c.rect(tx + 14, hy, tw - 28, 36, fill=C_NAVY, radius=5)
    cx = tx + 14
    for lbl, w in tcols:
        c.text(cx + 8, hy + 10, lbl, size=11, color="#FFFFFF", bold=True)
        cx += w

    for i, r in enumerate(rows):
        ry = hy + 42 + i * 68
        c.rect(tx + 14, ry, tw - 28, 60, fill="#FFFFFF" if i % 2 == 0 else C_LIGHT_SLATE, stroke=C_GRID, stroke_w=1.0, radius=4)
        vals = [
            r["graph"],
            f"{float(r['recall_mean']):.5f}",
            f"{float(r['mean_base_us']):.2f}",
            f"{float(r['mean_opt_us']):.2f}",
            f"{float(r['qps_opt']):.2f}",
            f"-{float(r['dup_l2_reduction_pct']):.2f}%",
            f"{float(r['loo_reduction_pct']):.3f}%",
        ]
        cx = tx + 14
        for vi, (val, (_, w)) in enumerate(zip(vals, tcols)):
            c.text(cx + 8, ry + 20, val, size=11, color=C_NAVY if vi == 0 else C_INK, bold=(vi in (0, 3)), mono=(vi == 0))
            cx += w

    c.rect(tx + 14, ty + 510, tw - 28, 92, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=1.4, radius=8)
    c.wrap_text(
        tx + 28,
        ty + 522,
        "Kiểm tra tính ổn định (Stability Gate PASS): 6/6 đồ thị > 0% và > 5.99%; cả Stock (6.032%) và Fast (6.034%) ≥ 3%; cả 6 giá trị Leave-One-Out nằm trong [6.023%, 6.040%]. Lưu ý: 3 bản r1–r3 chung SEED=555.",
        max_w=tw - 56,
        size=11,
        color=C_INK,
        line_h=18,
    )

    c.footer(
        "audit_results.json (per_graph, quality_mechanism) • tables/table10_per_graph_r90.csv",
        "Độ phân tán cực nhỏ giữa 6 đồ thị phản ánh tính nhất quán trên cohort R90 cố định, không chứng minh phương sai thấp trên RNG seed mới.",
    )
    c.save("fig13_per_graph_r90_results")


# ---------------------------------------------------------------------------
# Figure 14: Measured BUILD Comparison (Host A Historical Receipts)
# ---------------------------------------------------------------------------
def build_fig14() -> None:
    rows = load_csv("table11_measured_build_host_a.csv")
    c = DualCanvas(1600, 900)
    c.header(
        "Hình 14 · So sánh Thời gian Xây dựng Đồ thị BUILD (Measured trên Host A — Task A)",
        "6 biên nhận lịch sử R90 P0A v1.3 (MS-Turing-1M, C160/K1024/N2, 4 build threads, H85 Highway 6bc2d477...)",
    )
    # Left panel: BUILD wall time per graph + arm mean
    ax_x, ax_y, ax_w, ax_h = 120, 165, 920, 560
    y_max = 50.0
    c.rect(ax_x, ax_y, ax_w, ax_h, fill="#FFFFFF", stroke=C_BORDER, stroke_w=1.5)
    for tick in range(0, 51, 10):
        ty = ax_y + ax_h - tick / y_max * ax_h
        c.line(ax_x, ty, ax_x + ax_w, ty, color=C_GRID, width=1.0)
        c.text(ax_x - 14, ty - 7, f"{tick} s", size=12, color=C_MUTED, anchor="end")
    c.text(36, ax_y + ax_h / 2 - 14, "BUILD Wall", size=13, color=C_INK, bold=True)
    c.text(36, ax_y + ax_h / 2 + 6, "(giây, Host A)", size=11, color=C_MUTED)

    bars = [
        ("stock_r1", float(rows[0]["wall_s"]), C_STEEL, False),
        ("stock_r2", float(rows[1]["wall_s"]), C_STEEL, False),
        ("stock_r3", float(rows[2]["wall_s"]), C_STEEL, False),
        ("Mean Stock", 42.2567, C_NAVY, True),
        ("fast_r1", float(rows[3]["wall_s"]), C_TEAL, False),
        ("fast_r2", float(rows[4]["wall_s"]), C_TEAL, False),
        ("fast_r3", float(rows[5]["wall_s"]), C_TEAL, False),
        ("Mean Fast v2", 33.7933, C_GREEN, True),
    ]
    bw = 74
    slot = ax_w / len(bars)
    for i, (lbl, val, col, is_mean) in enumerate(bars):
        cx = ax_x + slot * (i + 0.5)
        bh = val / y_max * ax_h
        c.rect(cx - bw / 2, ax_y + ax_h - bh, bw, bh, fill=col, stroke=C_INK if is_mean else C_NAVY, stroke_w=2.0 if is_mean else 1.2, radius=5)
        c.text(cx, ax_y + ax_h - bh - 22, f"{val:.2f}s", size=12, color=col, bold=True, anchor="middle")
        c.text(cx, ax_y + ax_h + 14, lbl, size=11, color=C_INK if is_mean else C_MUTED, bold=is_mean, anchor="middle")
    c.line(ax_x + 4 * slot, ax_y + 12, ax_x + 4 * slot, ax_y + ax_h - 12, color=C_BORDER, width=1.6, dashed=True)
    c.badge(ax_x + 6 * slot, ax_y + 22, "Fast v2 vs Stock: -8.463 s (-20.03%)", bg=C_LIGHT_GREEN, fg=C_GREEN, size=14, anchor="middle")

    # Right panel: Provenance & Resource Neutrality
    rx, ry, rw, rh = 1080, 165, 484, 560
    c.rect(rx, ry, rw, rh, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(rx + 20, ry + 18, "ĐÓNG GÓP RIÊNG CỦA TASK A (A-OBS)", size=14, color=C_NAVY, bold=True)
    c.line(rx + 20, ry + 48, rx + rw - 20, ry + 48, color=C_GRID, width=1.2)
    info = [
        ("Cơ chế Fast v2 (Task A)", "H17 Packed Top-2 + FP32 prefilter trước bước đóng gói (so với H17, Fast giảm 97.45% pack calls và 48.06% phép so sánh nguồn trên MS-Turing-1M)."),
        ("Thời gian BUILD (4 threads)", "Stock: 42.257 s (42.57 / 41.99 / 42.21)\nFast v2: 33.793 s (33.84 / 33.74 / 33.80)\nTiết kiệm: 8.463 s / chỉ mục (-20.03%)."),
        ("Dung lượng đồ thị & Peak RSS", "Tổng 6 đồ thị: 1,292,447,108 B (~215.4 MB/graph, lệch +0.020%).\nBUILD Peak RSS trung bình: 2.9743 GiB (Stock), 2.9712 GiB (Fast v2)."),
        ("Tách bạch quyền sở hữu", "Các con số BUILD này thuộc đóng góp đo đạc của Task A trên Host A (tai-linux), được khóa bằng SHA-256 trong axd_g2_v2_build_reference.json — KHÔNG chạy lại trên Host D trong G2."),
    ]
    cy = ry + 64
    for title, desc in info:
        c.text(rx + 20, cy, f"■ {title}", size=13, color=C_NAVY, bold=True)
        cy = c.wrap_text(rx + 30, cy + 22, desc, max_w=rw - 50, size=12, color=C_INK, line_h=18) + 18

    c.footer(
        "configs/axd_g2_v2_build_reference.json (c9ad18b0...) • Task A R90_P0A_V13_NATIVE_24_RESULTS • tables/table11_measured_build_host_a.csv",
        "Host A dùng 4 luồng với cùng seed. Phương sai qua các seed khác chưa ước lượng được. Kiểm toán khớp SHA-256 của cả sáu đồ thị.",
    )
    c.save("fig14_measured_build_comparison")


# ---------------------------------------------------------------------------
# Figure 15: Modeled Two-Host BUILD-SEARCH (GO_B_SYSTEM_FIXED_COHORT)
# ---------------------------------------------------------------------------
def build_fig15() -> None:
    rows = load_csv("table12_modeled_two_host_build_search.csv")
    c = DualCanvas(1680, 960)
    c.header(
        "Hình 15 · Mô hình Tích hợp Hai Máy BUILD–SEARCH (GO_B_SYSTEM_FIXED_COHORT)",
        "MODELED TWO-HOST: T(Q) = BUILD_HostA + Q × SEARCH_HostD  •  LOẠI TRỪ chi phí transfer/load  •  KHÔNG PHẢI native single-host end-to-end",
    )
    # Warning banner
    c.rect(36, 104, 1608, 42, fill=C_LIGHT_AMBER, stroke=C_AMBER, stroke_w=1.8, radius=6)
    c.text(
        840,
        117,
        "CẢNH BÁO PHẠM VI: Kết hợp cộng tuyến tính Measured BUILD (Host A) + Measured SEARCH (Host D); loại trừ transfer/load (3.91–3.93 s ngoài batch gồm load, warmup, serialize trên Host D); CI điều kiện trên BUILD cố định.",
        size=12,
        color=C_INK,
        bold=True,
        anchor="middle",
    )

    # Left panel: Modeled Total Time T(Q) comparison across 4 arms at Q=100k & Q=1M (normalized relative to stock_base = 100%)
    px, py, pw, ph = 36, 164, 780, 710
    c.rect(px, py, pw, ph, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(px + 20, py + 16, "A. Tổng thời gian mô hình hóa T(Q) theo tải truy vấn Q", size=16, color=C_NAVY, bold=True)
    c.text(px + 20, py + 40, "Tổ hợp fast_opt trội tuyệt đối mọi Q ≥ 1 (break-even = null)", size=12, color=C_MUTED)

    # Compact exact table + visual horizontal bars for Q=1, 10k [DERIVED], 100k, 1M
    q_labels = {
        "1": "Q = 1 (JSON)",
        "10000": "Q = 10,000 [DERIVED]",
        "100000": "Q = 100,000 (JSON · Primary B)",
        "1000000": "Q = 1,000,000 (JSON)",
    }
    arm_series = [
        ("stock_base_s", "Stock + Base", C_SLATE),
        ("fast_base_s", "Fast + Base", C_STEEL),
        ("stock_opt_s", "Stock + B1+A1", C_PURPLE),
        ("fast_opt_s", "Fast + B1+A1", C_TEAL),
    ]
    # Legend
    lx = px + 24
    for _, albl, acol in arm_series:
        c.rect(lx, py + 68, 14, 14, fill=acol, radius=3)
        c.text(lx + 20, py + 67, albl, size=11, color=C_INK, bold=True)
        lx += 176

    for qi, r in enumerate(rows):
        gy = py + 102 + qi * 148
        c.rect(px + 20, gy, pw - 40, 134, fill="#FFFFFF", stroke=C_GRID, stroke_w=1.2, radius=8)
        c.text(px + 34, gy + 8, q_labels[r["Q"]], size=13, color=C_NAVY, bold=True)
        saved = float(r["saved_fast_opt_vs_stock_base_s"])
        spct = float(r["saved_pct"])
        c.badge(px + pw - 34, gy + 6, f"Tiết kiệm ΔT = +{saved:.2f} s (-{spct:.2f}%)", bg=C_LIGHT_GREEN, fg=C_GREEN, size=11, anchor="end")

        vmax = float(r["stock_base_s"])
        bar_x = px + 148
        max_bw = 460
        for ai, (k, albl, acol) in enumerate(arm_series):
            val = float(r[k])
            by = gy + 38 + ai * 22
            bw = (val / vmax) * max_bw
            c.text(bar_x - 8, by + 1, albl, size=11, color=C_INK if ai == 3 else C_MUTED, bold=(ai == 3), anchor="end")
            c.rect(bar_x, by, bw, 16, fill=acol, radius=3)
            c.text(bar_x + bw + 8, by + 1, f"{val:,.2f} s", size=11, color=acol if ai == 3 else C_INK, bold=(ai == 3))

    # Right panel: Decomposition of Modeled Time Saved ΔT(Q) = ΔBUILD (Task A) + ΔSEARCH (Task D)
    qx, qy, qw, qh = 844, 164, 800, 710
    c.rect(qx, qy, qw, qh, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.5, radius=10)
    c.text(qx + 20, qy + 16, "B. Phân rã Thời gian Tiết kiệm Mô hình hóa ΔT(Q) (fast_opt vs stock_base)", size=15, color=C_NAVY, bold=True)
    c.text(qx + 20, qy + 40, "Không phát hiện tương tác 2×2 (+0.037 µs, CI95 [-2.58, +2.66] µs) → phân rã xấp xỉ cộng tính", size=12, color=C_MUTED)

    # Stacked percentage composition bar for each Q + exact seconds annotations
    c.rect(qx + 24, qy + 68, 16, 16, fill=C_NAVY, radius=3)
    c.text(qx + 48, qy + 68, "Đóng góp Task A BUILD (+8.463 s cố định, Host A)", size=12, color=C_INK, bold=True)
    c.rect(qx + 410, qy + 68, 16, 16, fill=C_TEAL, radius=3)
    c.text(qx + 434, qy + 68, "Chênh SEARCH giữa hai ô (Q × 218.73 µs, Host D)", size=12, color=C_INK, bold=True)

    for qi, r in enumerate(rows):
        ry = qy + 114 + qi * 114
        tot_s = float(r["saved_fast_opt_vs_stock_base_s"])
        b_s = float(r["saved_build_component_s"])
        s_s = float(r["saved_search_component_s"])
        b_share = b_s / tot_s
        s_share = s_s / tot_s
        bx, bw_tot = qx + 30, qw - 60

        ci_note = ""
        if r["ci95_low_s"]:
            ci_note = f"  |  t-CI95 [{float(r['ci95_low_s']):.2f}, {float(r['ci95_high_s']):.2f}] s  |  Joint [{float(r['joint_ci95_low_s']):.2f}, {float(r['joint_ci95_high_s']):.2f}] s"
        c.text(bx, ry, f"{q_labels[r['Q']]}   →   Tổng tiết kiệm ΔT = {tot_s:.3f} s{ci_note}", size=12, color=C_INK, bold=True)

        wb = max(2, bw_tot * b_share)
        ws = max(0, bw_tot - wb)
        c.rect(bx, ry + 26, wb, 42, fill=C_NAVY, radius=4)
        if ws > 2:
            c.rect(bx + wb, ry + 26, ws, 42, fill=C_TEAL, radius=4)
        if wb > 140:
            c.text(bx + wb / 2, ry + 40, f"BUILD: {b_s:.2f}s ({b_share*100:.1f}%)", size=11, color="#FFFFFF", bold=True, anchor="middle")
        else:
            c.text(bx + 4, ry + 74, f"BUILD: {b_s:.2f}s ({b_share*100:.1f}%)", size=11, color=C_NAVY, bold=True)
        if ws > 150:
            c.text(bx + wb + ws / 2, ry + 40, f"SEARCH: {s_s:.2f}s ({s_share*100:.1f}%)", size=11, color="#FFFFFF", bold=True, anchor="middle")
        else:
            c.text(bx + bw_tot - 4, ry + 74, f"SEARCH: {s_s:.3f}s ({s_share*100:.1f}%)", size=11, color=C_TEAL, bold=True, anchor="end")

    # Erratum #2 disclosure box
    c.rect(qx + 24, qy + 586, qw - 48, 102, fill=C_LIGHT_BLUE, stroke=C_NAVY, stroke_w=1.5, radius=8)
    c.wrap_text(
        qx + 38,
        qy + 598,
        "Lưu ý quan trọng (Erratum #2 đã hiệu chỉnh):\n"
        "• 30.336 s (Q=100k) và 227.194 s (Q=1M) là THỜI GIAN TIẾT KIỆM MÔ HÌNH HÓA (saved_s = ΔT), KHÔNG PHẢI tổng thời gian chạy.\n"
        "• Tổng thời gian mô hình hóa T(Q) thực tế giảm từ 404.244 → 373.908 s (Q=100k) và 3,662.131 → 3,434.938 s (Q=1M).\n"
        "• Phần BUILD lớn ở Q nhỏ (~100% ở Q=1; 79.5% ở Q=10k); phần SEARCH lớn ở Q cao (72.1% ở Q=100k; 96.3% ở Q=1M).",
        max_w=qw - 76,
        size=11,
        color=C_INK,
        line_h=19,
    )

    c.footer(
        "axd-g2-v2-off-design3_1_run2-analysis.json (build_search) • audit_results.json • tables/table12_modeled_two_host_build_search.csv",
        "Đính chính câu chữ AXD_G2_FINAL_CLOSEOUT_STATUS.md §6 L104; không tuyên bố cộng hưởng hay độc lập tuyệt đối chỉ vì CI tương tác chứa 0.",
    )
    c.save("fig15_modeled_two_host_build_search")


# ---------------------------------------------------------------------------
# Figure 16: Objective Closure Matrix Visual
# ---------------------------------------------------------------------------
def build_fig16() -> None:
    rows = load_csv("table13_objective_closure_summary.csv")
    c = DualCanvas(1700, 1020)
    c.header(
        "Hình 16 · Ma trận Trạng thái Đóng Toàn bộ 26 Yêu cầu Nghiên cứu Task D",
        "Đối chiếu trực tiếp yêu cầu gốc (14/10), điều chỉnh sau góp ý GV (16/10), 3 Mục tiêu, Đề xuất A×D (15/11) & G2 v2 Closeout",
    )
    status_order = [
        "COMPLETE",
        "COMPLETE_WITH_SCOPE",
        "SURVEY_COMPLETE",
        "REFUTED_WITH_SCOPE",
        "NO_GO",
        "HOLD",
        "NOT_RUN",
        "OUT_OF_SCOPE",
        "ADVISOR_DECISION_REQUIRED",
    ]
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in status_order}

    # Top KPI Strip (status breakdown)
    kx = 36
    kw_tot = 1628
    c.rect(kx, 106, kw_tot, 84, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.4, radius=8)
    c.text(kx + 16, 116, f"PHÂN BỐ TRẠNG THÁI TRÊN TỔNG SỐ {len(rows)} YÊU CẦU (KHÔNG TỰ ĐÁNH DẤU TẤT CẢ COMPLETE):", size=12, color=C_NAVY, bold=True)
    bx = kx + 16
    for st in status_order:
        bg, fg = status_style(st)
        bw = c.badge(bx, 144, f"{st}: {counts[st]}", bg=bg, fg=fg, size=11, pad_x=8, pad_y=5)
        bx += bw + 10

    # Two-column grid of 26 requirement cards grouped by A..E
    groups_order = [
        "A. Phân công gốc (14/10 & Tuần 1)",
        "B. Điều chỉnh sau góp ý GV (16/10)",
        "C. Ba Mục tiêu cốt lõi Chuyên đề",
        "D. Đề xuất A×D 15/11 (P0–P6, H1–H3)",
        "E. G2 v2 design-3.1 & Closeout",
    ]
    left_groups = groups_order[:3]
    right_groups = groups_order[3:]

    def draw_group_col(glist: list[str], x_start: float, col_w: float) -> None:
        y = 208
        for g in glist:
            grows = [r for r in rows if r["group"] == g]
            gh = 42 + len(grows) * 44 + 10
            c.rect(x_start, y, col_w, gh, fill=C_PANEL, stroke=C_BORDER, stroke_w=1.4, radius=8)
            c.rect(x_start, y, col_w, 34, fill=C_NAVY, radius=8)
            c.rect(x_start, y + 24, col_w, 10, fill=C_NAVY)
            c.text(x_start + 14, y + 9, f"{g}  ({len(grows)} mục)", size=13, color="#FFFFFF", bold=True)
            for ri, r in enumerate(grows):
                ry = y + 42 + ri * 44
                bg, fg = status_style(r["status"])
                c.rect(x_start + 10, ry, col_w - 20, 36, fill="#FFFFFF", stroke=C_GRID, stroke_w=1.0, radius=5)
                c.text(x_start + 20, ry + 10, r["req_id"], size=12, color=C_NAVY, bold=True, mono=True)
                c.text(x_start + 92, ry + 10, r["short_title"], size=12, color=C_INK)
                c.badge(x_start + col_w - 20, ry + 6, r["status"], bg=bg, fg=fg, size=10, pad_x=7, pad_y=3, anchor="end")
            y += gh + 14

    draw_group_col(left_groups, 36, 796)
    draw_group_col(right_groups, 864, 800)

    c.footer(
        "TASK_D_OBJECTIVE_CLOSURE_MATRIX.md • tables/table13_objective_closure_summary.csv",
        "REQ-E4 và REQ-E5 dành cho giảng viên. Xem trạng thái chuẩn bị hồ sơ ở HANDOFF_PROGRESS.md. Trạng thái nghiên cứu: RESEARCH PAUSED.",
    )
    c.save("fig16_objective_closure_matrix")


def main() -> None:
    global FIGURES_DIR, TABLES_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, default=TABLES_DIR)
    parser.add_argument("--output", type=Path, default=FIGURES_DIR)
    args = parser.parse_args()
    TABLES_DIR = args.tables
    FIGURES_DIR = args.output
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        build_fig01, build_fig02, build_fig03, build_fig04,
        build_fig05, build_fig06, build_fig07, build_fig08,
        build_fig09, build_fig10, build_fig11, build_fig12,
        build_fig13, build_fig14, build_fig15, build_fig16,
    ]
    for fn in builders:
        fn()
        print("Generated:", fn.__name__)
    pngs = sorted(FIGURES_DIR.glob("fig*.png"))
    svgs = sorted(FIGURES_DIR.glob("fig*.svg"))
    print(f"Total generated: {len(pngs)} PNGs + {len(svgs)} SVGs in {FIGURES_DIR}")


if __name__ == "__main__":
    main()
