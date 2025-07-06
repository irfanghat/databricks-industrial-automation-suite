import os
import subprocess
from typing import Optional, List, Dict


class CertificateManager:
    """
    Manages the creation of OPC UA-compliant self-signed certificates using OpenSSL.
    Allows parameterization of relevant fields in the OpenSSL config.
    """

    DEFAULT_CERTS_DIR = "/tmp/certs"
    DEFAULT_CERT_FILENAME = "client_cert.pem"
    DEFAULT_KEY_FILENAME = "client_key.pem"
    DEFAULT_CONFIG_FILENAME = "openssl_opcua.cnf"

    OPENSSL_CONFIG_TEMPLATE = """
[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = req_distinguished_name
x509_extensions     = v3_req
prompt              = no

[ req_distinguished_name ]
CN                 = {common_name}

[ v3_req ]
keyUsage           = critical, digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage   = serverAuth, clientAuth
subjectAltName     = @alt_names

[ alt_names ]
{alt_names}
"""

    def __init__(
        self,
        certs_dir: Optional[str] = None,
        cert_filename: Optional[str] = None,
        key_filename: Optional[str] = None,
        config_filename: Optional[str] = None,
        common_name: str = "OPCUA Client",
        dns_names: Optional[List[str]] = None,
        ip_addresses: Optional[List[str]] = None,
        uris: Optional[List[str]] = None,
    ) -> None:
        """
        Initializes the CertificateManager with customizable options.

        Args:
            certs_dir (Optional[str]): Directory to store certs and keys.
            cert_filename (Optional[str]): Certificate filename.
            key_filename (Optional[str]): Private key filename.
            config_filename (Optional[str]): OpenSSL config filename.
            common_name (str): Certificate Common Name (CN).
            dns_names (Optional[List[str]]): DNS SAN entries.
            ip_addresses (Optional[List[str]]): IP SAN entries.
            uris (Optional[List[str]]): URI SAN entries.
        """
        self.certs_dir = certs_dir or self.DEFAULT_CERTS_DIR
        self.cert_filename = cert_filename or self.DEFAULT_CERT_FILENAME
        self.key_filename = key_filename or self.DEFAULT_KEY_FILENAME
        self.config_filename = config_filename or self.DEFAULT_CONFIG_FILENAME

        self.common_name = common_name
        self.dns_names = dns_names or ["localhost"]
        self.ip_addresses = ip_addresses or ["127.0.0.1"]
        self.uris = uris or ["urn:freeopcua:client"]

        self.client_cert = os.path.join(self.certs_dir, self.cert_filename)
        self.client_key = os.path.join(self.certs_dir, self.key_filename)
        self.cert_config = os.path.join(self.certs_dir, self.config_filename)

        os.makedirs(self.certs_dir, exist_ok=True)

    def generate_certificate(self, overwrite: bool = False) -> Dict[str, str]:
        """
        Generates a self-signed client certificate and private key.

        Args:
            overwrite (bool): Whether to overwrite existing files.

        Returns:
            Dict[str, str]: Message and path to the generated certificate.

        Raises:
            RuntimeError: If OpenSSL operations fail.
        """
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
        Writes a parameterized OpenSSL configuration file for certificate generation.
        """
        alt_names = []
        for i, dns in enumerate(self.dns_names, start=1):
            alt_names.append(f"DNS.{i} = {dns}")
        for i, ip in enumerate(self.ip_addresses, start=1):
            alt_names.append(f"IP.{i} = {ip}")
        for i, uri in enumerate(self.uris, start=1):
            alt_names.append(f"URI.{i} = {uri}")

        alt_names_str = "\n".join(alt_names)

        config_content = self.OPENSSL_CONFIG_TEMPLATE.format(
            common_name=self.common_name,
            alt_names=alt_names_str,
        )

        with open(self.cert_config, "w") as f:
            f.write(config_content)

    @staticmethod
    def _run_openssl(command: List[str]) -> None:
        """
        Runs an OpenSSL command with error handling.

        Args:
            command (List[str]): OpenSSL command arguments.

        Raises:
            subprocess.CalledProcessError: If OpenSSL command fails.
        """
        subprocess.run(["openssl"] + command, check=True)