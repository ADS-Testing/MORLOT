# Replication Package for "Many-Objective Reinforcement Learning for Online Testing of DNN-Enabled Systems"

This repository contains the replication package of the paper "Many-Objective Reinforcement Learning for Online Testing of DNN-Enabled Systems"

(NOTE: this markdown file is made using [atom](https://atom.io); if you do not have a proper markdown viewer, you can use [this online viewer](https://dillinger.io))


## Requirements

### Hardware
* NVIDIA GPU (>= 1080, RTX 2070+ is recommended)
* 16+ GB Memory
* 150+ GB Storage (SSD is recommended)

### Software
* Ubuntu 18.04
* python 3.7

### Python libraries
* details are in the requirement.txt file

#### How to Install Python Libraries
Initialize python's virtual environment and install the required packages:
```shell script
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Directory Structure
- `implementation`: source code of search algorithms (MORLAT and its alternatives), transfuser and automated evaluation scripts
- `data-analysis`: scripts to automatically process evaluation results data to generate figures
- `supporting-material`: supporting materials for safety requirements, constraints and possible values of test input attributes


## Installation

1. setup transfuser using the scripts from original website  (https://github.com/autonomousvision/transfuser/tree/cvpr2021) or follow the steps below:
```bash
git clone https://github.com/autonomousvision/transfuser
git checkout cvpr2021
pip -m venv env
source env/bin/activate
pip install -r requirements.txt
cd transfuser
chmod +x setup_carla.sh
./setup_carla.sh
```

2. replace `model_ckpt` and `leaderboard` in the repository with our updated version by running the following commands
```bash
rm -d -rf transfuser/model_ckpt
rm -d -rf transfuser/leaderboard
rm -d -rf transfuser/scenario_runner
cp implementation/transfuser/model_ckpt [userpath]/transfuser/model_ckpt
cp implementation/transfuser/leaderboard [userpath]/transfuser/leaderboard
cp implementation/transfuser/scenario_runner [userpath]/transfuser/scenario_runner
```
3. Move `[userpath]/transfuser` to `runner`

## Usage
Select the scenario to run
1. Update config files in `implementation/runner/lib` and  `[userpath]/transfuser/leaderboard/leaderboard` with absolute paths of current directory
2. Update following values to run different environments:

-- For Straight road environment:
```bash
update `scenario` with 0 in `lib/config` and `leaderboard/leaderboard/config` files.
Update `routes` in  leaderboard/scripts/run_evaluation.sh to `leaderboard/data/validation_routes/route_straight_road.xml`
```

-- For Left Turn environment:
```bash
update `scenario` with 1 in `lib/config` and `leaderboard/leaderboard/config` files.
Update ''routes'' in  leaderboard/scripts/run_evaluation.sh to ''leaderboard/data/validation_routes/route_left_turn.xml`
```
-- For Right Turn environment:
```bash
update  `scenario` with 2 in `lib/config` and `leaderboard/leaderboard/config` files.
Update `routes` in  `leaderboard/scripts/run_evaluation.sh` to `leaderboard/data/validation_routes/route_right_turn.xml`
```
run the algorithm using the following code

Note: To run baselines (RS, MOSA, FITEST) set RL Flag to false in  \implementation\transfuser\leaderborad\leaderborad\scenarios\fitness_value_executor.py (line 141) and vice versa
```bash
cd implementation/runner
python3 run_{search_algorithm}.py
```

Note: First run will download resnet models, after that it will run smoothly.


log files will be generated in output folder
