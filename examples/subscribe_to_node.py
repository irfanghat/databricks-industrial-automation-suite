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
