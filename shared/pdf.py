import fitz

from pathlib import Path
from typing import Callable, Generator
from PIL import Image
from fpdf import FPDF
from .utils import sanitize_filename


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

def extract_from_pdf(
      pdf_path: Path,
      output_path: Path,
      progress: Callable[[float], None],
    ) -> tuple[str | None, str | None]:

  title: str | None = None
  author: str | None = None

  with fitz.open(pdf_path) as doc:
    image_prefix = sanitize_filename(pdf_path.stem)
    max_digits = len(str(doc.page_count))
    metadata = doc.metadata

    if metadata is not None:
      title = metadata.get("title", "No Title Found")
      author = metadata.get("author", "No Author Found")
      if title is not None:
        image_prefix = title

    for index, (image, format) in enumerate(_extract_images_from_pdf(doc, progress)):
      image_name = str(index + 1).zfill(max_digits)
      image_name = f"{image_prefix}-{image_name}.{format}"
      image_path = output_path / image_name
      with open(image_path, "wb") as file:
        file.write(image)

  return title, author

def _extract_images_from_pdf(doc: fitz.Document, progress: Callable[[float], None]) -> Generator[tuple[bytes, str], None, None]:
  for index in range(doc.page_count):
    page = doc.load_page(index)
    for img_info in page.get_images():
      xref = img_info[0]
      image_dict = doc.extract_image(xref)
      image: bytes = image_dict["image"]
      format: str = image_dict['ext']
      yield image, format
    progress(float(index) / doc.page_count)
