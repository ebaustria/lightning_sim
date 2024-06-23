#!/bin/bash

source ./rebuild_conda_package.sh $1
source ./update_channel.sh $1
source ./remake_env.sh $1
