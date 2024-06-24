from pathlib import Path
import os
import json
from typing import Dict
from .trace_file import AXIInterface, ResolvedStream, ResolvedTrace, Stream, TraceEntry, TraceMetadata, UnresolvedTrace
from .model import Function

def axi_json_obj(axi_interface: AXIInterface) -> Dict:
    return { "name": axi_interface.name, "address": axi_interface.address }


def fifo_json_obj(resolved_stream: ResolvedStream) -> Dict:
    return {
        "display_name": resolved_stream.get_display_name(),
        "id": resolved_stream.id,
        "name": resolved_stream.name,
        "width": resolved_stream.width
    }


# TODO Add more information to this
def functions_json_obj(functions: Dict[str, Function]) -> Dict[str, str]:
    return {
        key: {
            "name": value.name,
            "instruction_latencies": {
                inst.name: latency.length for inst, latency in value.instruction_latencies.items()
            }
        } for key, value in functions.items()
    }


def axi_latencies_json_obj(axi_latencies: Dict[AXIInterface, int]) -> Dict[str, int]:
    return { key.name: value for key, value in axi_latencies.items() }


def channel_depths_json_obj(channel_depths: Dict[Stream, int]):
    return { key.name: { "id": key.id, "address": key.address, "value": value } for key, value in channel_depths.items() }


# TODO Add more information to this
def trace_entry_json_obj(trace_entry: TraceEntry):
    metadata: TraceMetadata = trace_entry.metadata
    return {
        "type": trace_entry.type,
        "metadata": {
            "basic_block": metadata.basic_block,
            "count": metadata.count,
            "fifo": metadata.fifo,
            "function": metadata.function,
            "increment": metadata.increment,
            "interface": metadata.interface,
            "name": metadata.name,
            "offset": metadata.offset,
            "tripcount": metadata.tripcount
        }
    }


def resolve_trace_path(base_name: str) -> Path:
    file_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"file_dir: {file_dir}")
    return Path(file_dir) / "trace" / base_name


def write_trace_json(json_data: Dict, trace_path: Path):
    if os.path.exists(trace_path):
        print(f"Output path '{trace_path}' exists. Removing...")
        os.remove(trace_path)
    else:
        print(f"Output path '{trace_path}' does not exist. Nothing to remove.")

    os.makedirs(os.path.dirname(trace_path), exist_ok=True)

    print(f"Writing new trace to output path '{trace_path}'.")
    with open(trace_path, "w+", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def write_unresolved_trace(trace: UnresolvedTrace):
    trace_path = resolve_trace_path("unresolved_trace.json")

    json_data = {
        "byte_count": trace.byte_count,
        "line_count": trace.line_count,
        "is_ap_ctrl_chain": trace.is_ap_ctrl_chain,
        "functions": functions_json_obj(trace.functions),
        "axi_latencies": axi_latencies_json_obj(trace.axi_latencies),
        "channel_depths": channel_depths_json_obj(trace.channel_depths),
        "trace": [ trace_entry_json_obj(entry) for entry in trace.trace ]
    }

    write_trace_json(json_data, trace_path)


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

    write_trace_json(json_data, trace_path)

