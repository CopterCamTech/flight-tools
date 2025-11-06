

# Flight-Tools

Flight-Tools is a modular toolkit of programs for analyzing PX4 and ArduPilot flight logs.  All code is Python and HTML.

With some notable exceptions, Flight-Tools scripts report log file data that can be obtained with other tools.  The advantage of Flight-Tools scripts is that they are pre-written and don't require setup or configuration.

## 🚀 Features

### Mulitple environment support:
  - Headless using commands and parameters
    - Text output presented to the terminal
    - Graphic output saved as .PNG files
    - Graphic output automatically displayed where associated apps for .PNG display exist
  - GUI using web browsers
    - Local GUI operation uses FLASK
    - Remote GUI operation uses FLASK, but a reverse proxy web server is recommended
  - Linux and Windows compatibility

### PX4 and ArduPilot support:
  - Scripts are coded for either PX4 or ArduPilot log files
  - Most scripts have similar versions for PX4 and ArduPilot log files

### Support for both PIP and UV python package managers
  - `REQUIREMENTS.TXT` support both PIP and UV
  - `PYPROJECT.TOML` supports UV


## 💡 Try the Live Version

Live versions of most Flight-Tools scripts are available on the [www.coptercam.tech](https://www.coptercam.tech/flight-tools) website.
You can explore log analysis, chart rendering, and route visualization directly in your browser—no setup required.

## 📁 Directory Structure

```bash
flight-tools/                       # Flight-tools python project root
flight-tools/tools/                 # Python scripts for log analysis
fligt-tools/webapp/routes/          # Flask route definitions
flight-tools/webapp/templates/      # HTML templates for web interface
flight-tools/webapp/uploads/        # Temporary storage for uploaded logs and created chart .png files
```

## ⚙️ Quickstart

### Option 1: Using Python's built-in `venv`

```bash
# Clone the repo
git clone https://github.com/your-username/flight-tools.git
cd flight-tools

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python3 -m webapp.app
```

### Option 2: Using `uv` (ultra-fast Python package manager)

```bash
# Clone the repo
git clone https://github.com/your-username/flight-tools.git
cd flight-tools

# Create environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Run Flask app
python3 -m webapp.app
```

## 🧪 CLI Usage

Most scripts in `tools/` support direct command-line execution. The only required argument is the input log file. Optional parameters vary by script.

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

👉 [Flight-Tools Documentation](https://www.coptercam.tech/flight-tools-documentation/)
