"""Setup."""

from setuptools import find_namespace_packages, setup

# Runtime requirements.
inst_reqs = ["stac-pydantic==1.3.8"]

extra_reqs = {"test": ["pytest", "pytest-cov"]}


setup(
    name="public-datasets.extensions",
    python_requires=">=3.7",
    packages=find_namespace_packages(),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
