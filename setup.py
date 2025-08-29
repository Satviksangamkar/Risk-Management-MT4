from setuptools import setup, find_packages

setup(
    name="mt4-risk-calculator",
    version="1.0.0",
    description="MT4 Risk Management and R-Multiple Calculator",
    author="Satviksangamkar",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "beautifulsoup4>=4.12.2",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
