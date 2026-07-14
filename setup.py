"""
UPE-78: Universal Processing Engine 78
Multi-Agent Acceleration Architecture v12.0
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="upe78",
    version="12.0.0",
    author="Taylor Christian Mattheisen",
    author_email="",
    description="UPE-78 v12.0 — Multi-Agent Acceleration with Honest Self-Audit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshoshfield-a11y/UPE-78",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "black", "flake8"],
        "viz": ["matplotlib>=3.3.0"],
        "z3": ["z3-solver>=4.12.0"],
        "transformers": ["transformers>=4.30.0", "torch>=2.0.0"],
        "onnx": ["onnxruntime>=1.15.0"],
        "networkx": ["networkx>=3.0"],
    },
)
