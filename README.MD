# Cincinnatus GUI

This is graphical user interface for the **Cincinnatus chess engine**. This tool provides a streamlined, user-friendly layer to interact with the engine's core capabilities using a native Python-based interface.
---

## Configuration & Setup

Follow these steps to set up a local development environment. Using a virtual environment ensures that dependencies are isolated and won't interfere with your system Python.

First clone the repo
```bash
git clone https://github.com/boce1/pyuci-chessgui.git
cd pyuci-chessgui
```

### Windows
1. Create virtual environment:
```bash
python -m venv venv
```
2. Activate the virtual environment:
```bash
.\venv\Scripts\activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Launch the application:
```bash
python main.py
```

### Linux
1. Create virtual environment:
```bash
python3 -m venv venv
```
2. Activate the virtual environment:
```bash
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Launch the application:
```bash
python3 main.py
```

## The Cincinnatus engine
The binaries are included in `engines` directory. There are executables for `Windows` and `Linux`.

This chess gui is cross-platform compatible.

The source code of the engine: https://github.com/boce1/cincinnatus.git