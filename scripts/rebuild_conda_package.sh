#!/bin/bash

conda_script="$HOME/miniconda3/etc/profile.d/conda.sh"
proj_root="$HOME/Projects/hbm-sim/extern/lightning_sim"

if [ "$1" = "--remote" ]
then
  pub_dir="/pub/scratch/ebush"
  conda_script="$pub_dir/miniconda3/etc/profile.d/conda.sh"
  proj_root="$pub_dir/Projects/lightning_sim"
fi

source "$conda_script"

conda activate base

conda-build "$proj_root/recipe" -c conda-forge
