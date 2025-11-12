#!/bin/bash

pip uninstall dist/opcua_manufacturing_server-0.0.1-py3-none-any.whl -y

sudo rm -rf build && sudo rm -rf dist

python3 setup.py sdist bdist_wheel

pip install dist/opcua_manufacturing_server-0.0.1-py3-none-any.whl 