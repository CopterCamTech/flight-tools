🛩️ flight-tools: Modular UAV Log Analysis Suite
flight-tools is a modular toolkit for analyzing UAV flight logs in both ArduPilot and PX4 formats. Designed for clarity, extensibility, and reproducibility, it helps users extract insights from .bin, .ulg, and other telemetry formats using a clean web interface and customizable plots.

🛫 Live version available at [flight-tools](https://coptercam.tech)

🚀 Features
📊 Power analysis, parameter inspection, and URI decoding for .bin and .ulg logs

🧩 Modular architecture with reusable plotting utilities and templates

🖥️ Lightweight web interface built with Flask and HTML templates

🔍 Supports both ArduPilot and PX4 log formats

🧼 Clean separation of runtime artifacts and source code for maintainability

📁 Project Structure
Code

```text
flight-tools/
├── app.py                  # Main Flask app
├── templates/              # HTML templates for UI
├── tools/                  # Core analysis modules and plotting utilities
├── LICENSE                 # MIT License
├── README.md               # This file
└── .gitignore              # Repo hygiene rules (customizable by contributors)
```

⚙️ Getting Started
Clone the repo:

```bash
git clone https://github.com/CopterCamTech/flight-tools.git
cd flight-tools
```
Install dependencies: (Coming soon: requirements.txt)

Run the app:

bash
python app.py
Upload a log file and explore the analysis modules.

🧠 Philosophy
This project values:

Transparency: Every module is documented and reproducible

Modularity: Tools are loosely coupled and easy to extend

Community: Designed to onboard contributors with minimal friction

🤝 Contributing
We welcome thoughtful contributions! Please:

Fork the repo and create a feature branch

Follow naming conventions and commit hygiene

Submit a pull request with a clear description

Coming soon:

Contributor checklist

Module onboarding guide

📜 License
This project is licensed under the MIT License.
