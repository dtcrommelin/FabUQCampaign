# 
# Copyright (C) University College London, 2007-2014, all rights reserved.
# 
# This file is part of FabSim and is CONFIDENTIAL. You may not work 
# with, install, use, duplicate, modify, redistribute or share this
# file, or any part thereof, other than as allowed by any agreement
# specifically made by you with University College London.
# 
# no batch system


cd /home/wouter/FabSim3/results/ade_example1_localhost_16/RUNS/Run_34
echo Running...

/usr/bin/env > env.log

python3 /home/wouter/CWI/VECMA/FabSim3/plugins/FabSC/examples/advection_diffusion/run_ADE.py ade_in.json
