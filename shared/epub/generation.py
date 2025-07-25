from pathlib import Path
from uuid import uuid4
from typing import Callable
from datetime import datetime, timezone
from xml.etree.ElementTree import Element

from .xml import XMLWriter
from .image import preprocess_images, ImageFormat
from .utils import iter_ids, clone_element, find_element


def generate_epub(
      title: str | None,
      author: str | None,
      image_paths: list[Path],
      temp_path: Path,
      output_path: Path,
      read_to_left: bool,
      progress: Callable[[float], None],
    ) -> None:

  _EpubGeneration(title, author, read_to_left, progress).do(
    image_paths=image_paths,
    temp_path=temp_path,
    output_path=output_path,
  )

_STEP_MAIN_OPF = (0.0, 0.05)
_STEP_CONTENTS_NCX = (0.05, 0.1)
_STEP_IMAGES = (0.1, 0.9)
_STEP_PAGES = (0.9, 1.0)

class _EpubGeneration:
  def __init__(
        self,
        title: str | None,
        author: str | None,
        read_to_left: bool,
        progress: Callable[[float], None],
      ) -> None:

    self._title: str | None = title
    self._author: str | None = author
    self._read_to_left: bool = read_to_left
    self._progress: Callable[[float], None] = progress
    self._identifer: str = uuid4().hex
    self._step: tuple[float, float] = (0.0, 0.0)

  def do(self, image_paths: list[Path], temp_path: Path, output_path: Path) -> None:
    image_infos, width, height = preprocess_images(image_paths, temp_path)
    with XMLWriter(output_path) as writer:
      self._generate_main_opf(writer, image_infos, width, height)
      self._generate_contents_ncx(writer, image_infos)
      self._generate_images(writer, image_infos)
      self._generate_pages(writer, image_infos, width, height)

  def _generate_main_opf(
        self,
        writer: XMLWriter,
        image_infos: list[tuple[Path, ImageFormat]],
        width: int, height: int,
      ) -> None:

    self._update_step(_STEP_MAIN_OPF)
    opf_path = Path("main.opf")
    header, root_xml = writer.template(opf_path)
    manifest_xml = find_element(root_xml, "manifest")

    for id in iter_ids(image_infos):
      item_xml = Element("item", {
        "id": f"page_{id}",
        "href": f"content/pages/page-{id}.html",
        "media-type": "application/xhtml+xml",
      })
      manifest_xml.append(item_xml)

    is_first_image = True
    cover_id: str | None = None
    cover_href: str | None = None

    for id, (_, format) in zip(iter_ids(image_infos), image_infos):
      href = f"content/images/image-{id}.{format.lower()}"
      media_type: str
      if format == "GIF":
        media_type = "image/gif"
      elif format == "JPEG":
        media_type = "image/jpeg"
      elif format == "PNG":
        media_type = "image/png"
      else:
        continue
      item_xml = Element("item", {
        "id": f"image_{id}",
        "fallback": f"page_{id}",
        "href": href,
        "media-type": media_type,
      })
      if is_first_image:
        is_first_image = False
        item_xml.set("properties", "cover-image")
        cover_id = id
        cover_href = href
      manifest_xml.append(item_xml)

    spine_xml = find_element(root_xml, "spine")
    if self._read_to_left:
      spine_xml.set("page-progression-direction", "rtl")
    else:
      spine_xml.set("page-progression-direction", "ltr")

    for kind in ("page", "image"):
      for id in iter_ids(image_infos):
        spine_xml.append(Element("itemref", {
          "idref": f"{kind}_{id}",
        }))

    guide_xml = find_element(root_xml, "guide")
    reference_xml = find_element(guide_xml, "reference")

    if cover_href is None:
      guide_xml.remove(reference_xml)
    else:
      reference_xml.set("href", cover_href)

    metadata_xml = find_element(root_xml, "metadata")
    to_removes: list[Element] = []

    for child_xml in metadata_xml:
      if child_xml.tag == "meta":
        name = child_xml.get("name")
        if name == "original-resolution":
          child_xml.set("content", f"{width}x{height}")
        elif name == "primary-writing-mode":
          if self._read_to_left:
            child_xml.set("content", "horizontal-rl")
          else:
            child_xml.set("content", "horizontal-lr")
        elif name == "cover":
          if cover_id is None:
            to_removes.append(child_xml)
          else:
            child_xml.set("content", f"image_{cover_id}")
        elif child_xml.get("property") == "dcterms:modified":
          current_time = datetime.now(timezone.utc)
          child_xml.text = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

      elif child_xml.tag == "dc:title":
        if self._title:
          child_xml.text = self._title
        else:
          to_removes.append(child_xml)

      elif child_xml.tag == "dc:identifier":
        child_xml.text = self._identifer

      elif child_xml.tag == "dc:creator":
        if self._author:
          child_xml.text = self._author
        else:
          to_removes.append(child_xml)

    for to_remove in to_removes:
      metadata_xml.remove(to_remove)

    writer.write_xml(opf_path, header, root_xml)

  def _generate_contents_ncx(self, writer: XMLWriter, image_infos: list[tuple[Path, ImageFormat]]) -> None:
    self._update_step(_STEP_CONTENTS_NCX)

    ncx_path = Path("content", "contents.ncx")
    header, root_xml = writer.template(ncx_path)
    head_xml = find_element(root_xml, "head")

    for sub_xml in head_xml:
      if sub_xml.tag != "meta":
        continue
      name = sub_xml.get("name")
      if name == "dtb:uid":
        sub_xml.set("content", self._identifer)
      elif name == "dtb:totalPageCount":
        sub_xml.set("content", str(len(image_infos)))
      elif name == "dtb:maxPageNumber":
        sub_xml.set("content", str(len(image_infos)))

    doc_title_xml = find_element(root_xml, "docTitle")
    if self._title:
      doc_title_text_xml = find_element(doc_title_xml, "text")
      doc_title_text_xml.text = self._title
    else:
      root_xml.remove(doc_title_xml)

    nav_map_xml = find_element(root_xml, "navMap")
    for index, id in enumerate(iter_ids(image_infos)):
      nav_point_xml = Element("navPoint", {
        "class": "other",
        "id": f"page_{id}",
        "playOrder": str(index + 1),
      })
      nav_label_xml = Element("navLabel")
      nav_label_text_xml = Element("text")
      nav_label_text_xml.text = id
      nav_label_xml.append(nav_label_text_xml)
      nav_point_xml.append(nav_label_xml)
      content_xml = Element("content")
      content_xml.set("src", f"./pages/page-{id}.html")
      nav_point_xml.append(content_xml)
      nav_map_xml.append(nav_point_xml)

    writer.write_xml(ncx_path, header, root_xml)

  def _generate_images(self, writer: XMLWriter, image_infos: list[tuple[Path, ImageFormat]]) -> None:
    self._update_step(_STEP_IMAGES)
    for i, id in enumerate(iter_ids(image_infos)):
      image_path, format = image_infos[i]
      image_name = f"image-{id}.{format.lower()}"
      image_zip_file = Path("content") / "images" / image_name
      writer.write(image_zip_file, image_path)
      self._update_progress(i + 1, len(image_infos))

  def _generate_pages(
        self,
        writer: XMLWriter,
        image_infos: list[tuple[Path, ImageFormat]],
        width: int,
        height: int,
      ) -> None:

    self._update_step(_STEP_PAGES)
    page_path = Path("content", "pages", "page.html")
    header, template_xml = writer.template(page_path)

    for i, id in enumerate(iter_ids(image_infos)):
      _, format = image_infos[i]
      root_xml = clone_element(template_xml)
      head_xml = find_element(root_xml, "head")
      title_xml = find_element(head_xml, "title")

      if self._title:
        title_xml.text = f"{self._title} - {id}"
      else:
        title_xml.text = id

      for sub_xml in head_xml:
        if sub_xml.tag != "meta":
          continue
        if sub_xml.get("name") != "viewport":
          continue
        sub_xml.set("content", f"width={width}, height={height}")

      img_xml = find_element(root_xml, "body", "div", "div", "img")
      img_xml.set("src", f"../images/image-{id}.{format.lower()}")
      img_xml.set("alt", id)

      page_path = page_path.parent / f"page-{id}.html"
      writer.write_xml(page_path, header, root_xml)
      self._update_progress(i + 1, len(image_infos))

  def _update_step(self, step: tuple[float, float]) -> None:
    self._step = step
    self._progress(step[0])

  def _update_progress(self, progress: int, max_progress: int) -> None:
    begin, end = self._step
    p = float(progress) / float(max_progress)
    p =  begin + (end - begin) * p
    self._progress(p)
