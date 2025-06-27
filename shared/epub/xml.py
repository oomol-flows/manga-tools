import re

from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from xml.etree.ElementTree import fromstring, tostring, Element

from .namespace import norm_namespace
from .utils import iter_files
from ..utils import extract_to


class XMLReader:
  def __init__(self, input_path: Path) -> None:
    self._zip: ZipFile = ZipFile(input_path, "r", ZIP_STORED)

  def read_xml(self, file: Path) -> Element:
    with self._zip.open(file.as_posix()) as f:
      file_content = f.read().decode("utf-8")
      _, element = _parse_xml_file_content(file_content)
      return element

  def extract(self, file: Path, output_path: Path) -> None:
    with self._zip.open(file.as_posix()) as source:
      extract_to(source, output_path)

  def __enter__(self) -> "XMLReader":
    return self

  def __exit__(self, type, value, traceback) -> None:
    self._zip.close()

_MINETYPE_NAME = "mimetype"
_TEMPLATE_EXT = ".template"

class XMLWriter:
  def __init__(self, output_path: Path) -> None:
    self._zip: ZipFile = ZipFile(output_path, "w", ZIP_STORED)
    self._epub_path: Path = Path(__file__).parent.parent.parent / "epub"
    mimetype_path = self._epub_path / _MINETYPE_NAME

    # minetype must be the first file (for EPUB)
    self._zip.write(mimetype_path, _MINETYPE_NAME)
    for file in iter_files(self._epub_path):
      if file.name == _MINETYPE_NAME:
        continue
      suffixes = file.suffixes
      if len(suffixes) == 2 and suffixes[0] == _TEMPLATE_EXT:
        continue
      self._zip.write(
        filename=self._epub_path / file,
        arcname=str(file.as_posix()),
      )

  def template(self, file: Path) -> tuple[str, Element]:
    template_name = file.with_suffix(_TEMPLATE_EXT + file.suffix)
    template_path = self._epub_path / template_name
    with open(template_path, "r", encoding="utf-8") as f:
      return _parse_xml_file_content(f.read())

  def write(self, file: Path, input_path: Path) -> None:
    self._zip.write(
      filename=input_path,
      arcname=file.as_posix(),
    )

  def write_xml(self, file: Path, header: str, element: Element) -> None:
    content = tostring(element, encoding="unicode")
    content = "\n".join((header, content))
    self._zip.writestr(
      zinfo_or_arcname=file.as_posix(),
      data=content.encode("utf-8"),
    )

  def __enter__(self) -> "XMLWriter":
    return self

  def __exit__(self, type, value, traceback) -> None:
    self._zip.close()

_HEADER_PATTERN = re.compile(r"(<\?.*?\?>)|(<\!.*?>)", flags=re.DOTALL)

def _parse_xml_file_content(file_content: str) -> tuple[str, Element]:
  parts = [
    part for part in _HEADER_PATTERN.split(file_content, maxsplit=2)
    if part and not part.isspace()
  ]
  element = fromstring(parts.pop())
  element = norm_namespace(element)
  header = "\n".join(parts)
  return header, element