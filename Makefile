
format:
	black pyramid_resource.py tests
	isort pyramid_resource.py tests

lint:
	flake8 pyramid_resource.py tests
	black --check pyramid_resource.py tests
	isort -c pyramid_resource.py tests
