#!/bin/bash

lightningsim_dir="/pub/scratch/ebush/miniconda3/envs/lightningsim_trace/lib/python3.12/site-packages/lightningsim"

vadd="vadd"
matmul="matmul"

hbm_sim_vadd="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$vadd"
hbm_sim_matmul="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$matmul"

traces_vadd="$lightningsim_dir/trace/$vadd"
traces_matmul="$lightningsim_dir/trace/$matmul"

move_file () {
    if [ -f $1 ];
    then
        mv $1 $2
    else
        echo "File $1 could not be found. Skipping..."
    fi
}

echo "Moving trace files..."
move_file "$traces_vadd/resolved_trace.json" "$hbm_sim_vadd/resolved_trace.json"
move_file "$traces_vadd/unresolved_trace.json" "$hbm_sim_vadd/unresolved_trace.json"
move_file "$traces_matmul/resolved_trace.json" "$hbm_sim_matmul/resolved_trace.json"
move_file "$traces_matmul/unresolved_trace.json" "$hbm_sim_matmul/unresolved_trace.json"

echo "Moving simulation file..."
move_file "$lightningsim_dir/simulation/$vadd/actual_simulation.json" "$hbm_sim_vadd/actual_simulation.json"
move_file "$lightningsim_dir/simulation/$matmul/actual_simulation.json" "$hbm_sim_matmul/actual_simulation.json"
