from typing import Any, Generator
from pathlib import Path
from xml.etree.ElementTree import Element


def clone_element(element: Element) -> Element:
  new_element = Element(element.tag)
  for attr_name, attr_value in element.items():
    new_element.set(attr_name, attr_value)
  new_element.text = element.text
  for child in element:
    new_child = clone_element(child)
    new_element.append(new_child)
    new_child.tail = child.tail
  return new_element

def find_element(root_xml: Element, *tags: str) -> Element:
  element: Element | None = root_xml
  for tag in tags:
    element = element.find(tag)
    if element is None:
      raise ValueError(f"cannot find tag: {tag}")
  return element

def iter_ids(image_paths: list[Any]) -> Generator[str, None, None]:
  max_digits = len(str(len(image_paths)))
  for index, _ in enumerate(image_paths):
    yield str(index + 1).zfill(max_digits)

def iter_files(target_path: Path, relative_path: Path | None = None) -> Generator[Path, None, None]:
  for sub_path in target_path.iterdir():
    sub_name = sub_path.name
    if sub_name.startswith("."):
      continue

    sub_relative_path = relative_path
    if sub_relative_path is None:
      sub_relative_path = Path(sub_name)
    else:
      sub_relative_path = sub_relative_path / sub_name

    if sub_path.is_file():
      yield sub_relative_path
    elif sub_path.is_dir():
      yield from iter_files(
        target_path=sub_path,
        relative_path=sub_relative_path,
      )