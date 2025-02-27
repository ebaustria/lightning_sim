#!/bin/bash

lightningsim_dir="/pub/scratch/ebush/miniconda3/envs/lightningsim_trace/lib/python3.12/site-packages/lightningsim"

vadd="vadd"
matmul="matmul"
vadd_1="vadd_1"
vadd_2="vadd_2"
vadd_3="vadd_3"

hbm_sim_vadd="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$vadd"
hbm_sim_matmul="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$matmul"
hbm_sim_vadd_1="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$vadd_1"
hbm_sim_vadd_2="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$vadd_2"
hbm_sim_vadd_3="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out/$vadd_3"

traces_vadd="$lightningsim_dir/trace/$vadd"
traces_matmul="$lightningsim_dir/trace/$matmul"

move_file () {
    if [ -d "$1" ];
    then
        mkdir -p "$2"
        mv "$1/actual_simulation.json" "$2/actual_simulation.json"
    else
        echo "File $1 could not be found. Skipping..."
    fi
}

echo "Moving simulation files..."
move_file "$lightningsim_dir/simulation/$vadd" "$hbm_sim_vadd"
move_file "$lightningsim_dir/simulation/$matmul" "$hbm_sim_matmul"
move_file "$lightningsim_dir/simulation/$vadd_1" "$hbm_sim_vadd_1"
move_file "$lightningsim_dir/simulation/$vadd_2" "$hbm_sim_vadd_2"
move_file "$lightningsim_dir/simulation/$vadd_3" "$hbm_sim_vadd_3"
