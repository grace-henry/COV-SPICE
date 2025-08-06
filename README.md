# COV-SPICE

The code and dataset for the paper **"COV-SPICE: Coverage-Guided Mutation Strategy Optimization for SPICE Circuit Simulation via Multi-Armed Bandit"**, implemented in Python. COV-SPICE extracts seed netlists from official SPICE circuit repositories and applies a coverage-driven mutation strategy. By utilizing the Multi-Armed Bandit (MAB) model, COV-SPICE adaptively selects mutation strategies to maximize test coverage. The framework performs differential testing across solvers (e.g., Ngspice and Xyce) and uses feedback to refine mutation selection dynamically.

## 1. Project Structure

```
.
├── data/
│   ├── raw_data.zip         # Raw netlist test cases (to be extracted)
│   └── seed_netlist.zip     # Prepared seed netlists (to be extracted)
│
├── scripts/
│   ├── CoverageGuidedBandit.py     # MAB-based mutation strategy selector
│   ├── CoverageParser.py           # Parses coverage info from simulation logs
│   ├── differential_testing.py     # Differential testing for Ngspice
│   ├── differential_testing_xyce.py# Differential testing for Xyce
│   ├── extract_error.py            # Extracts errors from log files
│   ├── mutation_xyce.py            # Mutation handler for Xyce-compatible formats
│   ├── mutations.py                # Mutation rules and syntax templates
│   └── reinforcement_learning.py  # Reinforcement learning utilities (optional)
│
├── main_ngspice.py       # Entry script for Ngspice-based workflow
├── main_xyce.py          # Entry script for Xyce-based workflow
├── requirements.txt      # Python dependencies
└── README.md             # Project description
```

## 2. Environment Setup

- Python 3.10 is recommended.
- Dependencies can be installed with:

```bash
pip install -r requirements.txt
```

- Ensure that the paths to `ngspice` and `xyce` are added to your system’s environment variables.

## 3. Data Preparation

Before running the main script, extract the raw circuit data and seed netlists into the `data/` folder.

```bash
unzip data/raw_data.zip -d data/raw_data
unzip data/seed_netlist.zip -d data/seed_netlist
```

Each extracted netlist should correspond to a valid simulation input for Ngspice or Xyce.

## 4. Usage

### Run with Ngspice

```bash
python main_ngspice.py --seed_dir ./data/seed_netlist/ngspice
```

### Run with Xyce

```bash
python main_xyce.py --seed_dir ./data/seed_netlist/xyce
```

Each main file executes a full cycle of:
- Mutation strategy selection
- Netlist mutation
- Simulation and coverage measurement
- Differential testing
- Strategy score update based on reward (coverage gain)

Results and error traces will be saved in a result directory if implemented
