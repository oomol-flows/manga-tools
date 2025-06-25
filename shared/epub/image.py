from pathlib import Path
from typing import Iterable, Literal
from PIL import Image


ImageFormat = Literal["GIF", "JPEG", "PNG"]

# EPub only supports gif, jpeg, png
# https://idpf.org/epub/20/spec/OPS_2.0.1_draft.htm#Section1.3.7
# https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html
_EPUB_SUPPORTED_IMAGE_FORMATS = (
  "GIF", "JPEG", "PNG"
)

def preprocess_images(image_paths: list[Path], temp_path: Path) -> tuple[list[tuple[Path, ImageFormat]], int, int]:
  target_infos: list[tuple[Path, ImageFormat]] = []
  image_sizes: list[tuple[int, int]] = []

  for image_path in image_paths:
    with Image.open(image_path) as image:
      if image.format is None:
        continue

      format: ImageFormat = "PNG"
      if image.format in _EPUB_SUPPORTED_IMAGE_FORMATS:
        format = image.format
      else:
        image_path = image_path.with_suffix(".png")
        image_path = temp_path / image_path.name
        image.save(image_path)

      target_infos.append((image_path, format))
      image_sizes.append((image.width, image.height))

  if not target_infos:
    return target_infos, 0, 0

  width = round(_find_median(float(width) for width, _ in image_sizes))
  height = round(_find_median(float(height) for _, height in image_sizes))

  return target_infos, width, height

def _find_median(numbers: Iterable[float]) -> float:
  sorted_numbers = sorted(numbers)
  n = len(sorted_numbers)
  mid = n // 2

  if n % 2 == 1:
    return sorted_numbers[mid]
  else:
    return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2