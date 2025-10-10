✈️ F# Flight-Tools: Modular UAV Log Analysis Suite
**Flight-Tools** is a lightweight, modular diagnostic suite for analyzing UAV log files from ArduPilot (`.bin`) and PX4 (`.ulg`) systems. It’s designed for clarity, reproducibility, and community onboarding.

🔍 Features
Power analysis and current draw visualization

- Parameter listing and metadata extraction

- URI decoding and message inspection

- Modular architecture for easy extension

- Web-based interface for log upload and analysis

📁 Project Structure
```text
flight-tools/
├── app.py                  # Main Flask app
├── templates/              # HTML templates
├── tools/                  # Analysis modules
│   ├── bin_info.py
│   ├── bin_parameter_list.py
│   ├── bin_power_plot.py
├── static/                 # CSS and JS assets
├── requirements.txt        # Python dependencies
└── README.md
```
🚀 Getting Started

1. Clone the repository
```bash
git clone https://github.com/CopterCamTech/flight-tools.git
cd flight-tools
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Launch the app
```bash
python app.py
```

Then visit `http://localhost:5000` in your browser and upload a .bin or .ulg file to begin analysis.

👥 Contributing

- We welcome clean, modular contributions that align with the project’s goals:

- Add new analysis modules to 'tools/'

- Improve UI/UX in 'templates/'

- Refactor for clarity and reproducibility

The routing in 'app.py' maps uploaded '.bin' and '.ulg' logs to specific analysis functions. If you're adding a new tool, you'll likely need to:

- Define a new route in 'app.py'

- Connect it to your module in 'tools/'

- Update the UI in 'templates/' to expose the new functionality

Please fork the repo, make changes in a feature branch, and submit a pull request with a clear description.

📜 License

This project is licensed under the MIT License.
