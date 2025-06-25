import re

from typing import Any, Generator
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

_NS_PATTERN = re.compile(r"^{(.+)}")

def extract_xmlns(element: Element, root_xmlns: str | None = None) -> str:
  matches = _NS_PATTERN.match(element.tag)
  if not matches:
    return ""

  xmlns = matches.group(1)
  if root_xmlns is None or root_xmlns == xmlns:
    element.tag = _NS_PATTERN.sub("", element.tag)
  if root_xmlns is None:
    root_xmlns = xmlns

  for child in element:
    extract_xmlns(child, root_xmlns)

  return xmlns

def get_xmlns(element: Element) -> tuple[str | None, str]:
  matches = _NS_PATTERN.match(element.tag)
  if matches:
    return matches.group(1), _NS_PATTERN.sub("", element.tag)
  else:
    return None, element.tag