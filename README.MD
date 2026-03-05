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

### Refrences

## References

- **Application Icon:** "Caesar icon" by [Delapouite](https://game-icons.net/1x1/delapouite/caesar.html) is licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
- **Chess Piece Icons:** PNGs provided by [Green Chess](https://greenchess.net/info.php?item=downloads) are licensed under [CC BY-SA](https://creativecommons.org/licenses/by-sa/3.0/).
- **Sound effects:** From [Lichess](https://github.com/lichess-org/lila/tree/master/public/sound) (Licensed under [GPL-3.0 or later](https://github.com/lichess-org/lila/blob/master/COPYING.md)).


# Executables

The engine and the GUI are Windows and Linux compatable. 

You can find the latest compiled binaries (EXE) and the source code in the [Releases](https://github.com/boce1/pyuci-chessgui/releases/tag/v1.0) section.