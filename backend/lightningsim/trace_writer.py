
from contextlib import nullcontext
from pathlib import Path
from tempfile import mkdtemp
from .trace_file import ResolvedTrace


def write_trace(trace: ResolvedTrace):
    n_context: nullcontext[str] = nullcontext(mkdtemp(prefix="lightningsim."))
    output_dir = Path(n_context)
    trace_path = output_dir / "trace"
    with open(trace_path, "r+") as f:
        f.seek(0)
        f.write(f"{trace.byte_count}\n{trace.line_count}")
        f.truncate

