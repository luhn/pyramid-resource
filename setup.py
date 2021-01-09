from setuptools import setup

VERSION = "0.4.0"
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Framework :: Pyramid",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python",
]

REQUIRES = ["pyramid>=1.7,<2.0"]

EXTRAS_REQUIRE = {
    "testing": [
        "pytest~=6.2",
        "webtest~=2.0",
    ],
    "linting": [
        "black==20.8b1",
        "flake8~=3.6",
        "isort~=5.7",
    ],
}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyramid-resource",
    version=VERSION,
    description="A simple base resource class for Pyramid traversal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Theron Luhn",
    author_email="theron@luhn.com",
    url="https://github.com/luhn/pyramid-resource",
    py_modules=["pyramid_resource"],
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.6",
)
