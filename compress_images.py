from pathlib import Path
import os
import subprocess
import tempfile

IMAGE_DIR = Path("images")
MAX_DIMENSION = 800
JPEG_QUALITY = 70
IMAGE_EXTENSIONS = {".jpg", ".jpeg"}


def compress_image(image_path: Path) -> tuple[int, int]:
  """Compress one image and return its original and final byte sizes."""
  original_size = image_path.stat().st_size
  file_descriptor, temporary_name = tempfile.mkstemp(
      suffix=".jpg", dir=image_path.parent
  )
  os.close(file_descriptor)
  temporary_path = Path(temporary_name)
  temporary_path.unlink()

  try:
    subprocess.run(
        [
            "sips",
            "-Z",
            str(MAX_DIMENSION),
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(JPEG_QUALITY),
            "--out",
            str(temporary_path),
            str(image_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    compressed_size = temporary_path.stat().st_size

    if compressed_size < original_size:
      os.replace(temporary_path, image_path)
      return original_size, compressed_size

    return original_size, original_size
  except subprocess.CalledProcessError as error:
    details = error.stderr.strip() or "unknown sips error"
    raise RuntimeError(f"Could not compress {image_path}: {details}") from error
  finally:
    temporary_path.unlink(missing_ok=True)


def image_files():
  return sorted(
      path
      for path in IMAGE_DIR.iterdir()
      if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
  )


def main():
  files = image_files()
  if not files:
    print(f"No JPEG images found in {IMAGE_DIR}/")
    return

  total_before = 0
  total_after = 0
  compressed_count = 0

  for image_path in files:
    try:
      before, after = compress_image(image_path)
      total_before += before
      total_after += after
      if after < before:
        compressed_count += 1
      print(f"{image_path}: {before:,} -> {after:,} bytes")
    except (OSError, RuntimeError) as error:
      print(f"Failed: {error}")

  saved = total_before - total_after
  print(
      f"\nCompressed {compressed_count}/{len(files)} images; "
      f"saved {saved:,} bytes ({saved / total_before:.1%})."
  )


if __name__ == "__main__":
  main()
