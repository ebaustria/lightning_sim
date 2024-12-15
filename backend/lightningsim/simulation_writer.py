import json
import os
from typing import Any, Dict, List
from pathlib import Path

from ._core import AxiGenericIo, AxiInterface, AxiInterfaceIo, Fifo, FifoIo, SimulatedModule # type: ignore
from .writer_utils import resolve_path
from .simulator import Simulation


def axi_generic_io_obj(axi_generic_ios: List[AxiGenericIo]): # type: ignore
    return [
        {
            "range_length": generic_io.range.length,
            "range_offset": generic_io.range.offset,
            "delay": generic_io.delay,
            "time": generic_io.time,
            "module": generic_io.module
        } for generic_io in axi_generic_ios
    ] # type: ignore


def axi_io_json_obj(address: int, axi_interface_io: AxiInterfaceIo) -> Dict[str, Any]:
    return {
        "address": address,
        "readreqs": axi_generic_io_obj(axi_interface_io.readreqs),
        "reads": axi_generic_io_obj(axi_interface_io.reads),
        "writereqs": axi_generic_io_obj(axi_interface_io.writereqs),
        "writeresps": [resp for resp in axi_interface_io.writeresps],
        "writes": axi_generic_io_obj(axi_interface_io.writes)
    }


def axi_json_arr(axi_io: Dict[AxiInterface, AxiInterfaceIo]) -> List[Dict[str, Any]]:
    return [ axi_io_json_obj(key.address, value) for key, value in axi_io.items() ]


def fifo_json_obj(fifo_io: Dict[Fifo, FifoIo]):
    pass


def write_simulation(json_data: Dict[str, Any]):
    sim_path: Path = resolve_path("simulation", "actual_simulation.json")
    print(f"trace path: {sim_path}")

    if os.path.exists(sim_path):
        print(f"Output path '{sim_path}' exists. Removing...")
        os.remove(sim_path)
    else:
        print(f"Output path '{sim_path}' does not exist. Nothing to remove.")

    os.makedirs(os.path.dirname(sim_path), exist_ok=True)

    print(f"Writing new simulation to output path '{sim_path}'.")
    with open(sim_path, "w+", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def write_actual_simulation(sim: Simulation):
    top_module: SimulatedModule = sim.top_module

    json_data: Dict[str, Any] = {
        "top_module": {
            "name": top_module.name,
            "start": top_module.start,
            "end": top_module.end
        },
        "axi_io": axi_json_arr(sim.axi_io),
        "fifo_io": fifo_json_obj(sim.fifo_io)
    }

    write_simulation(json_data)
