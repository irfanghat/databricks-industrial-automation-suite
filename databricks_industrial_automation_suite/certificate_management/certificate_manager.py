import os
import subprocess
from typing import Optional, List, Dict


class CertificateManager:
    """
    Manages the creation of OPC UA-compliant self-signed certificates
    using OpenSSL. Certificates are stored in a specified directory.
    """

    DEFAULT_CERTS_DIR = "/tmp/certs"
    DEFAULT_CERT_FILENAME = "client_cert.pem"
    DEFAULT_KEY_FILENAME = "client_key.pem"
    DEFAULT_CONFIG_FILENAME = "openssl_opcua.cnf"


    def __init__(
        self,
        certs_dir: Optional[str] = None,
        dns_names: Optional[List[str]] = None,
        ip_addresses: Optional[List[str]] = None,
        uris: Optional[List[str]] = None,
    ) -> None:
        self.certs_dir = certs_dir or self.DEFAULT_CERTS_DIR
        self.client_cert = os.path.join(self.certs_dir, self.DEFAULT_CERT_FILENAME)
        self.client_key = os.path.join(self.certs_dir, self.DEFAULT_KEY_FILENAME)
        self.cert_config = os.path.join(self.certs_dir, self.DEFAULT_CONFIG_FILENAME)

        self.dns_names = dns_names or ["localhost"]
        self.ip_addresses = ip_addresses or ["127.0.0.1"]
        self.uris = uris or ["urn:freeopcua:client"]

        os.makedirs(self.certs_dir, exist_ok=True)


    def generate_certificate(self, overwrite: bool = False) -> Dict[str, str]:
        if (
            os.path.exists(self.client_cert)
            and os.path.exists(self.client_key)
            and not overwrite
        ):
            return {
                "message": "Certificate and key already exist — skipping generation.",
                "certificate": self.client_cert,
            }

        try:
            self._write_openssl_config()

            self._run_openssl(["genpkey", "-algorithm", "RSA", "-out", self.client_key])

            self._run_openssl(
                [
                    "req",
                    "-x509",
                    "-new",
                    "-key",
                    self.client_key,
                    "-out",
                    self.client_cert,
                    "-days",
                    "1825",
                    "-config",
                    self.cert_config,
                ]
            )

            os.remove(self.cert_config)

            return {
                "message": "Client certificate generated successfully.",
                "certificate": self.client_cert,
            }

        except Exception as e:
            raise RuntimeError(f"Certificate generation failed: {str(e)}")


    def _write_openssl_config(self) -> None:
        """
        Writes the OpenSSL configuration file dynamically.
        """
        alt_names = []

        for i, dns in enumerate(self.dns_names, 1):
            alt_names.append(f"DNS.{i} = {dns}")

        for i, ip in enumerate(self.ip_addresses, 1):
            alt_names.append(f"IP.{i} = {ip}")

        for i, uri in enumerate(self.uris, 1):
            alt_names.append(f"URI.{i} = {uri}")

        config_template = f"""
[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = req_distinguished_name
x509_extensions     = v3_req
prompt              = no

[ req_distinguished_name ]
CN                  = OPCUA Client

[ v3_req ]
keyUsage            = critical, digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage    = serverAuth, clientAuth
subjectAltName      = @alt_names

[ alt_names ]
{chr(10).join(alt_names)}
"""

        with open(self.cert_config, "w") as f:
            f.write(config_template)

    @staticmethod
    def _run_openssl(command: List[str]) -> None:
        subprocess.run(["openssl"] + command, check=True)
