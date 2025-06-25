import re

from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from xml.etree.ElementTree import fromstring, tostring, Element
from .utils import get_xmlns, extract_xmlns


_MINETYPE_NAME = "mimetype"
_TEMPLATE_EXT = ".template"
_HEADER_PATTERN = re.compile(r"(<\?.*?\?>)|(<\!.*?>)", flags=re.DOTALL)

class XMLWriter:
  def __init__(self, output_path: Path) -> None:
    self._zip: ZipFile = ZipFile(output_path, "w", ZIP_STORED)
    self._epub_path: Path = Path(__file__).parent.parent.parent / "epub"
    mimetype_path = self._epub_path / _MINETYPE_NAME

    # minetype must be the first file (for EPUB)
    self._zip.write(mimetype_path, _MINETYPE_NAME)
    for file in self._iter_files(self._epub_path):
      if file.name == _MINETYPE_NAME:
        continue
      suffixes = file.suffixes
      if len(suffixes) == 2 and suffixes[0] == _TEMPLATE_EXT:
        continue
      self._zip.write(
        filename=self._epub_path / file,
        arcname=str(file.as_posix()),
      )

  @property
  def zip(self) -> ZipFile:
    return self._zip

  def template(self, file: Path) -> tuple[str, str, Element]:
    template_name = file.with_suffix(_TEMPLATE_EXT + file.suffix)
    template_path = self._epub_path / template_name
    with open(template_path, "r", encoding="utf-8") as f:
      parts = [
        part for part in _HEADER_PATTERN.split(f.read(), maxsplit=2)
        if part and not part.isspace()
      ]
      element = fromstring(parts.pop())
      header = "\n".join(parts)
      xmlns = extract_xmlns(element)
      return header, xmlns, element

  def write(self, file: Path, header: str, xmlns: str, element: Element):
    target_path = self._epub_path / file
    self._set_xmlns(element, xmlns)
    element.set("xmlns", xmlns)
    with open(target_path, "w", encoding="utf-8") as f:
      f.write(header + "\n" + tostring(
        element,
        encoding="unicode",
      ))

  def __enter__(self) -> "XMLWriter":
    return self

  def __exit__(self, type, value, traceback) -> None:
    self._zip.close()

  def _iter_files(self, root_path: Path):
    for file in root_path.iterdir():
      if file.name.startswith("."):
        continue
      if file.is_file():
        yield file
      elif file.is_dir():
        for sub_file in self._iter_files(file):
          yield file / sub_file

  def _set_xmlns(self, element: Element, xmlns: str) -> None:
    element_xmlns, element_tag = get_xmlns(element)
    if xmlns != element_xmlns:
      element.tag = "{" + xmlns + "}" + element_tag
    for child in element:
      self._set_xmlns(child, xmlns)