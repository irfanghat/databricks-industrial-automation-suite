from asyncua import Client, ua
import asyncio
import logging

import os
from typing import AsyncGenerator, Optional


CERTS_DIR = "certs"
CLIENT_CERT = "ec_client_cert.pem"
CLIENT_CSR = "ec_client.csr"
CLIENT_PRIVATE_KEY = "ec_client_key.pem"

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
_logger = logging.getLogger(__name__)


# Setup shared variables for streaming
latest_value = None
value_updated = asyncio.Event()
client = None
subscription = None


class OPCUAConfig:
    server_url: str = "opc.tcp://127.0.0.1:4840/"
    security_policy: str = "None"
    message_security_mode: str = "None"
    username: Optional[str] = None
    password: Optional[str] = None
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    server_cert_path: Optional[str] = None  # Optional: Trust server cert


opcua_config = OPCUAConfig()


class SubHandler:
    """Handles data change notifications."""

    def datachange_notification(self, node, val, data):
        global latest_value
        latest_value = val
        _logger.info(f"Data change on node {node}: {val}")
        value_updated.set()  # Notify the stream about the new value


async def get_security_policies():
    """Fetches available security policies from the OPC UA server."""
    client = Client(url=opcua_config.server_url)
    policies = []

    try:
        # Set security configuration
        if opcua_config.security_policy != "None":
            security_string = (
                f"{opcua_config.security_policy},{opcua_config.message_security_mode}"
            )
            if opcua_config.certificate_path and opcua_config.private_key_path:
                security_string += (
                    f",{opcua_config.certificate_path},{opcua_config.private_key_path}"
                )
                print(f"Using security: {security_string}")

            await client.set_security_string(security_string)

        # Set authentication
        if opcua_config.username and opcua_config.password:
            client.set_user(opcua_config.username)
            client.set_password(opcua_config.password)

        await client.connect()

        # Fetch available security policies
        endpoints = await client.get_endpoints()
        policies = [ep.SecurityPolicyUri for ep in endpoints]

    except Exception as e:
        _logger.error(f"Failed to fetch security policies: {e}")

    finally:
        await client.disconnect()

    return {"security_policies": policies}


async def browse_node_recursively(node):
    """Recursively browse all child nodes and return a nested structure"""
    try:
        children = await node.get_children()
        node_data = {
            "id": node.nodeid.to_string(),
            "browse_name": str(await node.read_browse_name()),
            "children": [await browse_node_recursively(child) for child in children],
        }
        return node_data
    except Exception as e:
        return {"error": str(e)}


async def subscribe_to_node(node_id: str):
    """Subscribes to the specified OPC UA node."""
    global latest_value, client, subscription
    client = Client(url=opcua_config.server_url)

    try:
        # Set security if a policy is provided
        if opcua_config.security_policy != "None":
            security_string = (
                f"{opcua_config.security_policy},{opcua_config.message_security_mode}"
            )

            # Append certificate and private key if provided
            if opcua_config.certificate_path and opcua_config.private_key_path:
                security_string += (
                    f",{opcua_config.certificate_path},{opcua_config.private_key_path}"
                )
                print(security_string)

            await client.set_security_string(security_string)

        # Set authentication if provided
        if opcua_config.username and opcua_config.password:
            client.set_user(opcua_config.username)
            client.set_password(opcua_config.password)

        # Connect to OPC UA server
        await client.connect()
        _logger.info(f"Connected to OPC UA server at {opcua_config.server_url}")

        # Verify root node to confirm connection is valid
        root = client.get_root_node()
        _logger.info(f"Root Node: {root}")

        # Verify node exists before subscribing
        time_node = client.get_node(node_id)

        try:
            latest_value = await time_node.read_value()
            _logger.info(f"Node {node_id} found. Initial Value: {latest_value}")
        except Exception as e:
            _logger.error(f"Node {node_id} not found or unreadable: {e}")
            return  # Stop execution if node is invalid

        # Subscribe to node changes
        handler = SubHandler()
        subscription = await client.create_subscription(1000, handler)
        await subscription.subscribe_data_change(time_node)

    except Exception as e:
        _logger.error(f"Subscription error: {e}")


async def stream_data() -> AsyncGenerator[str, None]:
    """Streams OPC UA updates using SSE."""
    global latest_value
    while True:
        await value_updated.wait()  # Wait until the value updates
        yield f"data: {latest_value}\n\n"  # SSE format
        value_updated.clear()  # Reset the event


class OPCUASetupRequest:
    server_url: str
    security_policy: str = "None"
    message_security_mode: str = "None"
    username: Optional[str] = None
    password: Optional[str] = None


# ----------------------------------------
# The following section lists routes
# for managing manage opcua connections
# ----------------------------------------
async def setup_opcua(config: OPCUASetupRequest):
    """
    Sets up the OPC UA connection with the provided parameters.

    Sample configurations:

    - Working with Microsoft's OPC PLC server
    - Features:
        - Different nodes
        - Random data generation
        - Anomalies and configuration of user defined nodes

    {
        "server_url": "opc.tcp://localhost:50000/",
        "security_policy": "Basic256Sha256",
        "message_security_mode": "SignAndEncrypt",
        "username": "sysadmin",
        "password": "demo"
    }

    - Working with open62541's OPC server
    - Features:
        - Different nodes
        - Open Source OPC UA licensed under the MPL v2.0

    {
        "server_url": "opc.tcp://localhost:50000/",
        "security_policy": "Basic256Sha256",
        "message_security_mode": "SignAndEncrypt",
        "username": "sysadmin",
        "password": "demo"
    }

    """
    global opcua_config

    # Ensure the server_url is a valid OPC UA URL
    if not config.server_url.startswith("opc.tcp://"):
        return {
            "error": "Invalid server_url. Must be a full OPC UA address (opc.tcp://...)."
        }

    # Auto-assign certificate paths if security policy is not "None"
    if config.security_policy != "None":
        cert_path = os.path.join(CERTS_DIR, CLIENT_CERT)
        key_path = os.path.join(CERTS_DIR, CLIENT_PRIVATE_KEY)

        opcua_config = OPCUAConfig(
            server_url=config.server_url,
            security_policy=config.security_policy,
            message_security_mode=config.message_security_mode,
            username=config.username,
            password=config.password,
            certificate_path=cert_path,
            private_key_path=key_path,
        )
    else:
        opcua_config = config  # Use as is if no security

    return {"message": "OPC UA configuration updated", "config": opcua_config.dict()}


async def subscribe(node_id: str):
    """
    Starts the OPC UA subscription for a specific node.

    Sample nodes to subscribe to:
    - Microsoft OPC PLC Server: ns=3;s=BadFastUInt1
    - Open62541 Server: ...
    """
    if not node_id:
        raise Exception(f"Node ID is required")

    asyncio.create_task(subscribe_to_node(node_id))
    return {
        "message": f"Subscription started for {node_id}, call stream() for streaming"
    }


async def unsubscribe():
    """Unsubscribes from the OPC UA node and disconnects the client."""
    global client, subscription, latest_value
    if client and subscription:
        await subscription.delete()
        await client.disconnect()
        latest_value = None
        value_updated.clear()
        return {"message": "Unsubscribed from OPC UA node and disconnected from server"}
    return {"message": "No active subscription to unsubscribe from"}


async def browse_nodes():
    """Recursively browse all OPC UA nodes starting from the root."""
    client = Client(url=opcua_config.server_url)

    try:
        # Set security if a policy is provided
        if opcua_config.security_policy != "None":
            security_string = (
                f"{opcua_config.security_policy},{opcua_config.message_security_mode}"
            )

            if opcua_config.certificate_path and opcua_config.private_key_path:
                security_string += (
                    f",{opcua_config.certificate_path},{opcua_config.private_key_path}"
                )
                print(f"Using security: {security_string}")

            await client.set_security_string(security_string)

        # Set authentication if credentials are provided
        if opcua_config.username and opcua_config.password:
            client.set_user(opcua_config.username)
            client.set_password(opcua_config.password)

        await client.connect()

        # Start browsing from the root node
        root = client.nodes.root
        nodes = await root.get_children()

        # Recursively browse each node
        node_data = [await browse_node_recursively(node) for node in nodes]

        return {"nodes": node_data}

    except Exception as e:
        _logger.error(f"Browsing error: {e}")
        return {"error": str(e)}

    finally:
        await client.disconnect()


# ------------------------------------------
# The following is a sample request.
# NOTE: the % symbol represents the = sign
# meaning the actual request would be http://...i=2253
# where i=2253 is the Node Id
#
# curl -X 'GET' \
# 'http://localhost:8000/opcua/browse/i%3D2253' \
#  -H 'accept: application/json'
# ------------------------------------------
async def browse_children(node_id: str):
    """
    Browse the children of a specific node.

    Sample nodes to browse:
    - Microsoft OPC PLC Server: i=7617
    - Open62541 Server: ...
    """
    client = Client(url=opcua_config.server_url)

    try:
        # Set security configuration
        if opcua_config.security_policy != "None":
            security_string = (
                f"{opcua_config.security_policy},{opcua_config.message_security_mode}"
            )
            if opcua_config.certificate_path and opcua_config.private_key_path:
                security_string += (
                    f",{opcua_config.certificate_path},{opcua_config.private_key_path}"
                )
                print(f"Using security: {security_string}")

            await client.set_security_string(security_string)

        # Set authentication
        if opcua_config.username and opcua_config.password:
            client.set_user(opcua_config.username)
            client.set_password(opcua_config.password)

        await client.connect()

        # Browse children of the specified node
        node = client.get_node(node_id)
        children = await node.get_children()
        node_data = [
            {
                "id": child.nodeid.to_string(),
                "browse_name": str(await child.read_browse_name()),
            }
            for child in children
        ]

        return {"nodes": node_data}

    except Exception as e:
        _logger.error(f"Browsing error: {e}")
        return {"error": str(e)}

    finally:
        await client.disconnect()


async def stream():
    """Returns a real-time stream of data updates."""
    return stream_data()


async def fetch_security_policies():
    """Returns the available security policies."""
    return await get_security_policies()


"""
# OPC UA Security Policies:
- None: No security (no encryption or signing).
- Basic128Rsa15: Uses RSA-1024 and AES-128 for encryption. (Deprecated)
- Basic256: Uses RSA-2048 and AES-256 for encryption.
- Basic256Sha256: Uses RSA-2048 and SHA-256 for stronger security.
- Aes128_Sha256_RsaOaep: Uses AES-128 and SHA-256 with RSA-OAEP encryption.
- Aes256_Sha256_RsaPss: Uses AES-256 and SHA-256 with RSA-PSS encryption.

# OPC UA Message Security Modes:
- None: No security (plain communication).
- Sign: Signs messages to ensure integrity but does not encrypt.
- SignAndEncrypt: Signs and encrypts messages for full security.
"""
