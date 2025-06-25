from typing import Any, Generator, Callable
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def archive_with_zip(
    title: str,
    raw_files: list[Path],
    output_path: Path,
    progress: Callable[[int], None],
  ) -> None:

  with ZipFile(output_path, "w", ZIP_DEFLATED) as zip:
    for i, (file_name, raw_path) in enumerate(_iter_files(title, raw_files)):
      zip.write(raw_path, file_name)
      progress(i + 1)

def _iter_files(title: str, raw_files: list[Path]) -> Generator[tuple[str, Path], Any, None]:
  max_digits = len(str(len(raw_files)))
  for index, raw_path in enumerate(raw_files):
    file_name = str(index).zfill(max_digits)
    if title:
      file_name: str = f"{title}-{file_name}"
    suffix = "".join(raw_path.suffixes)
    file_name = f"{file_name}{suffix}"
    yield file_name, raw_path