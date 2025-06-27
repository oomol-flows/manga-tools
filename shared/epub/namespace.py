import re

from dataclasses import dataclass
from typing import Generator
from xml.etree.ElementTree import Element


def norm_namespace(root_xml: Element) -> Element:
  ins = _NamespaceNormalization()
  ins.extract_and_mark_namespaces(root_xml)
  ins.migrate_namespaces()
  return root_xml

_ID = tuple[int, ...]
_DEFAULT_KEY = "default"
_NS_PATTERN = re.compile(r"^{(.+)}")
_NS_ACRONYM = {
  "http://www.idpf.org/2007/opf": _DEFAULT_KEY,
  "http://www.daisy.org/z3986/2005/ncx/": _DEFAULT_KEY,
  "http://www.w3.org/1999/xhtml": _DEFAULT_KEY,
  "http://purl.org/dc/elements/1.1/": "dc",
}

@dataclass
class _ElementNode:
  id: _ID
  parent_id: _ID | None
  raw: Element
  tag: str
  namespace: str | None

class _NamespaceNormalization:
  def __init__(self) -> None:
    self._nodes: dict[_ID, _ElementNode] = {}
    self._ns2ids: dict[str, list[_ID]] = {}

  def extract_and_mark_namespaces(self, root_xml: Element):
    for id, parent_id, element in self._search_elements(root_xml):
      tag, namespace = self._split_tag_and_namespace(element.tag)
      self._nodes[id] = _ElementNode(
        id=id,
        parent_id=parent_id,
        raw=element,
        tag=tag,
        namespace=namespace,
      )
      if namespace is not None:
        element_ids = self._ns2ids.get(namespace, None)
        if not element_ids:
          element_ids = []
          self._ns2ids[namespace] = element_ids
        element_ids.append(id)

  def _search_elements(
        self,
        element: Element,
        id: _ID = (0,),
        parent_id: _ID | None = None,
      ) -> Generator[tuple[_ID, _ID | None, Element], None, None]:

    yield id, parent_id, element
    for index, child in enumerate(element):
      child_id = id + (index,)
      yield child_id, id, child
      yield from self._search_elements(child, child_id, id)

  def _split_tag_and_namespace(self, raw_tag: str) -> tuple[str, str | None]:
    matches = _NS_PATTERN.match(raw_tag)
    if not matches:
      return raw_tag, None
    namespace = matches.group(1)
    tag = _NS_PATTERN.sub("", raw_tag)
    return tag, namespace

  def migrate_namespaces(self) -> None:
    for namespace, element_ids in self._ns2ids.items():
      ns = _NS_ACRONYM.get(namespace, None)
      if ns is not None:
        parent_id = self._find_nearest_common_parent_id(element_ids)
        parent_element = self._nodes[parent_id].raw
        xmlns_key = "xmlns"
        if ns != _DEFAULT_KEY:
          xmlns_key += f":{ns}"
        parent_element.set(xmlns_key, namespace)

      for id in element_ids:
        node = self._nodes[id]
        tag = node.tag
        if ns is not None and ns != _DEFAULT_KEY:
          tag: str = f"{ns}:{tag}"
        node.raw.tag = tag

  def _find_nearest_common_parent_id(self, check_ids: list[_ID]) -> _ID:
    collection: dict[int, set[_ID]] = {}
    for id in check_ids:
      deep = len(id) - 1
      ids = collection.get(deep, None)
      if ids is None:
        ids = set()
        collection[deep] = ids
      ids.add(id)

    while True:
      max_deep = max(collection.keys())
      if max_deep <= 0:
        break

      previous_ids = collection.get(max_deep - 1, None)
      if previous_ids is None:
        previous_ids = set()
        collection[max_deep - 1] = previous_ids

      for id in collection.pop(max_deep):
        parent_id = self._nodes[id].parent_id
        assert parent_id is not None, f"node id={id} don't have parent"
        previous_ids.add(parent_id)

      if len(collection.keys()) == 1 and \
         len(next(iter(collection.values()))) == 1:
        break

    for ids in collection.values():
      for id in ids:
        return id
    raise RuntimeError("invalid breanch")