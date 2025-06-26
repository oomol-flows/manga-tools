from typing import Any, Generator, Callable
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED


def archive_with_zip(
    title: str | None,
    raw_files: list[Path],
    output_path: Path,
    progress: Callable[[int], None],
  ) -> None:

  with ZipFile(output_path, "w", ZIP_STORED) as zip:
    for i, (file_name, raw_path) in enumerate(_iter_files(title, raw_files)):
      zip.write(raw_path, file_name)
      progress(i + 1)

def _iter_files(title: str | None, raw_files: list[Path]) -> Generator[tuple[str, Path], Any, None]:
  max_digits = len(str(len(raw_files)))
  for index, raw_path in enumerate(raw_files):
    file_name = str(index + 1).zfill(max_digits)
    if title is not None:
      file_name: str = f"{title}-{file_name}"
    suffix = "".join(raw_path.suffixes)
    file_name = f"{file_name}{suffix}"
    yield file_name, raw_path

def unarchive_with_zip(
      input_path: Path,
      output_path: Path,
      progress: Callable[[float], None],
    ) -> None:

  with ZipFile(input_path, "r") as zip:
    file_paths = _read_files_of_root(zip)
    for i, file_path in enumerate(file_paths):
      target_path = output_path / file_path.name
      with zip.open(str(file_path)) as src:
        with open(target_path, "wb") as dst:
          while True:
            chunk = src.read(16384)
            if chunk:
              dst.write(chunk)
            else:
              break
      progress(float(i + 1) / len(file_paths))

def _read_files_of_root(zip: ZipFile) -> list[Path]:
  root_name: str | None = None
  for info in zip.infolist():
    if info.is_dir():
      parts = Path(info.filename).parts
      if len(parts) == 1:
        root_name = parts[0]
        break

  file_paths: list[Path] = []
  for info in zip.infolist():
    if info.is_dir():
      continue
    file_path = Path(info.filename)
    file_parts = file_path.parts
    if root_name is None:
      if len(file_parts) == 1:
        file_paths.append(file_path)
    elif len(file_parts) == 2:
      parent_name, _ = file_parts
      if parent_name == root_name:
        file_paths.append(file_path)

  return file_paths