PROJECT_NAME:=music-models
INT:=python3
SRC:=src/main.py

INSTALL:=pip3 install
BUILD:=-m build

BLACK:=-m black src
ISORT:=-m isort src

help:
	@echo "Usage:"
	@echo "    make <command>"
	@echo "Commands:"
	@echo "    build        Builds and installs the project and it's dependencies."
	@echo "    run		Runs the project, after building it."
	@echo "    clean 	Removes all pycache, egg-info, dist, and build files."

build:
	${INSTALL} build
	${INT} ${BUILD}
	${INSTALL} --editable .

lint:
	${INT} ${BLACK}
	${INT} ${ISORT}

run: lint
	${INT} ${SRC}
