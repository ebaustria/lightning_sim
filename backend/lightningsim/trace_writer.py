from pathlib import Path
import os
import json
from .trace_file import AXIInterface, ResolvedStream, ResolvedTrace

def axi_json_obj(axi_interface: AXIInterface) -> dict:
    return { "name": axi_interface.name, "address": axi_interface.address }


def fifo_json_obj(resolved_stream: ResolvedStream) -> dict:
    return {
        "display_name": resolved_stream.get_display_name(),
        "id": resolved_stream.id,
        "name": resolved_stream.name,
        "width": resolved_stream.width
    }


def resolve_trace_path(base_name: str) -> Path:
    file_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"file_dir: {file_dir}")
    return Path(file_dir) / "trace" / base_name


def write_resolved_trace(trace: ResolvedTrace):
    trace_path = resolve_trace_path("resolved_trace.json")
    print(f"trace path: {trace_path}")

    params = trace.params

    json_data = {
        "byte_count": trace.byte_count,
        "line_count": trace.line_count,
        "axi_interfaces": [axi_json_obj(axi_itf) for axi_itf in trace.axi_interfaces],
        "fifos": [fifo_json_obj(fifo) for fifo in trace.fifos],
        "params": {
            "ap_ctrl_chain_top_port_count": params.ap_ctrl_chain_top_port_count,
            "fifo_depths": params.fifo_depths,
            "axi_delays": params.axi_delays
        }
    }

    if os.path.exists(trace_path):
        print(f"Output path '{trace_path}' exists. Removing...")
        os.remove(trace_path)
    else:
        print(f"Output path '{trace_path}' does not exist. Nothing to remove.")

    print(f"Writing new trace to output path '{trace_path}'.")
    with open(trace_path, "w+", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

