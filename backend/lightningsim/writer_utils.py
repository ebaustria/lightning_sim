import os
from pathlib import Path

def resolve_trace_path(subdir: str, base_name: str) -> Path:
    file_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"file_dir: {file_dir}")
    return Path(file_dir) / subdir / base_name
