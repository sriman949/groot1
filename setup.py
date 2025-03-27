from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="groot-cli",
    version="0.1.0",
    author="Groot Team",
    author_email="info@groot-ai.com",
    description="An AI-powered CLI for Kubernetes troubleshooting and management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/groot-ai/groot",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "groot": [
            "templates/*.yaml",
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "groot=groot.cli:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)