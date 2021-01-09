from distutils.core import setup

VERSION = "0.3.0"
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Framework :: Pyramid",
]

REQUIRES = ["pyramid>=1.7,<2.0"]

EXTRAS_REQUIRE = {
    "testing": [
        "pytest~=6.2",
        "webtest~=2.0",
    ],
    "linting": [
        "black==20.8b1"
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
    author="Theron Luhn",
    author_email="theron@luhn.com",
    url="https://github.com/luhn/pyramid-resource",
    py_modules=["pyramid_resource"],
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.4,<4.0",
)
