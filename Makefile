PYTHON ?= python3
PYTHON2 ?= python2

PYTHON_FILES = messenger.py wit.py test_messenger.py scripts/check_weatherbot_contracts.py

.PHONY: clean lint test build verify check

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check_weatherbot_contracts.py
	@if command -v $(PYTHON2) >/dev/null 2>&1 && $(PYTHON2) -c "import bottle, requests, webtest" >/dev/null 2>&1; then \
		env WIT_TOKEN=test-wit-token FB_PAGE_TOKEN=test-page-token FB_VERIFY_TOKEN=test-verify-token OPEN_WEATHER_TOKEN=test-weather-token $(PYTHON2) -m unittest test_messenger; \
	else \
		echo "Skipping legacy Python 2 test_messenger: dependencies are not installed."; \
	fi

build: lint

verify: lint test build

check: clean verify
	$(MAKE) clean
