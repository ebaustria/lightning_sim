from pathlib import Path
import os
import json
import sys
from typing import Dict

from .writer_utils import resolve_path
from .trace_file import AXIInterface, ResolvedStream, ResolvedTrace, Stream, TraceEntry, UnresolvedTrace
from .model import Function, Instruction, InstructionLatency, CDFGEdge, BasicBlock
from .model.function import Port
from .model.dataflow import Channel


def axi_json_obj(axi_interface: AXIInterface) -> Dict:
    return { "name": axi_interface.name, "address": axi_interface.address }


def fifo_json_obj(resolved_stream: ResolvedStream) -> Dict:
    return {
        "display_name": resolved_stream.get_display_name(),
        "id": resolved_stream.id,
        "name": resolved_stream.name,
        "width": resolved_stream.width
    }


def operand_json_obj(operand: CDFGEdge) -> Dict:
    return {
        "id": operand.id,
        "type": operand.type,
        "is_back_edge": operand.is_back_edge,
        "source_id": operand.source_id,
        "sink_id": operand.sink_id
    }


def channel_json_obj(channel: Channel):
    return {
        "id": channel.id,
        "name": channel.name,
        "is_scalar": channel.is_scalar,
        "sources": [source.id for source in channel.sources],
        "sinks": [sink.id for sink in channel.sinks]
    }


def basic_block_json_obj(basic_block: BasicBlock):
    dataflow = {}
    if basic_block.dataflow:
        dataflow = {
            "channels": [channel_json_obj(channel) for channel in basic_block.dataflow.channels]
        }
    return {
        "id": basic_block.id,
        "ii": basic_block.ii if basic_block.ii is not None else -1,
        "end": basic_block.end,
        "start": basic_block.start,
        "is_dataflow": basic_block.is_dataflow,
        "is_pipeline": basic_block.is_pipeline,
        "is_pipeline_critical_path": basic_block.is_pipeline_critical_path,
        "is_sequential": basic_block.is_sequential,
        "dataflow": dataflow
    }


def instruction_json_obj(inst: Instruction) -> Dict:
    inst.operands
    return {
        "bitwidth": inst.bitwidth,
        "id": inst.id,
        "function_name": inst.function_name,
        "index": inst.index,
        "name": inst.name,
        "opcode": inst.opcode,
        "operands": [operand_json_obj(operand) for operand in inst.operands if operand is not None],
        "latency": inst_latency_json_obj(inst.latency)
    }


def inst_latency_json_obj(latency: InstructionLatency) -> Dict:
    return {
        "length": latency.length,
        "start": latency.start,
        "end": latency.end,
        "relative_start": latency.relative_start,
        "relative_end": latency.relative_end
    }


def port_json_obj(port: Port) -> Dict:
    return {
        "id": port.id,
        "interface_type": port.interface_type,
        "name": port.name
    }


# TODO Add more information to this
def functions_json_obj(functions: Dict[str, Function]) -> Dict[str, str]:
    return {
        key: {
            "name": func.name,
            "instructions": {
                id: instruction_json_obj(inst) for id, inst in func.instructions.items()
            },
            "ports": { port_id: port_json_obj(port) for port_id, port in func.ports.items() },
            "basic_blocks": { bb_id: basic_block_json_obj(basic_block) for bb_id, basic_block in func.basic_blocks.items() }
        } for key, func in functions.items()
    }


def axi_latencies_json_obj(axi_latencies: Dict[AXIInterface, int]) -> Dict[str, int]:
    return { key.name: value for key, value in axi_latencies.items() }


def channel_depths_json_obj(channel_depths: Dict[Stream, int]):
    return { key.name: { "id": key.id, "address": key.address, "value": value } for key, value in channel_depths.items() }


def derive_metadata(trace_entry: TraceEntry):
    type = trace_entry.type
    metadata = trace_entry.metadata

    if type in ("trace_bb", "loop_bb"):
        return { "function": metadata.function, "basic_block": metadata.basic_block }
    if type in ("fifo_read", "fifo_write"):
        return { "fifo": { "address": metadata.fifo.address, "id": metadata.fifo.id, "name": metadata.fifo.name } }
    if type in ("axi_readreq", "axi_writereq"):
        return { "offset": metadata.offset, "increment": metadata.increment, "count": metadata.count, "interface": { "address": metadata.interface.address, "name": metadata.interface.name } }
    if type in ("axi_read", "axi_write", "axi_writeresp"):
        return { "interface": { "address": metadata.interface.address, "name": metadata.interface.name } }
    return { "name": metadata.name, "tripcount": metadata.tripcount }


# TODO Add more information to this
def trace_entry_json_obj(trace_entry: TraceEntry):
    return {
        "type": trace_entry.type,
        "metadata": derive_metadata(trace_entry)
    }


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
    trace_path = resolve_path("trace", "unresolved_trace.json")

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
    trace_path = resolve_path("trace", "resolved_trace.json")
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

