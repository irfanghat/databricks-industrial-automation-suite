from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "OPC UA Manufacturing Plant Server Simulation"

setup(
    name="opcua-manufacturing-server",
    version="0.0.1",
    author="Irfan Ghat",
    author_email="irfan.ghat@obueatske.com",
    description="OPC UA Manufacturing Plant Server Simulation for IIoT and Databricks demos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/irfanghat/Databricks-Hackathon-Nov-2025",
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=[
        "asyncua>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "opcua-manufacturing-server=opcua_manufacturing_server.main:run",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
