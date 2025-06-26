from pathlib import Path
from typing import Callable
from fpdf import FPDF
from PIL import Image


def generate_pdf(
    title: str | None,
    dpi: int,
    raw_files: list[Path],
    output_path: Path,
    progress: Callable[[int], None],
  ) -> None:

  points = 72 # inch = 72 points
  pdf = FPDF()
  if title is not None:
    pdf.set_title(title)

  for index, raw_file in enumerate(raw_files):
    with Image.open(raw_file) as image:
      width_pt = image.width / dpi * points
      height_pt = image.height / dpi * points
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