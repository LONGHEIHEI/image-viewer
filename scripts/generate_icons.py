from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
  from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
except ModuleNotFoundError as exc:  # pragma: no cover
  raise SystemExit(
    "Pillow is required to generate icons.\n"
    "Tip: run with backend/.venv on this repo:\n"
    "  backend\\.venv\\Scripts\\python.exe scripts\\generate_icons.py\n"
  ) from exc


@dataclass(frozen=True)
class Brand:
  # Matches frontend/src/style.css
  accent: tuple[int, int, int] = (0xFF, 0x6A, 0x3D)  # #ff6a3d
  accent_2: tuple[int, int, int] = (0xFF, 0xB8, 0x4A)  # #ffb84a
  bg: tuple[int, int, int] = (0xF6, 0xF6, 0xF6)  # #f6f6f6
  ink: tuple[int, int, int] = (0x1B, 0x1E, 0x27)  # #1b1e27


def _lerp(a: int, b: int, t: float) -> int:
  return int(round(a + (b - a) * t))


def _lerp_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
  return (_lerp(a[0], b[0], t), _lerp(a[1], b[1], t), _lerp(a[2], b[2], t))


def _linear_gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
  # Create an RGB vertical gradient, one scanline at a time.
  img = Image.new("RGB", (size, size), top)
  px = img.load()
  for y in range(size):
    t = y / (size - 1) if size > 1 else 0.0
    c = _lerp_rgb(top, bottom, t)
    for x in range(size):
      px[x, y] = c
  return img


def _rounded_rect_mask(size: int, radius: int) -> Image.Image:
  mask = Image.new("L", (size, size), 0)
  d = ImageDraw.Draw(mask)
  d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
  return mask


def _soft_shadow(mask: Image.Image, offset: tuple[int, int], blur: int, color: tuple[int, int, int], alpha: int) -> Image.Image:
  # mask: L image
  shadow = Image.new("RGBA", mask.size, (0, 0, 0, 0))
  layer = Image.new("RGBA", mask.size, (*color, alpha))
  shadow.paste(layer, (0, 0), mask)
  shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
  if offset != (0, 0):
    shadow = ImageChops.offset(shadow, offset[0], offset[1])
  return shadow


def _load_font(px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
  # Prefer common Windows fonts. Fall back to Pillow default.
  candidates = [
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\seguisb.ttf",  # Segoe UI Semibold
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
  ]
  for path in candidates:
    try:
      if os.path.exists(path):
        return ImageFont.truetype(path, px)
    except Exception:
      pass
  return ImageFont.load_default()


def _draw_monogram(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, size: int) -> None:
  font = _load_font(size)
  # Center text in the given box with small optical tweak.
  x0, y0, x1, y1 = box
  w = x1 - x0
  h = y1 - y0
  bbox = d.textbbox((0, 0), text, font=font)
  tw = bbox[2] - bbox[0]
  th = bbox[3] - bbox[1]
  x = x0 + (w - tw) // 2
  y = y0 + (h - th) // 2 - int(round(size * 0.05))
  d.text((x, y), text, font=font, fill=(255, 255, 255, 255))


def make_icon(size: int, *, maskable: bool) -> Image.Image:
  brand = Brand()
  # Background: light gradient for browser tabs and adaptive surfaces.
  bg = _linear_gradient(size, (0xFF, 0xFA, 0xF6), brand.bg).convert("RGBA")

  # Foreground tile: rounded square with brand gradient.
  pad = int(round(size * (0.18 if maskable else 0.10)))
  tile_size = size - pad * 2
  radius = int(round(tile_size * 0.22))
  tile = _linear_gradient(tile_size, brand.accent, brand.accent_2).convert("RGBA")
  tile_mask = _rounded_rect_mask(tile_size, radius)
  tile.putalpha(tile_mask)

  # Shadow.
  shadow = _soft_shadow(tile_mask, offset=(0, int(round(size * 0.02))), blur=int(round(size * 0.04)), color=(20, 25, 35), alpha=60)
  bg.alpha_composite(shadow, (pad, pad))
  bg.alpha_composite(tile, (pad, pad))

  # Subtle highlight to make it feel less flat.
  highlight = Image.new("RGBA", (tile_size, tile_size), (255, 255, 255, 0))
  hd = ImageDraw.Draw(highlight)
  hd.ellipse(
    (int(tile_size * -0.15), int(tile_size * -0.20), int(tile_size * 0.75), int(tile_size * 0.70)),
    fill=(255, 255, 255, 45),
  )
  highlight.putalpha(tile_mask)
  bg.alpha_composite(highlight, (pad, pad))

  # Monogram.
  glyph_box = (pad, pad, pad + tile_size, pad + tile_size)
  gd = ImageDraw.Draw(bg)
  _draw_monogram(gd, glyph_box, "IV", size=int(round(tile_size * 0.46)))

  return bg


def write_png(path: Path, img: Image.Image) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  img.save(path, format="PNG", optimize=True)


def write_ico(path: Path, img: Image.Image) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  base = img.convert("RGBA")
  sizes = [(16, 16), (32, 32), (48, 48)]
  frames = [base.resize(sz, Image.Resampling.LANCZOS) for sz in sizes]
  frames[0].save(path, format="ICO", sizes=sizes)


def main() -> None:
  repo_root = Path(__file__).resolve().parents[1]
  public_dir = repo_root / "frontend" / "public"
  icons_dir = public_dir / "icons"

  # PWA icons (any)
  write_png(icons_dir / "icon-192.png", make_icon(192, maskable=False))
  write_png(icons_dir / "icon-512.png", make_icon(512, maskable=False))

  # PWA icons (maskable)
  write_png(icons_dir / "icon-maskable-192.png", make_icon(192, maskable=True))
  write_png(icons_dir / "icon-maskable-512.png", make_icon(512, maskable=True))

  # Browser assets
  write_png(public_dir / "apple-touch-icon.png", make_icon(180, maskable=False))
  write_ico(public_dir / "favicon.ico", make_icon(256, maskable=False))


if __name__ == "__main__":
  main()
