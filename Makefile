# Variables
PY_FILES = $(wildcard *.py)
HTML_FILES = $(wildcard templates/*.html)
JS_FILES = $(wildcard static/*.js)

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	#force install latest whisper
test:
	#python -m pytest -vv --cov=main --cov=mylib test_*.py

format:	
	black *.py 

# Lint all files
lint: lint-python lint-html lint-js

# Format all files
format: format-python format-html format-js

# Lint Python files using pylint
lint-python:
	@echo "Linting Python files..."
	pylint --disable=R,C *.py

# Lint HTML files using Prettier
lint-html:
	@echo "Linting HTML files..."
	prettier --check $(HTML_FILES)

# Lint JavaScript files using Prettier
lint-js:
	@echo "Linting JavaScript files..."
	prettier --check $(JS_FILES)

# Format Python files using Black
format-python:
	@echo "Formatting Python files..."
	black $(PY_FILES)

# Format HTML files using Prettier
format-html:
	@echo "Formatting HTML files..."
	prettier --write $(HTML_FILES)

# Format JavaScript files using Prettier
format-js:
	@echo "Formatting JavaScript files..."
	prettier --write $(JS_FILES)

container-lint:
	#docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint

deploy:
	#deploy goes here
		
all: install lint test format deploy
