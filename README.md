# Music Genre Classification AI Experiment

## How to run

Makefiles were provided for convieniance, so ideally you use those. The project was built
using python3.10 on WSL2 for ubuntu.

The project was built using pyproject, meaning the process is very slightly different from
a standard python project.

Before anything, make sure you get a virtual environment going. I used venv, so ideally you do the same.

Once done, install the requirements.txt and a library called 'build'

```sh
$ pip install build
$ pip install -r requirements.txt 
```

Then run the 'make build' command (assuming you have make installed, if not, then just follow the bash commands in the makefile)

```sh
$ make build
# Or pip install build && python3 -m build && pip install . --editable
```

then run the program

```sh
$ make run
# Or simply run python3 src/main.py
```

Voila! The program will output the expected results.
