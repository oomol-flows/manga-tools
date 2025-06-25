from curses import raw
from pathlib import Path
from oocana import Context
from typing import cast, Literal
from shutil import rmtree

from shared.archive import archive_with_zip
from shared.pdf import generate_pdf


#region generated meta
import typing
class Inputs(typing.TypedDict):
  images: list[str]
  title: str | None
  format: typing.Literal["cbz", "epub", "pdf"] | None
  pack_path: str | None
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

  if pack_path is None:
    workspace_path = Path(context.session_dir) / "manga-tools"
    pack_path = workspace_path / f"{context.job_id}{suffix}"
    pack_path.parent.mkdir(parents=True, exist_ok=True)

  else:
    pack_path = Path(pack_path)
    pack_suffix = pack_path.suffix.lower()
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

  if pack_path.exists():
    rmtree(pack_path)
  title = (params["title"] or "").strip()

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
  else:
    raise ValueError(f"invalid suffix {suffix}")

  return { "pack_path": str(pack_path) }