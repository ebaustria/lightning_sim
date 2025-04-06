#!/bin/bash

lightningsim_out="/pub/scratch/ebush/Projects/hbm-sim/lightningsim_out"
lightningsim_dir="/pub/scratch/ebush/miniconda3/envs/lightningsim_trace/lib/python3.12/site-packages/lightningsim"
lightningsim_sim="$lightningsim_dir/simulation"
lightningsim_trace="$lightningsim_dir/trace"

data_sizes=("4096" "8192" "16384" "32768" "65536")

matmul="matmul"
vadd_1="vadd_1"
vadd_2="vadd_2"
vadd_3="vadd_3"
vadd_4="vadd_4"
vadd_5="vadd_5"
vadd_dataflow="vadd_dataflow"

hbm_sim_matmul="$lightningsim_out/$matmul"
hbm_sim_vadd_1="$lightningsim_out/$vadd_1"
hbm_sim_vadd_2="$lightningsim_out/$vadd_2"
hbm_sim_vadd_3="$lightningsim_out/$vadd_3"
hbm_sim_vadd_4="$lightningsim_out/$vadd_4"
hbm_sim_vadd_5="$lightningsim_out/$vadd_5"
hbm_sim_vadd_dataflow="$lightningsim_out/$vadd_dataflow"

move_file () {
    if [ -d "$1" ];
    then
        mkdir -p "$2"
        mv "$1/"* "$2/"
    else
        echo "Directory $1 could not be found. Skipping..."
    fi
}

echo "Moving simulation and trace files..."
move_file "$lightningsim_sim/$matmul" "$hbm_sim_matmul"
move_file "$lightningsim_trace/$matmul" "$hbm_sim_matmul"

move_file "$lightningsim_sim/$vadd_1" "$hbm_sim_vadd_1"
move_file "$lightningsim_trace/$vadd_1" "$hbm_sim_vadd_1"

move_file "$lightningsim_sim/$vadd_2" "$hbm_sim_vadd_2"
move_file "$lightningsim_trace/$vadd_2" "$hbm_sim_vadd_2"

move_file "$lightningsim_sim/$vadd_3" "$hbm_sim_vadd_3"
move_file "$lightningsim_trace/$vadd_3" "$hbm_sim_vadd_3"

move_file "$lightningsim_sim/$vadd_4" "$hbm_sim_vadd_4"
move_file "$lightningsim_trace/$vadd_4" "$hbm_sim_vadd_4"

move_file "$lightningsim_sim/$vadd_5" "$hbm_sim_vadd_5"
move_file "$lightningsim_trace/$vadd_5" "$hbm_sim_vadd_5"

for dat_size in "${data_sizes[@]}"; do
    move_file "$lightningsim_sim/${vadd_dataflow}_$dat_size" "${hbm_sim_vadd_dataflow}_$dat_size"
    move_file "$lightningsim_trace/${vadd_dataflow}_$dat_size" "${hbm_sim_vadd_dataflow}_$dat_size"
done
