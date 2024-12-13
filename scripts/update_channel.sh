#!/bin/bash

conda_dir="$HOME/miniconda3"
conda_script="$conda_dir/etc/profile.d/conda.sh"
proj_root="$HOME/Projects/hbm-sim/extern/lightning_sim"

if [ "$1" = "--remote" ]
then
  pub_dir="/pub/scratch/ebush"
  conda_dir="$pub_dir/miniconda3"
  conda_script="$conda_dir/etc/profile.d/conda.sh"
  proj_root="$pub_dir/Projects/lightning_sim"
fi

source "$conda_script"

conda activate base

chan_dir="$proj_root/channel/linux-64"

echo "Emptying channel directory..."
rm -rf "$chan_dir"/*

for file in "$conda_dir"/conda-bld/linux-64/lightningsim_trace-0.2.2*.tar.bz2; do
  base_name=${file##*/}
  if [[ $base_name =~ "*" ]]; then
    echo "File name $base_name contains asterisk. Ignoring."
    continue
  fi
  echo "Moving file $base_name"
  mv "$file" "$chan_dir/$base_name"
done

conda index "$proj_root/channel/"
