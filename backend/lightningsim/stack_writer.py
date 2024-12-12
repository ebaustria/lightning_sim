
import json
import os
from typing import Any, Dict, List
from .writer_utils import resolve_path
from .model.instruction import Instruction
from .trace_file import StackFrame, CDFGRegion, BasicBlock, ResolvedBlock, UnresolvedLoop

def terminator_object(terminator: Instruction): # type: ignore
    return {
        "id": terminator.id,
        "name": terminator.name,
        "function_name": terminator.function_name,
        "index": terminator.index
    } # type: ignore

def parent_object():
    return

def region_object(region: CDFGRegion): # type: ignore
    return {
        "name": region.name,
        "depth": region.depth,
        "type": region.type,
        "start": region.start,
        "end": region.end
    } # type: ignore

def basic_block_object(basic_block: BasicBlock): # type: ignore
    return {
        "id": basic_block.id,
        "name": basic_block.name,
        "is_dataflow": basic_block.is_dataflow,
        "is_pipeline": basic_block.is_pipeline,
        "start": basic_block.start,
        "end": basic_block.end,
        "length": basic_block.length,
        "parent": basic_block.parent.name,
        "terminator": terminator_object(basic_block.terminator),
        "region": region_object(basic_block.region)
    } # type: ignore


def resolved_block_object(resolved_block: ResolvedBlock): # type: ignore
    
    return {
        "basic_block": basic_block_object(resolved_block.basic_block),
        "num_events": resolved_block.num_events,
        "start_stage": resolved_block.start_stage,
        "end_stage": resolved_block.end_stage
    } # type: ignore

def unresolved_loop_object(unresolved_loop: UnresolvedLoop): # type: ignore
    return {
        "name": unresolved_loop.name,
        "tripcount": unresolved_loop.tripcount,
        "ii": unresolved_loop.ii,
        "end_stage": unresolved_loop.end_stage,
        "latest_end_stage": unresolved_loop.latest_end_stage
    } # type: ignore


def stack_frame_object(stack_frame: StackFrame): # type: ignore
    current_block = {}
    current_loop = {}

    if stack_frame.current_block is not None:
        current_block = resolved_block_object(stack_frame.current_block) # type: ignore

    if stack_frame.current_loop is not None:
        current_loop = unresolved_loop_object(stack_frame.current_loop) # type: ignore

    return {
        "current_block": current_block,
        "current_loop": current_loop,
        "loop_idx": stack_frame.loop_idx,
        "dynamic_stage": stack_frame.dynamic_stage,
        "static_stage": stack_frame.static_stage,
        "latest_dynamic_stage": stack_frame.latest_dynamic_stage,
        "latest_static_stage": stack_frame.latest_static_stage
    } # type: ignore

class StackWriter:
    def __init__(self):
        self.json_data: Dict[str, List[Any]] = {
            "reads": [],
            "writes": []
        }

    def add_stack_entries(self, key: str, stack: List[StackFrame]):
        for stack_frame in stack:
            stack_frame_obj = stack_frame_object(stack_frame) # type: ignore
            self.json_data[key].append(stack_frame_obj)

    def write_stack(self):
        stack_path = resolve_path("stack", "stack.json") # type: ignore
        
        if os.path.exists(stack_path):
            print(f"Stack path '{stack_path}' exists. Removing...")
            os.remove(stack_path)
        else:
            print(f"Stack path '{stack_path}' does not exist. Nothing to remove.")

        os.makedirs(os.path.dirname(stack_path), exist_ok=True)

        print(f"Writing new trace to output path '{stack_path}'.")
        with open(stack_path, "w+", encoding="utf-8") as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=4)
