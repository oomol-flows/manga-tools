from curses import raw
from pathlib import Path
from oocana import Context
from typing import cast, Literal
from shutil import rmtree

from shared.archive import archive_with_zip
from shared.pdf import generate_pdf
from shared.epub import generate_epub
from shared.utils import sanitize_filename


#region generated meta
import typing
class Inputs(typing.TypedDict):
  images: list[str]
  format: typing.Literal["cbz", "epub", "pdf"] | None
  pack_path: str | None
  title: str | None
  author: str | None
  reading_order: typing.Literal["to-right", "to-left"]
class Outputs(typing.TypedDict):
  pack_path: str
#endregion

_Suffix = Literal[".cbz", ".epub", ".pdf"]
_SUFFIX_TUPPLE: tuple[_Suffix, ...] = (".cbz", ".epub", ".pdf")

def main(params: Inputs, context: Context) -> Outputs:
  format = params["format"]
  pack_path = params["pack_path"]
  suffix: _Suffix = ".cbz"

  if format is not None:
    suffix = cast(_Suffix, f".{format}")

  title = _normalize_str(params["title"])
  author = _normalize_str(params["author"])

  if pack_path is None:
    workspace_path = Path(context.session_dir) / "manga-tools"
    pack_path = workspace_path / f"{context.job_id}{suffix}"
    pack_path.parent.mkdir(parents=True, exist_ok=True)

  else:
    pack_path = Path(pack_path)
    pack_suffix = pack_path.suffix.lower()
    if title is None:
      title = sanitize_filename(pack_path.stem)
    if pack_suffix in _SUFFIX_TUPPLE:
      suffix = cast(_Suffix, pack_suffix)
    else:
      pack_path = pack_path.with_suffix(suffix)

  raw_paths: list[Path] = []
  for path in params["images"]:
    path = Path(path)
    if not path.exists():
      raise ValueError(f"Image path {path} does not exist")
    if not path.is_file():
      raise ValueError(f"Image path {path} is not a file")
    raw_paths.append(path)

  pack_path= _clean_path(pack_path)

  if suffix == ".cbz":
    archive_with_zip(
      title=title,
      raw_files=raw_paths,
      output_path=pack_path,
      progress=lambda p: context.report_progress(
        progress=100*float(p)/len(raw_paths),
      ),
    )
  elif suffix == ".pdf":
    generate_pdf(
      title=title,
      dpi=96,
      raw_files=raw_paths,
      output_path=pack_path,
      progress=lambda p: context.report_progress(
        progress=100*float(p)/len(raw_paths),
      ),
    )
  elif suffix == ".epub":
    temp_path = Path(context.tmp_pkg_dir) / context.job_id
    temp_path = _clean_path(temp_path)
    temp_path.mkdir(parents=True, exist_ok=True)
    generate_epub(
      title=title,
      author=author,
      image_paths=raw_paths,
      output_path=pack_path,
      temp_path=temp_path,
      read_to_left=(params["reading_order"] == "to-left"),
      progress=lambda p: context.report_progress(100.0*p),
    )
  return { "pack_path": str(pack_path) }

def _normalize_str(param: str | None) -> str | None:
  if param is None:
    return None
  param = param.strip()
  if not param:
    return None
  return param

def _clean_path(path: Path) -> Path:
  if path.exists():
    if path.is_file():
      path.unlink()
    else:
      rmtree(path)
  return path