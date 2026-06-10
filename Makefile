PYTHON ?= python3

PYTHON_FILES = messenger.py wit.py test_messenger.py scripts/check_weatherbot_contracts.py

.PHONY: clean lint test build verify check

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check_weatherbot_contracts.py
	@if $(PYTHON) -c "import bottle, requests, webtest" >/dev/null 2>&1; then \
		env WIT_TOKEN=test-wit-token FB_PAGE_TOKEN=test-page-token FB_VERIFY_TOKEN=test-verify-token OPEN_WEATHER_TOKEN=test-weather-token $(PYTHON) -m unittest test_messenger; \
	else \
		echo "Skipping dependency-backed test_messenger: install requirements.txt and test-requirements.txt."; \
	fi

build: lint

verify: lint test build

check: clean verify
	$(MAKE) clean
