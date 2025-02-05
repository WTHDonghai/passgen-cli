from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="passgen-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A secure password generator and manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/passgen-cli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1.7',
        'colorama>=0.4.6',
        'cryptography>=41.0.1',
        'SQLAlchemy>=2.0.23',
    ],
    entry_points={
        'console_scripts': [
            'passgen=src.cli:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 