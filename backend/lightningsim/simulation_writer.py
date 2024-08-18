import json

from ._core import SimulatedModule
from .writer_utils import resolve_trace_path
from .simulator import Simulation

def write_actual_simulation(sim: Simulation):
    sim_path = resolve_trace_path("simulation", "actual_simulation.json")
    print(f"trace path: {sim_path}")


    top_module: SimulatedModule = sim.top_module

    json_data = {
        "top_module": {
            "name": top_module.name,
            "start": top_module.start,
            "end": top_module.end
        }
    }