from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pysaxs",
    version="0.1.0",
    author="PySAXS Development Team",
    author_email="",
    description="AI-powered SAXS crystalline structure identification and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/pysaxs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "scikit-learn>=1.0.0",
        "tensorflow>=2.8.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "click>=8.0.0",
        "tqdm>=4.62.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "jupyter",
            "notebook",
        ],
    },
    entry_points={
        "console_scripts": [
            "pysaxs=pysaxs.interface.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pysaxs": ["neural_network/models/*.h5", "data/*.json"],
    },
)