#!/bin/bash

conda_dir="$HOME/miniconda3"
conda_script="$conda_dir/etc/profile.d/conda.sh"
proj_root="$HOME/Projects/LightningSim"

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

rm -rf "$chan_dir/*"

for file in "$conda_dir/conda-bld/linux-64/lightningsim_trace*.tar.bz2"; do
  base_name=${file##*/}
  if [[ $base_name =~ "*" ]]; then
    echo "File name $base_name contains asterisk. Ignoring."
    break
  fi
  mv "$file" "$chan_dir/$base_name"
done

conda index "$proj_root/channel/"
conda env update --file "$proj_root/environment.yml"
