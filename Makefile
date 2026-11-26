PYTHON ?= python3.11
TARGETS := setup test check seed run evaluate real-eval security
.PHONY: $(TARGETS)
$(TARGETS):
	$(PYTHON) scripts/tasks.py $@
