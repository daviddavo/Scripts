#!/bin/bash

source /opt/anaconda/bin/activate root

for env in $(conda env list | cut -d" " -f1 | tail -n+4); do
    conda activate $env
    # $@
    sudo ipython kernel install --name="$env"
    conda deactivate
done
