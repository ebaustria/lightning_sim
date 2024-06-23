#!/bin/bash

scripts_dir="$HOME/Projects/LightningSim/scripts"

if [ "$1" = "--remote" ]
then
  pub_dir="/pub/scratch/ebush"
  scripts_dir="$pub_dir/Projects/lightning_sim/scripts"
fi

source $scripts_dir/rebuild_conda_package.sh $1
source $scripts_dir/update_channel.sh $1
source $scripts_dir/remake_env.sh $1
