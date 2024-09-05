import json
import os
from typing import Any, Dict, List
from pathlib import Path

from ._core import AxiGenericIo, AxiInterface, AxiInterfaceIo, Fifo, FifoIo, SimulatedModule # type: ignore
from .writer_utils import resolve_path
from .simulator import Simulation


def axi_generic_io_obj(axi_generic_ios: List[AxiGenericIo]):
    return [
        { "range": generic_io.range, "time": generic_io.time } for generic_io in axi_generic_ios
    ]


def axi_io_json_obj(axi_interface_io: AxiInterfaceIo):
    return {
        "readreqs": axi_generic_io_obj(axi_interface_io.readreqs),
        "reads": axi_generic_io_obj(axi_interface_io.reads),
        "writereqs": axi_generic_io_obj(axi_interface_io.writereqs),
        "writeresps": [resp for resp in axi_interface_io.writeresps],
        "writes": axi_generic_io_obj(axi_interface_io.writes)
    }


def axi_json_obj(axi_io: Dict[AxiInterface, AxiInterfaceIo]) -> Dict[int, Any]:
    return { key.address: axi_io_json_obj(value) for key, value in axi_io.items() }


def fifo_json_obj(ifo_io: Dict[Fifo, FifoIo]):
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

    json_data = {
        "top_module": {
            "name": top_module.name,
            "start": top_module.start,
            "end": top_module.end
        },
        "axi_io": axi_json_obj(sim.axi_io),
        "fifo_io": fifo_json_obj(sim.fifo_io)
    }

    write_simulation(json_data)
