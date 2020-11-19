"""Setup."""

from setuptools import find_namespace_packages, setup

# Runtime requirements.
inst_reqs = ["rasterio", "stac-pydantic"]

extra_reqs = {
    "test": ["pytest", "pytest-cov"],
}


setup(
    name="public-datasets-feeder",
    version="0.1.0",
    python_requires=">=3.7",
    packages=find_namespace_packages(),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
