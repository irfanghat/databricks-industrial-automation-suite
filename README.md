# Databricks Industrial Automation Suite

## Overview

The **Databricks Industrial Automation Suite** is a comprehensive library designed to support all major industrial automation protocols within the Databricks ecosystem. It enables seamless integration, data exchange, and control across diverse industrial systems, helping enterprises unify and modernize their operational technology (OT) and IT workflows.

---

## Supported Protocols

| Protocol                    | Status            |
| --------------------------- | ----------------- |
| OPC UA                      | ✅ Supported      |
| Modbus TCP                  | ⬜ Planned        |
| HART Communication Protocol | ⬜ Planned        |
| MQTT                        | ⬜ Planned        |

---

## Getting Started

### Installation

To install the library, run the following command in your notebook:

```bash
%pip install databricks-industrial-automation-suite
```

---

## Usage Highlights

* Native support for OPC UA client connections, with plans to expand to Modbus TCP, HART, MQTT, and others.
* Modular architecture allowing easy integration of new protocols.
* Designed for scalability, reliability and ease of use.

---

## Contribution

This suite is under active development. We welcome contributions ranging from new protocol implementations to bug fixes and documentation improvements. Please open issues or pull requests on the repository.

---

## Additional Resources

* Consider using certificate management tools such as **XCA** for managing secure connections.
* Docker-based demo servers for OPC UA and other protocols can be integrated for testing purposes.
