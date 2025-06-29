import re

from typing import IO
from os import PathLike
from pathlib import Path


_CHUNK_SIZE = 16384

def extract_to(source: IO[bytes], target_path: PathLike) -> None:
  with open(target_path, "wb") as dst:
    while True:
      chunk = source.read(_CHUNK_SIZE)
      if chunk:
        dst.write(chunk)
      else:
        break

def image_name(id: str, prefix: str | None, raw_path: Path) -> str:
  file_name = id
  if prefix is not None:
    file_name: str = f"{prefix}-{file_name}"
  suffix = "".join(raw_path.suffixes)
  return f"{file_name}{suffix}"

_ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/:*?"<>|\r\n\t\x00-\x1F]')
_MULTIPLE_WHITESPACE_PATTERN = re.compile(r"\s+")

def sanitize_filename(filename: str) -> str:
  sanitized = _ILLEGAL_CHARS_PATTERN.sub("_", filename)
  sanitized = _MULTIPLE_WHITESPACE_PATTERN.sub(" ", sanitized)
  return sanitized.strip()