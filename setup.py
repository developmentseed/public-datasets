"""Setup."""

from typing import List

from setuptools import find_namespace_packages, setup

# Runtime requirements.
inst_reqs: List[str] = []

extra_reqs = {
    "docs": ["nbconvert", "mkdocs", "mkdocs-material", "mkdocs-jupyter", "pygments"],
}


setup(
    name="public-datasets",
    version="0.1.0",
    python_requires=">=3.7",
    packages=find_namespace_packages(
        include=["public_datasets.*"], exclude=["*tests*"],
    ),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
