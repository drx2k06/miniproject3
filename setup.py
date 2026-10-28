from setuptools import find_packages, setup

setup(
    name="quantpulse",
    version="2.0.0",
    author="Daniel Richard Xavier",
    author_email="danielrichardxavier@gmail.com",
    description="Institutional Cryptocurrency Microstructure Signal & Backtesting Engine",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.2.0",
        "numpy>=1.26.0",
        "scikit-learn>=1.4.0",
        "xgboost>=2.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.36.0",
        "plotly>=5.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "quantpulse=cli:main",
        ],
    },
)
