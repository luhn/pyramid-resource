
format:
	ruff format pyramid_resource.py tests examples

lint:
	ruff check pyramid_resource.py tests examples
	ruff format --check pyramid_resource.py tests examples

test:
	pytest
