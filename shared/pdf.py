import fitz

from pathlib import Path
from typing import cast, Any, Callable
from PIL.Image import open as open_image, frombytes
from fpdf import FPDF


_POINTS = 72 # inch = 72 points

def generate_pdf(
    title: str | None,
    dpi: int,
    raw_files: list[Path],
    output_path: Path,
    progress: Callable[[int], None],
  ) -> None:

  pdf = FPDF()
  if title is not None:
    pdf.set_title(title)

  for index, raw_file in enumerate(raw_files):
    with open_image(raw_file) as image:
      width_pt = image.width / dpi * _POINTS
      height_pt = image.height / dpi * _POINTS
      pdf.add_page(format=(width_pt, height_pt))
      pdf.image(
        name=raw_file,
        x=0,
        y=0,
        w=width_pt,
        h=height_pt
      )
      progress(index + 1)

  pdf.output(str(output_path))

_SAVED_EXT = "png"

def extract_from_pdf(
      title: str | None,
      pdf_path: Path,
      dpi: int,
      output_path: Path,
      progress: Callable[[float], None],
    ) -> None:

  with fitz.open(pdf_path) as pdf:
    for index in range(pdf.page_count):
      page = pdf.load_page(index)
      matrix = fitz.Matrix(dpi / _POINTS, dpi / _POINTS)
      pixmap = cast(Any, page).get_pixmap(matrix=matrix)
      image = frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

      max_digits = len(str(pdf.page_count))
      image_name = str(index + 1).zfill(max_digits)
      image_name = f"{image_name}.{_SAVED_EXT}"
      if title is not None:
        image_name = f"{title}-{image_name}"
      image_path = output_path / image_name
      image.save(image_path)

      progress(float(index + 1) / pdf.page_count)
