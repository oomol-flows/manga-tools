import fitz

from pathlib import Path
from typing import Callable, Generator
from PIL import Image
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
    with Image.open(raw_file) as image:
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
      output_path: Path,
      progress: Callable[[float], None],
    ) -> None:

  with fitz.open(pdf_path) as doc:
    max_digits = len(str(doc.page_count))
    for index, (image, format) in enumerate(_extract_images_from_pdf(doc, progress)):
      image_name = str(index + 1).zfill(max_digits)
      image_name = f"{image_name}.{format}"
      if title is not None:
        image_name = f"{title}-{image_name}"
      image_path = output_path / image_name
      with open(image_path, "wb") as file:
        file.write(image)

def _extract_images_from_pdf(doc: fitz.Document, progress: Callable[[float], None]) -> Generator[tuple[bytes, str], None, None]:
  for index in range(doc.page_count):
    page = doc.load_page(index)
    for img_info in page.get_images():
      xref = img_info[0]
      image_dict = doc.extract_image(xref)
      image: bytes = image_dict["image"]
      format: str = image_dict['ext']
      yield image, format
    progress(float(index + 1) / doc.page_count)
