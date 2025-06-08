#!/usr/bin/env python3
"""
Package setup script for CoHost.AI.

This script handles the installation and packaging of the CoHost.AI
streaming co-host application using setuptools.

Author: Tom Pravetz
License: MIT
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "AI-powered streaming co-host application"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="cohost-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=read_requirements(),
    
    # Metadata
    author="Tom Pravetz",
    author_email="pravetz.tom@gmail.com",
    description="AI-powered streaming co-host with voice recognition and TTS",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tompravetz/cohost.ai",
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    # Requirements
    python_requires=">=3.8",
    
    # Entry points
    entry_points={
        "console_scripts": [
            "cohost-ai=run:main",
        ],
    },
    
    # Additional files
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.example"],
    },
    
    # Keywords
    keywords="ai streaming twitch obs voice-recognition text-to-speech",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/tompravetz/cohost.ai/issues",
        "Source": "https://github.com/tompravetz/cohost.ai",
        "Documentation": "https://github.com/tompravetz/cohost.ai#readme",
    },
)
