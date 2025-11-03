
```markdown
# Flight-Tools

Flight-Tools is a modular toolkit for analyzing PX4 and ArduPilot flight logs. It supports both command-line and Flask-based web interfaces, with a focus on clarity, reproducibility, and contributor-friendly architecture.

## 🚀 Features

- Dual-mode execution (CLI + Flask)
- Modular scripts for `.ulg` and `.bin` log formats
- Dynamic web interface with multi-step tools
- Stateless Flask routes and fallback messaging
- Clean chart rendering and summary tables
- Designed for sustainable re-engagement and onboarding

## 📁 Directory Structure
```
```bash
tools/                  # Python scripts for log analysis
webapp/routes/          # Flask route definitions
webapp/templates/       # HTML templates for web interface
webapp/uploads/         # Temporary storage for uploaded logs
webapp/static/          # Optional static assets (CSS, JS, images)
```
```markdown
## ⚙️ Quickstart

### Option 1: Using Python's built-in `venv`
```
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
```markdown
### Option 2: Using `uv` (ultra-fast Python package manager)
```
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
```markdown
## 🧪 CLI Usage

Most scripts in `tools/` support direct command-line execution. The only required argument is the input log file. Optional parameters vary by script.

### Common Parameters

- `input_file` (required): Path to `.bin` or `.ulg` log file
- `--mode` (optional): Controls output behavior
  - `cli` (default): Prints summary or chart to console
  - `file`: Saves output to a file (e.g., `.txt` or `.png`)
  - `flask`: Returns dictionary (used internally by Flask routes)

### Example: Text Summary

# Print summary to console
```
```bash
python3 tools/bin_info.py path/to/log.bin
```
```markdown
# Save summary to file (auto-named as log.bin_info.txt)
```
```bash
python3 tools/bin_info.py path/to/log.bin --mode file
```
```markdown
### Example: Chart Rendering
```
```bash
# Show chart in GUI environment
python3 tools/bin_power_plot.py path/to/log.bin

# Save chart to PNG in headless mode
python3 tools/bin_power_plot.py path/to/log.bin --mode file
```
```markdown
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
```

---