import asyncio
import logging
from typing import Optional, List, Dict, AsyncGenerator

from asyncua import Client

_logger = logging.getLogger(__name__)


class OPCUAClient:
    """
    A client wrapper for connecting to OPC UA servers using asyncua.

    Supports:
    - Configurable security policies and credentials
    - Recursive node browsing
    - Real-time data change subscriptions
    - Streaming updates via asyncio generator
    """

    def __init__(
        self,
        server_url: str,
        security_policy: str = "None",
        message_security_mode: str = "None",
        certificate_path: Optional[str] = None,
        private_key_path: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize the OPC UA client.

        Args:
            server_url (str): URL of the OPC UA server (e.g., "opc.tcp://localhost:4840").
            security_policy (str): OPC UA security policy (e.g., "Basic256Sha256").
            message_security_mode (str): Security mode (e.g., "SignAndEncrypt").
            certificate_path (Optional[str]): Path to client certificate file (.pem).
            private_key_path (Optional[str]): Path to client private key file (.pem).
            username (Optional[str]): Username for authentication.
            password (Optional[str]): Password for authentication.
        """
        self.server_url = server_url
        self.security_policy = security_policy
        self.message_security_mode = message_security_mode
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        self.username = username
        self.password = password

        self.client = Client(url=self.server_url)
        self.subscription = None
        self.subscribed_node = None
        self.latest_value = None
        self.value_updated = asyncio.Event()

    async def connect(self) -> None:
        """
        Connects to the OPC UA server with the configured security and credentials.

        Raises:
            Exception: If the connection or configuration fails.
        """
        if self.security_policy != "None":
            security_string = f"{self.security_policy},{self.message_security_mode}"
            if self.certificate_path and self.private_key_path:
                security_string += f",{self.certificate_path},{self.private_key_path}"
            await self.client.set_security_string(security_string)

        if self.username and self.password:
            self.client.set_user(self.username)
            self.client.set_password(self.password)

        await self.client.connect()
        _logger.info(f"Connected to OPC UA server: {self.server_url}")

    async def disconnect(self) -> None:
        """
        Disconnects from the OPC UA server and cleans up subscriptions.
        """
        if self.subscription:
            await self.subscription.delete()
        await self.client.disconnect()
        self.latest_value = None
        self.value_updated.clear()
        _logger.info("Disconnected from OPC UA server")

    async def browse_all(self) -> List[Dict]:
        """
        Recursively browse all child nodes starting from the root.

        Returns:
            List[Dict]: A list of node structures with children recursively populated.
        """
        root = self.client.nodes.root
        children = await root.get_children()
        return [await self._browse_node_recursive(node) for node in children]

    async def browse_children(self, node_id: str) -> List[Dict]:
        """
        Browse direct children of a specific node.

        Args:
            node_id (str): Node ID string (e.g., "ns=3;s=Temperature").

        Returns:
            List[Dict]: List of child node identifiers and browse names.
        """
        node = self.client.get_node(node_id)
        children = await node.get_children()
        return [
            {
                "id": child.nodeid.to_string(),
                "browse_name": str(await child.read_browse_name()),
            }
            for child in children
        ]

    async def get_security_policies(self) -> List[str]:
        """
        Fetches supported security policies from the OPC UA server.

        Returns:
            List[str]: List of supported SecurityPolicy URIs.
        """
        await self.connect()
        endpoints = await self.client.get_endpoints()
        await self.disconnect()
        return [ep.SecurityPolicyUri for ep in endpoints]

    async def subscribe_to_node(self, node_id: str) -> None:
        """
        Subscribes to data change events on a given node.

        Args:
            node_id (str): Node ID to subscribe to (e.g., "ns=3;s=Sensor1").

        Raises:
            Exception: If the node does not exist or is unreadable.
        """
        node = self.client.get_node(node_id)
        self.subscribed_node = node
        self.latest_value = await node.read_value()

        handler = self._SubHandler(self)
        self.subscription = await self.client.create_subscription(1000, handler)
        await self.subscription.subscribe_data_change(node)

    async def stream(self) -> AsyncGenerator[str, None]:
        """
        Stream real-time value changes using server-sent event format.

        Yields:
            str: Formatted SSE message with the latest value.
        """
        while True:
            await self.value_updated.wait()
            yield f"data: {self.latest_value}\n\n"
            self.value_updated.clear()

    async def _browse_node_recursive(self, node) -> Dict:
        """
        Helper method to recursively browse a node's children.

        Args:
            node: An asyncua Node object.

        Returns:
            Dict: Nested node structure.
        """
        try:
            children = await node.get_children()
            return {
                "id": node.nodeid.to_string(),
                "browse_name": str(await node.read_browse_name()),
                "children": [
                    await self._browse_node_recursive(child) for child in children
                ],
            }
        except Exception as e:
            return {"error": str(e)}

    class _SubHandler:
        """
        Internal subscription handler for OPC UA data changes.
        """

        def __init__(self, outer: "OPCUAClient"):
            self.outer = outer

        def datachange_notification(self, node, val, data):
            """
            Callback triggered on data change.

            Args:
                node: The node that changed.
                val: New value.
                data: Additional change data.
            """
            self.outer.latest_value = val
            _logger.info(f"Data change on node {node}: {val}")
            self.outer.value_updated.set()


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
