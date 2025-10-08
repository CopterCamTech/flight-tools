# 🛠️ Flight Tools: Installation Guide

This guide walks you through installing and running `flight-tools` on a Linux-based system. It ensures reproducibility and matches the production environment used at [flight-tools.coptercam.tech](https://flight-tools.coptercam.tech).

---

### 📦 Requirements

- Linux-based system with internet access
- Git installed (`sudo apt install git`)
- Python **3.11.x** installed and available as `python3.11`
- Ability to create and activate virtual environments

---

### 🐍 Step 0: Check for Python 3.11

Run:

```bash
python3.11 --version
```
If Python 3.11 is not installed, follow one of these methods:

### Option A: Install via package manager (if available)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### Option B: Install from source

sudo apt install -y build-essential libssl-dev zlib1g-dev \
libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
tk-dev libffi-dev wget

```bash
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tgz
sudo tar xzf Python-3.11.13.tgz
cd Python-3.11.13
sudo ./configure --enable-optimizations
sudo make -j4
sudo make altinstall
```

Verify:

```bash
python3.11 --version
```

### 📁 Step 1: Clone the repository

```bash
cd ~
git clone https://github.com/coptercamtech/flight-tools.git ~/flight-tools
```

### 🧪 Step 2: Create and activate the virtual environment

```bash
python3.11 -m venv ~/flight-tools
source ~/flight-tools/bin/activate
```

### 📦 Step 3: Install dependencies

```bash
pip install -r ~/flight-tools/requirements.txt
```

### 📂 Step 4: Add `pymavlink_src` if required
If the application expects a local file like `pymavlink_src/DFReader.py`, and this directory is not included in the repository, you can manually add it:

```bash
mkdir -p ~/flight-tools/pymavlink_src
cd ~/flight-tools/pymavlink_src
wget https://raw.githubusercontent.com/ArduPilot/pymavlink/master/DFReader.py
```
This pulls the public version of `DFReader.py` from the upstream `pymavlink` GitHub repo.

### 🚀 Step 5: Launch the app

```bash
cd ~/flight-tools
python app.py
```

Visit http://localhost:5000 in your browser to confirm the interface loads and all modules respond.

### 🧭 Notes

- This guide assumes Python 3.11 is required for compatibility. Python 3.12 and 3.13 are untested.

- All dependencies are installed from public sources. No proprietary files are included in the repository.

- The virtual environment is embedded directly in the project root for simplicity.







