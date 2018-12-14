
test: lint
	poetry run pytest test.py

lint:
	poetry run flake8 pyramid_resource.py test.py examples/

.PHONY: test lint
