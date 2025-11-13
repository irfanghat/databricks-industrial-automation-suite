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


# ---------------------------------------------------------------------------
# Sample Node Ids (Retrieved by running <oc.browse_all()>)
#
#
# 'id': 'ns=2;i=1',
# 'browse_name': "QualifiedName(NamespaceIndex=2, Name='IndustrialPlant')",
# 'children': [
#     {
#     'id': 'ns=2;i=2',
#     'browse_name': "QualifiedName(NamespaceIndex=2, Name='BoilerSystem')",
#     'children': [
#         {
#         'id': 'ns=2;i=5',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='Temperature')",
#         'children': [

#         ]
#         },
#         {
#         'id': 'ns=2;i=6',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='Pressure')",
#         'children': [

#         ]
#         }
#     ]
#     },
#     {
#     'id': 'ns=2;i=3',
#     'browse_name': "QualifiedName(NamespaceIndex=2, Name='PumpSystem')",
#     'children': [
#         {
#         'id': 'ns=2;i=7',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='RPM')",
#         'children': [

#         ]
#         },
#         {
#         'id': 'ns=2;i=8',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='FlowRate')",
#         'children': [

#         ]
#         }
#     ]
#     },
#     {
#     'id': 'ns=2;i=4',
#     'browse_name': "QualifiedName(NamespaceIndex=2, Name='TankSystem')",
#     'children': [
#         {
#         'id': 'ns=2;i=9',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='Level')",
#         'children': [

#         ]
#         },
#         {
#         'id': 'ns=2;i=10',
#         'browse_name': "QualifiedName(NamespaceIndex=2, Name='pH')",
#         'children': [

#         ]
#         }
#     ]
#     },
#
#   ...
#
# --------------------------------------------------------------------------


async def main():
    await oc.connect()

    node_ids = [
        "ns=2;i=5",  # Temperature
        "ns=2;i=6",  # Pressure
        "ns=2;i=7",  # RPM
    ]

    for node_id in node_ids:
        await oc.subscribe_to_node(node_id)

    async for event in oc.stream():
        print(event)  # Now prints nice structured dicts with timestamp, etc.


asyncio.run(main())
