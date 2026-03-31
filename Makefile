.PHONY: install test lint clean generate-pd generate-all

install:
	pip install -e .

test:
	pytest tests/ -v --cov=src/sozo_generator --cov-report=term-missing

lint:
	python -m py_compile src/sozo_generator/**/*.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -rf outputs/documents/ outputs/visuals/ outputs/qa/

generate-pd:
	python -m sozo_generator.cli.main build-condition --condition parkinsons

generate-all:
	python -m sozo_generator.cli.main build-all
