"""Setup."""

from setuptools import find_namespace_packages, setup

# Runtime requirements.
inst_reqs = [
    "stac-fastapi.api",
    "stac-fastapi.types",
    "stac-fastapi.extensions",
    "public-datasets.extensions",
]

extra_reqs = {"test": ["pytest", "pytest-cov", "pytest-asyncio", "requests"]}


setup(
    name="public-datasets.api",
    python_requires=">=3.8",
    packages=find_namespace_packages(),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
