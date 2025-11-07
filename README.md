

# Flight-Tools

Flight-Tools is a modular toolkit of programs for analyzing PX4 and ArduPilot flight logs.  All code is Python scripts or HTML documents.

With few exceptions, data reported by Flight-Tools scripts can be obtained with other tools.  An advantage of Flight-Tools scripts is that they are single purpose, pre-written and don't require setup or configuration.  Another advantage is that Flight-Tools is cross platform with Linux and Windows support.

I have future plans to write Windows executable versions of these scripts - which will eliminate the need for a python environment.

## 🚀 Features

### Mulitple operating environments:
  - **Headless** using commands and parameters (CLI Mode)
    - Text output presented to the terminal
    - Graphic output saved as .PNG files
    - Graphic output automatically displayed where associated apps for .PNG display exist
  - **GUI** using web browsers (FLASK Mode)
    - Local GUI operation uses FLASK
    - Remote GUI operation uses FLASK, but a reverse proxy web server is recommended
  - **Linux** and **Windows** compatibility

### PX4 and ArduPilot support:
  - Scripts are coded individually for PX4 and ArduPilot log files
  - Scripts generate similar output for PX4 and ArduPilot log files

### Support for both PIP and UV python package managers
  - `REQUIREMENTS.TXT` support both PIP and UV
  - `PYPROJECT.TOML` supports UV


## 💡 Try the Live Version

Go to [www.coptercam.tech](https://www.coptercam.tech/flight-tools) for live versions of Flight-Tools scripts.
You can explore log analysis, chart rendering, and route visualization directly in your browser—no setup required.

##   🐍 Python Dependencies and Requirements

- Familiarity using Python scripts and Python virtual environments
- Python 3.10 or later recommended

## 📁 Directory Structure

```bash
flight-tools/                       # Flight-tools python project root
flight-tools/tools/                 # Python scripts for log analysis
flight-tools/webapp/routes/         # Flask route definitions
flight-tools/webapp/templates/      # HTML templates for web interface
flight-tools/webapp/uploads/        # Temporary storage for uploaded logs and created chart .png files
```

## 👉 Python scripts in `flight-tools/tools`

| Script Name | Log Type | Mode | Description |
|---|---|---|---|
| bin_info.py | `.bin`  ArduPilot | CLI & FLASK | Lists record types |
| bin_parameter_list.py | `.bin`  ArduPilot | CLI & FLASK | Lists parameters and their values |
| bin_range_signal.py | `.bin`  ArduPilot | CLI & FLASK | Charts control and telemetry radio RSSI & LQ against 3D distance |
| bin_power_plot.py | `.bin`  ArduPilot | CLI & FLASK | Charts voltage, amperage and watt-hours |
| ulg_info.py | `.ulg`  PX4 | CLI & FLASK | Lists record types |
| ulg_parameter.list.py | `.ulg`  PX4 | CLI & FLASK | Lists parameters and their values |
| ulg_range_signal.py | `.ulg`  PX4 | CLI & FLASK | Charts control and telemetry radio RSSI & LQ against 3D distance |
| ulg_power_plot.py | `ulg`  PX4 | CLI & FLASK | Charts voltage, amperage and watt-hours |
| ulg_log_explorer.py | `.ulg`  PX4 | FLASK only | Allows drilling down through log message type and field names to display field values |


## 👉 CLI Mode (command line) Requirements & Syntax

A python virtual environment must be active to run python scripts.

A suitable python virtual environment can be created using the `flight-tools/requirements.txt` file.

The `flight-tools` Python scripts are in the `flight-tools/tools` directory.  They are run conventionally.  For example, the script `bin_info.py` is run like this:

```bash
(venv) user@host:~/flight-tools$ Python3 tools/bin_info.py parameter-1 parameter-2 ...
```
## 👉 FLASK MODE (GUI) Requirements and Syntax

FLASK is a micro web server for python scripts.  When FLASK is enabled, python scripts are available on a local web browser using `http://localhost:5000`  (port 5000 is a FLASK default - and can be changed)

A python virtual environment must be active to run FLASK.

A suitable python virtual environment can be created using the `flight-tools/requirements.txt` file.

Web requests to a FLASK web server are routed to the appropriate script by supporting scripts in the `flight-tools/webapp/routes` directory.  This routing uses special web address to get to the appropriate Flight-Tools python script.

### To activate a Python virtual environment

| **Linux** | **Windows** |
|---|---|
| `source .venv/bin/activate` | `.venv\Scripts\activate` |

### To start FLASK (Linux):
```bash
(venv) user@host:~/flight-tools$ python3 -m webapp.app
```

### To start FLASK (Windows):
```bash
(venv) C:/flight-tools$ python -m webapp.app
```

### FLASK web addresses

| Flight-Tools Script Name | FLASK web address |
|---|---|
| `bin_info.py` | `http://localhost:5000/bin-info` |
| `bin_parameter_list.py` | `http://localhost:5000/bin-parameter-list` |
| `bin_range_signal.py` | `http://localhost:5000/bin-range-signal` |
| `bin_power_plot.py` | `http://localhost:5000/bin-power-plot` |
| `ulg_info.py` | `http://localhost:5000/ulg-info` |
| `ulg_range_signal.py` | `http://localhost:5000/ulg-range-signal`|
| `ulg_power_plot.py` | `http://localhost:5000/ulg-power-plot` |
| `ulg_log_explorer.py` | `http://localhost:5000/ulg-log-explorer` |

## ⚙️ Quickstart - Cloneing the Repo - Creating and Activating Python Virtual Environment - Starting FLASK

### Option 1: Using Python's built-in `venv`

```bash
# Clone the repo
git clone https://github.com/coptercamtech/flight-tools.git
cd flight-tools

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app (Linux)
python3 -m webapp.app

# Run Flask app (Windows)
python -m webapp.app
```

### Option 2: Using `uv` (ultra-fast Python package manager)

```bash
# Clone the repo
git clone https://github.com/coptercamtech/flight-tools.git
cd flight-tools

# Create environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run Flask app (Linux)
python3 -m webapp.app

# Run Flask app (Windows)
python -m webapp.app
```

## 🧪 CLI Parameters

Most scripts in `tools/` support direct command-line execution. (Presently only `ulg_log_log_explorer.py` must be run in FLASK mode)

Scripts that generate text output will generate the output on the terminal.

Scripts that generate graphics/charts will create a `.PNG` file.  On a workstation with windows support, the output file will be opened with the app associated with `.PNG` file type.

In a headless or non-graphic workstation environment, the output graphic/chart can be saved to a filename specified by a script parameter.

Output files are saved in the flight-tools/uploads directory.

By default, the output is automatically displayed - no parameters are required to dispaly output.

### Common Parameters

- `input_file` (required): Path to `.bin` or `.ulg` log file
- `--mode` (optional): Controls output behavior
  - `cli` (default): Prints summary or chart to console
  - `file`: Saves output to a file (e.g., `.txt` or `.png`)
  - `flask`: Returns dictionary (used internally by Flask routes)

### Example: Text Summary

### Print summary to console

```bash
python3 tools/bin_info.py path/to/log.bin
```

### Save summary to file (auto-named as log.bin_info.txt)

```bash
python3 tools/bin_info.py path/to/log.bin --mode file
```

### Example: Chart Rendering

```bash
# Show chart in GUI environment
python3 tools/bin_power_plot.py path/to/log.bin

# Save chart to PNG in headless mode
python3 tools/bin_power_plot.py path/to/log.bin --mode file
```

> Note: Output filenames are auto-generated unless a script explicitly supports custom naming. GUI mode is assumed unless headless rendering is required.

## 🧠 Contributor Notes

- All scripts follow a modular pattern with reusable functions
- Flask routes are stateless and template-driven
- Templates use Jinja2 with fallback logic
- Uploads are stored temporarily in `webapp/uploads/`
- Cleanup script architecture is planned but not yet implemented

## 📚 Full Documentation

For detailed architecture, onboarding flow, and AI re-engagement tips, visit:

👉 [Flight-Tools Techical Documentation](https://www.coptercam.tech/flight-tools-documentation/)
