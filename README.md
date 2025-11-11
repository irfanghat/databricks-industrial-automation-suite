# Databricks Industrial Automation Suite (Databricks Free Edition Hackathon)

## Overview

The **Databricks Industrial Automation Suite** is a comprehensive library designed to support all major industrial automation protocols within the Databricks ecosystem. It enables seamless integration, data exchange, and control across diverse industrial systems, helping enterprises unify and modernize their operational technology (OT) and IT workflows.

---

## Supported Protocols

| Protocol                    | Status        |
| --------------------------- | ------------- |
| OPC UA                      | ✅ Supported   |
| Matter                      | ⬜ Planned     |
| Modbus TCP                  | ⬜ In Progress |
| HART Communication Protocol | ⬜ Planned     |
| MQTT                        | ⬜ Planned     |

---

## Getting Started

### Installation (User Mode)

To install the published package:

```bash
%pip install databricks-industrial-automation-suite
```

---

## Development Setup (Build & Install Locally)

If you want to **develop**, **test**, or **contribute** to the project locally, follow these steps:

### Clone the repository

```bash
git clone https://github.com/yourusername/databricks-industrial-automation-suite.git
cd databricks-industrial-automation-suite
```

---

### Install dependencies using Poetry

If you use **Poetry** (recommended):

```bash
poetry install
```

This creates a virtual environment and installs all dependencies automatically.

To enter that environment:

```bash
poetry shell
```

---

### Build the package

```bash
poetry build
```

This generates distributable files under `dist/`:

```
dist/
 ├── databricks_industrial_automation_suite-0.1.0.tar.gz
 └── databricks_industrial_automation_suite-0.1.0-py3-none-any.whl
```

---

### Install the built package locally

Option 1 — Install from wheel:

```bash
pip install dist/databricks_industrial_automation_suite-0.1.0-py3-none-any.whl
```

Option 2 — Editable install for live code updates:

```bash
pip install -e .
```

---

### Test the installation

Try importing the library or running example scripts:

```bash
python
>>> from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient
>>> print("Library loaded successfully!")
```

Or execute one of the included examples:

```bash
python examples/browse_child_nodes.py
```

---

### Rebuild cleanly (optional)

If you need a fresh build:

```bash
rm -rf dist build *.egg-info
poetry build
```

---

### (Optional) Local virtual environment test

You can also test the install in a clean environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dist/*.whl
```

---

## Usage Highlights

* Native OPC UA client connection support (streaming, browsing, and security).
* Modular, extensible architecture for upcoming industrial protocols.
* Designed for scalability, observability, and Databricks integration.

---

## Contribution

This suite is under active development.
We welcome contributions of:

* New protocol integrations
* Documentation improvements
* Bug fixes or performance enhancements

Please open issues or pull requests on the GitHub repository.

---

## Additional Resources

* **Certificate Management:** Use tools like [XCA](https://hohnstaedt.de/xca/) to manage secure client certificates.
* **Testing:** You can run an OPC UA demo server locally via Docker:

  ```bash
  docker run -d -p 4840:4840 ghcr.io/falk-werner/opcua-server:latest
  ```