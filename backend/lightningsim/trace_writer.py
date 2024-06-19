
from contextlib import nullcontext
from pathlib import Path
from tempfile import mkdtemp
from .trace_file import ResolvedTrace


def write_trace(trace: ResolvedTrace):
    n_context = nullcontext(mkdtemp(prefix="lightningsim."))
    print(f"n_context: {n_context}")
    output_dir = Path(str(n_context))
    trace_path = output_dir / "trace"
    with open(trace_path, "r+") as f:
        f.seek(0)
        f.write(f"{trace.byte_count}\n{trace.line_count}")
        f.truncate

