from typing import TypeVar, Literal
from pathlib import Path


#region generated meta
import typing
class Inputs(typing.TypedDict):
  source_path: str
  title: str | None
  author: str | None
  reading_order: typing.Literal["to-right", "to-left"]
  input_title: str | None
  input_author: str | None
  input_reading_order: typing.Literal["to-right", "to-left"] | None
class Outputs(typing.TypedDict):
  title: str | None
  author: str | None
  reading_order: typing.Literal["to-right", "to-left"]
#endregion


def main(params: Inputs) -> Outputs:
  title = _merge(params["input_title"], params["title"])
  author = _merge(params["input_author"], params["author"])
  reading_order: Literal["to-right", "to-left"] = _merge(params["input_reading_order"], params["reading_order"])
  if title is None:
    source_path = Path(params["source_path"])
    title = source_path.stem

  return {
    "title": title,
    "author": author,
    "reading_order": reading_order,
  }

_T = TypeVar("_T")

def _merge(value1: _T | None, value2: _T) -> _T:
  if value1 is not None:
    return value1
  else:
    return value2