VENV ?= .venv
PY := $(VENV)/bin/python
CONFIG ?= config.yaml

.PHONY: setup test run analyze

setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest tests

# make run ARGS="--distance 30" | ARGS="--resume"
run:
	$(PY) -m linktest.runner --config $(CONFIG) $(ARGS)

# make analyze RUN=<output_dir>/<run_id>
analyze:
	@test -n "$(RUN)" || { echo "usage: make analyze RUN=<run directory>"; exit 2; }
	$(PY) -m linktest.analysis --run $(RUN)
	$(PY) -m linktest.linkbudget --config $(CONFIG) --run $(RUN)
