from pathlib import Path
from uuid import uuid4
from xml.etree.ElementTree import Element

from .xml_writer import XMLWriter
from .image import preprocess_images, ImageFormat
from .utils import iter_ids, clone_element, find_element


def generate_epub(
      title: str,
      image_paths: list[Path],
      temp_path: Path,
      output_path: Path,
      read_to_left: bool,
    ) -> None:

  image_infos, width, height = preprocess_images(image_paths, temp_path)
  with XMLWriter(output_path) as writer:
    _write_main_opf(writer, title, image_infos, width, height, read_to_left)
    _write_contents_ncx(writer, title, image_infos)
    _write_images(writer, image_infos)
    _write_pages(writer, title, image_infos, width, height)

def _write_main_opf(
      writer: XMLWriter,
      title: str,
      image_infos: list[tuple[Path, ImageFormat]],
      width: int,
      height: int,
      read_to_left: bool,
    ) -> None:

  opf_path = Path("content", "main.opf")
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
  for id in iter_ids(image_infos):
    item_xml = Element("itemref", {
      "idref": f"page_{id}",
    })
    spine_xml.append(item_xml)

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
        if read_to_left:
          child_xml.set("content", "horizontal-lr")
        else:
          child_xml.set("content", "horizontal-rl")
      elif name == "cover":
        if cover_id is None:
          to_removes.append(child_xml)
        else:
          child_xml.set("content", f"image_{cover_id}")
    elif child_xml.tag == "dc:title":
      if title:
        child_xml.text = title
      else:
        to_removes.append(child_xml)

  for to_remove in to_removes:
    metadata_xml.remove(to_remove)

  writer.write(opf_path, header, root_xml)

def _write_contents_ncx(
      writer: XMLWriter,
      title: str,
      image_infos: list[tuple[Path, ImageFormat]],
    ) -> None:

  ncx_path = Path("content", "contents.ncx")
  header, root_xml = writer.template(ncx_path)
  head_xml = find_element(root_xml, "head")

  for sub_xml in head_xml:
    if sub_xml.tag != "meta":
      continue
    name = sub_xml.get("name")
    if name == "dtb:uid":
      sub_xml.set("content", uuid4().hex)
    elif name == "dtb:totalPageCount":
      sub_xml.set("content", str(len(image_infos)))
    elif name == "dtb:maxPageNumber":
      sub_xml.set("content", str(len(image_infos)))

  doc_title_xml = find_element(root_xml, "docTitle")
  if title:
    doc_title_text_xml = find_element(doc_title_xml, "text")
    doc_title_text_xml.text = title
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

  writer.write(ncx_path, header, root_xml)

def _write_images(writer: XMLWriter, image_infos: list[tuple[Path, ImageFormat]]) -> None:
  for id, (image_path, format) in zip(iter_ids(image_infos), image_infos):
    href = f"content/images/image-{id}.{format.lower()}"
    writer.zip.write(image_path, href)

def _write_pages(
      writer: XMLWriter,
      title: str,
      image_infos: list[tuple[Path, ImageFormat]],
      width: int,
      height: int,
    ) -> None:

  page_path = Path("content", "pages", "page.html")
  header, template_xml = writer.template(page_path)

  for id, (_, format) in zip(iter_ids(image_infos), image_infos):
    root_xml = clone_element(template_xml)
    head_xml = find_element(root_xml, "head")
    title_xml = find_element(head_xml, "title")

    if title:
      title_xml.text = f"{title} - {id}"
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

    page_path = page_path.parent / f"page_{id}.html"
    writer.write(page_path, header, root_xml)
