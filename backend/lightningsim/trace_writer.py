from pathlib import Path
import os
from .trace_file import ResolvedTrace


def write_trace(trace: ResolvedTrace):
    cwd = os.getcwd()
    print(f"cwd: {cwd}")
    output_dir = Path(cwd)
    trace_path = output_dir / "trace"
    print(f"trace path: {trace_path}")

    if os.path.exists(trace_path):
        print(f"Output path '{trace_path}' exists. Removing...")
        os.remove(trace_path)
    else:
        print(f"Output path '{trace_path}' does not exist. Nothing to remove.")

    print(f"Writing new trace to output path '{trace_path}'.")
    with open(trace_path, "w+") as f:
        f.write(f"{trace.byte_count}\n{trace.line_count}")

