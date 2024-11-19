# Convert Trajectories from experiments to Mobius format

Mobius uses a json format to represent trajectories.

This script converts txt trajectories from this [data archive](https://ped.fz-juelich.de/db/) in the appropriate json file.

## Json definition

The json structure includes three main blocks:

- **Entities**: A list of entities, each with attributes like ID, name, max speed, and map plane information.
- **Simulation**: A time-series list where each entry corresponds to a simulation time, containing samples of entity positions, modes, rotations, and speeds.
- **Metadata**: A block providing overall simulation information, such as duration, distance maps, timestamps, and additional parameters.

## Usage

1. Create a virtual environment and install the requirements:

(recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

2. Run script 

```bash
python txt_to_json.py --help
```
