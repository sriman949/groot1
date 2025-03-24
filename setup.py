from setuptools import setup, find_packages

setup(
    name="groot-k8s",
    version="1.0.0",
    description="Advanced AI-powered Kubernetes troubleshooting assistant",
    author="Groot Team",
    author_email="groot@example.com",
    packages=find_packages(),
    install_requires=[
        "kubernetes>=24.2.0",
        "openai>=0.27.0",
        "spacy>=3.5.0",
        "tabulate>=0.9.0",
        "termcolor>=2.2.0",
        "flask>=2.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "rich>=12.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "groot=groot.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Systems Administration",
    ],
)