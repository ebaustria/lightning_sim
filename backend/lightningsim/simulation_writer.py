import json
import os
from typing import Any, Dict, List
from pathlib import Path

from ._core import AxiGenericIo, AxiInterface, AxiInterfaceIo, Fifo, FifoIo, SimulatedModule # type: ignore
from .writer_utils import resolve_path
from .simulator import Simulation
from .module_data_struct import ModuleDataStruct


def axi_generic_io_obj(axi_generic_ios: List[AxiGenericIo], mod_data_struct: ModuleDataStruct): # type: ignore
    return [
        {
            "range_length": generic_io.range.length,
            "range_offset": generic_io.range.offset,
            "delay": generic_io.delay,
            "time": generic_io.time,
            "module": mod_data_struct.get_module_name_if_present(generic_io.mod_id)
        } for generic_io in axi_generic_ios
    ] # type: ignore


def axi_io_json_obj(address: int, axi_interface_io: AxiInterfaceIo, mod_data_struct: ModuleDataStruct) -> Dict[str, Any]:
    return {
        "address": address,
        "readreqs": axi_generic_io_obj(axi_interface_io.readreqs, mod_data_struct),
        "reads": axi_generic_io_obj(axi_interface_io.reads, mod_data_struct),
        "writereqs": axi_generic_io_obj(axi_interface_io.writereqs, mod_data_struct),
        "writeresps": [resp for resp in axi_interface_io.writeresps],
        "writes": axi_generic_io_obj(axi_interface_io.writes, mod_data_struct)
    }


def axi_json_arr(axi_io: Dict[AxiInterface, AxiInterfaceIo], mod_data_struct: ModuleDataStruct) -> List[Dict[str, Any]]:
    return [ axi_io_json_obj(key.address, value, mod_data_struct) for key, value in axi_io.items() ]


def fifo_json_obj(fifo_io: Dict[Fifo, FifoIo]):
    pass


def make_dir_name(top_module: str, cu_num: int | None, data_size: int | None):
    dir_name: str = top_module

    if data_size is not None:
        dir_name += f"_{data_size}"
        return dir_name

    if cu_num is not None:
        dir_name += f"_{cu_num}"
        return dir_name

    return dir_name


def write_simulation(json_data: Dict[str, Any], cu_num: int | None, data_size: int | None):
    top_module: str = json_data["top_module"]["name"]
    dir_name: str = make_dir_name(top_module, cu_num, data_size)
    sim_path: Path = resolve_path("simulation", f"{dir_name}/actual_simulation.json")
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


def write_actual_simulation(sim: Simulation, mod_data_struct: ModuleDataStruct, cu_num: int | None, data_size: int | None):
    top_module: SimulatedModule = sim.top_module

    json_data: Dict[str, Any] = {
        "top_module": {
            "name": top_module.name,
            "start": top_module.start,
            "end": top_module.end
        },
        "axi_io": axi_json_arr(sim.axi_io, mod_data_struct),
        "fifo_io": fifo_json_obj(sim.fifo_io)
    }

    write_simulation(json_data, cu_num, data_size)
