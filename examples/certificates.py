from databricks_industrial_automation_suite.certificate_management.certificate_manager import (
    CertificateManager,
)

cm = CertificateManager(
    certs_dir="/tmp/certs",
    dns_names=["opcua.demo-this.com"],  # Required for valid SAN
    ip_addresses=["127.0.0.1"],         # Optional
    uris=["urn:freeopcua:client"],      # Standard OPC UA client URI
)

if __name__ == "__main__":
    cm.generate_certificate(overwrite=True)