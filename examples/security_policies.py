import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient


# ----------------------------------------------------------------------
# Working with Authentication
# -----------------------------------------------------------------------

# oc = OPCUAClient(
#     server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
#     security_policy="Basic256Sha256",
#     message_security_mode="SignAndEncrypt",
#     certificate_path="/tmp/certs/client_cert.pem",
#     private_key_path="/tmp/certs/client_key.pem",
# )


# -------------------------------------------------------------------------------------------------------
# Secure OPC UA Connection (with Databricks UC Volumes)
#
# In this example, we use Unity Catalog Volumes to securely store and access client certificates.
# This ensures our encryption keys and certificates are managed centrally under Databricks governance.
# -------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# Example UC volume paths
# Note: Replace , , and  with your actual UC volume identifiers.
# -------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Volume path structure: /Volumes////
# ----------------------------------------------------------------------------
cert_path = "/Volumes/industrial_automation/security/client_cert.pem"
key_path  = "/Volumes/industrial_automation/security/client_key.pem"

# -----------------------------------------------------------------------------------------
# Secure OPC UA client configuration
#
# oc = OPCUAClient(
#     server_url="opc.tcp://opcua.demo-this.com:51210/UA/SampleServer",
#     security_policy="Basic256Sha256",         # Strong encryption policy
#     message_security_mode="SignAndEncrypt",   # Ensures confidentiality + integrity
#     certificate_path=cert_path,               # Certificate stored in UC volume
#     private_key_path=key_path,                # Private key stored in UC volume
# )
# ---------------------------------------------------------------------------------------


oc = OPCUAClient(server_url="opc.tcp://localhost:4840/freeopcua/server/")


async def main():
    policies = await oc.get_security_policies()
    for policy in policies:
        print(policy)


asyncio.run(main())

# -------------------------------------------------------------------------------
# Expected output
#
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256
# http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep
# http://opcfoundation.org/UA/SecurityPolicy#Aes256_Sha256_RsaPss
# http://opcfoundation.org/UA/SecurityPolicy#Aes128_Sha256_RsaOaep
# http://opcfoundation.org/UA/SecurityPolicy#Aes256_Sha256_RsaPss
#
# -------------------------------------------------------------------------------