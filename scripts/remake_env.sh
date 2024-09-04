#!/bin/bash

env_name=lightningsim_trace
conda_script=miniconda3/etc/profile.d/conda.sh
full_conda_path="$HOME/$conda_script"
proj_root="$HOME/Projects/LightningSim"

if [ "$1" = "--remote" ]
then
  pub_dir="/pub/scratch/ebush"
  full_conda_path="$pub_dir/$conda_script"
  proj_root="$pub_dir/Projects/lightning_sim"
fi

local_chan=$proj_root/channel

source "$full_conda_path"

conda activate base
conda remove -n $env_name --all --yes
conda create --yes --name $env_name --channel $local_chan --channel conda-forge $env_name
