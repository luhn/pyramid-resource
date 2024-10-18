
format:
	black pyramid_resource.py tests examples
	isort pyramid_resource.py tests examples

lint:
	flake8 pyramid_resource.py tests examples
	black --check pyramid_resource.py tests examples
	isort -c pyramid_resource.py tests examples

test:
	pytest
