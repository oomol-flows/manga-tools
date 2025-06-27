from pathlib import Path
from oocana import Context


#region generated meta
import typing
class Inputs(typing.TypedDict):
  input_path: str
class Outputs(typing.TypedDict):
  images: list[str]
#endregion

_ENABLE_EXTS = (
  ".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi",
  ".png",
  ".gif",
  ".webp",
  ".bmp",
  ".tiff", ".tif",
  ".avif",
)

def main(params: Inputs, context: Context) -> Outputs:
  input_path = Path(params["input_path"])
  if not input_path.exists():
    raise ValueError(f"Archive path {input_path} does not exist")
  if not input_path.is_dir():
    raise ValueError(f"Archive path {input_path} is not a directory")

  image_names: list[str] = []
  for file in input_path.iterdir():
    if file.name.startswith("."):
      continue
    if file.suffix not in _ENABLE_EXTS:
      continue
    image_names.append(file.name)

  images = [
    str(input_path / name) for name in image_names
  ]
  return { "images": images }
