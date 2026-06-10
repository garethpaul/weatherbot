PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON_FILES = messenger.py wit.py test_messenger.py scripts/check_weatherbot_contracts.py

.PHONY: clean lint test build verify check

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check_weatherbot_contracts.py"
	cd "$(ROOT)" && env WIT_TOKEN=test-wit-token FB_PAGE_TOKEN=test-page-token FB_VERIFY_TOKEN=test-verify-token FB_APP_SECRET=test-app-secret OPEN_WEATHER_TOKEN=test-weather-token $(PYTHON) -m unittest test_messenger

build: lint

verify: lint test build

check: clean verify
	$(MAKE) clean
