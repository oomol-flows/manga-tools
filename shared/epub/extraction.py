from typing import Callable, Generator
from pathlib import Path
from xml.etree.ElementTree import Element

from .xml import XMLReader
from .utils import iter_ids, find_element
from ..utils import image_name


def extract_from_epub(
      epub_path: Path,
      output_path: Path,
      progress: Callable[[float], None],
    ) -> tuple[str | None, str | None]:

  with XMLReader(epub_path) as reader:
    rootfile_path = _read_rootfile_path(reader)
    rootfile_xml = reader.read_xml(rootfile_path)
    image_files: list[Path] = []

    for page_file in _search_page_files(rootfile_xml, rootfile_path):
      page_xml: Element = reader.read_xml(page_file)
      image_files.extend(_search_image_files_in_page(page_xml, page_file))

    title, author = _find_title_and_author(rootfile_xml)
    cover_file = _find_cover_image_file(rootfile_xml)

    if cover_file is not None:
      if cover_file in image_files:
        image_files.remove(cover_file)
      image_files.insert(0, cover_file)

    image_prefix: str = epub_path.stem
    for i, id in enumerate(iter_ids(image_files)):
      image_file = image_files[i]
      name = image_name(id, image_prefix, image_file)
      reader.extract(image_file, output_path / name)
      progress(float(i + 1) / len(image_files))

    return title, author

def _read_rootfile_path(reader: XMLReader) -> Path:
  container_xml = reader.read_xml(Path("META-INF", "container.xml"))
  rootfile_xml = find_element(container_xml, "rootfiles", "rootfile")
  rootfile_path = rootfile_xml.get("full-path")
  assert rootfile_path is not None, "cannot find full-path"
  return Path(rootfile_path)

def _search_page_files(rootfile_xml: Element, rootfile_path: Path) -> Generator[Path, None, None]:
  # TODO: 目前不考虑 ncx，它在 2.0 和 3.0 下标准不一致，我不想搞得太麻烦
  #       为了得到更准确的图片顺序，我本该从目录中读取，以确定正确的顺序
  #       以后再说吧
  for item_xml in find_element(rootfile_xml, "manifest"):
    if item_xml.get("media-type") not in ("text/html", "application/xhtml+xml"):
      continue
    href = item_xml.get("href")
    if href is None:
      continue
    yield _resolve_path(
      base_file_path=rootfile_path,
      relative_path=Path(href),
    )

def _search_image_files_in_page(page_xml: Element, page_file: Path):
  for img_xml in _search_img_tags(page_xml):
    src = img_xml.get("src")
    if src is not None:
      yield _resolve_path(
        base_file_path=page_file,
        relative_path=Path(src),
      )

def _find_title_and_author(rootfile_xml: Element) -> tuple[str | None, str | None]:
  title: str | None = None
  author: str | None = None
  for child in find_element(rootfile_xml, "metadata"):
    if child.tag == "dc:title":
      title = child.text
    elif child.tag == "dc:creator":
      author = child.text
  return title, author

def _find_cover_image_file(rootfile_xml: Element) -> Path | None:
  cover_id: str | None = None
  for child in find_element(rootfile_xml, "metadata"):
    if child.tag == "meta" and child.get("name") == "cover":
      cover_id = child.get("content")
      break
  if cover_id is None:
    return None

  cover_href: str | None = None
  for child in find_element(rootfile_xml, "manifest"):
    if child.tag == "item" and child.get("id") == cover_id:
      cover_href = child.get("href")
  if cover_href is None:
    return None

  return Path(cover_href)

def _search_img_tags(element: Element):
  for child in element:
    if child.tag == "img":
      yield child
    yield from _search_img_tags(child)

def _resolve_path(base_file_path: Path, relative_path: Path) -> Path:
  relative_parts = relative_path.parts
  if len(relative_parts) == 0:
    return base_file_path
  if relative_parts[0] not in (".", ".."):
    return relative_path

  base_stack = list(base_file_path.parent.parts)
  for part in relative_parts:
    if part == ".":
      pass
    elif part == "..":
      if not base_stack:
        raise ValueError(f"invalid path {relative_path} (base on {base_file_path})")
      base_stack.pop()
    else:
      base_stack.append(part)

  return Path(*base_stack)