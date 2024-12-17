#!/bin/bash

lightningsim_dir="/pub/scratch/ebush/miniconda3/envs/lightningsim_trace/lib/python3.12/site-packages/lightningsim"
hbm_sim_dir="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/"

echo "Moving trace files..."
mv "$lightningsim_dir/trace/resolved_trace.json" "$hbm_sim_dir/resolved_trace.json"
mv "$lightningsim_dir/trace/unresolved_trace.json" "$hbm_sim_dir/unresolved_trace.json"

echo "Moving simulation file..."
mv "$lightningsim_dir/simulation/actual_simulation.json" "$hbm_sim_dir/actual_simulation.json"
