To get started...

```
git clone --recurse-submodules https://github.com/LordsBoards/PyKLE-Schematic.git
cd ./PyKLE-Schematic

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

./main.py
```

Place your KLE as keyboard-layout.json or specify w/ CLI args
The current CLI commands are:

--kle - Path to KLE file 

--switchlib - Path to switch library 

--stabilizerlib - Path to stabilizer library 

