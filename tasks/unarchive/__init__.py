from pathlib import Path
from typing import Literal
from oocana import Context
from shutil import rmtree

from shared.archive import unarchive_with_zip
from shared.pdf import extract_from_pdf
from shared.epub import extract_from_epub

#region generated meta
import typing
class Inputs(typing.TypedDict):
  archive_path: str
  output_path: str | None
  clean_output_path: bool
class Outputs(typing.TypedDict):
  output_path: str
  format: typing.Literal["cbz", "epub", "pdf"]
  title: str | None
  author: str | None
  reading_order: typing.Literal["to-right", "to-left"]
#endregion


def main(params: Inputs, context: Context) -> Outputs:
  clean_output_path = params["clean_output_path"]
  output_path = params["output_path"]

  if output_path is None:
    output_path = Path(context.session_dir) / "manga-tools" / context.job_id
  else:
    output_path = Path(output_path)

  if not output_path.exists():
    output_path.mkdir(parents=True, exist_ok=True)
  elif output_path.is_dir() and clean_output_path:
    rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
  elif output_path.is_file():
    if clean_output_path:
      output_path.unlink()
    else:
      raise ValueError("output_path is a file")

  archive_path = Path(params["archive_path"])
  archive_suffix = archive_path.suffix
  format: Literal["cbz", "epub", "pdf"]
  title: str | None = None
  author: str | None = None
  reading_order: Literal["to-right", "to-left"] = "to-right"
  on_progress = lambda p: context.report_progress(p * 100.0)

  if archive_suffix == ".cbz":
    format = "cbz"
    unarchive_with_zip(
      input_path=archive_path,
      output_path=output_path,
      progress=on_progress,
    )
  elif archive_suffix == ".epub":
    format = "epub"
    title, author = extract_from_epub(
      epub_path=archive_path,
      output_path=output_path,
      progress=on_progress,
    )
  elif archive_suffix == ".pdf":
    format = "pdf"
    title, author = extract_from_pdf(
      pdf_path=archive_path,
      output_path=output_path,
      progress=on_progress,
    )
  else:
    raise ValueError(f"archive_path {archive_path} is not a supported archive format (only cbz, pdf, epub are supported)")

  return {
    "output_path": str(output_path),
    "format": format,
    "title": title,
    "author": author,
    "reading_order": reading_order,
  }
