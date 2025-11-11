"""
Smart Subscription - Auto-Discovery
====================================
Automatically discovers nodes by browsing the server, then subscribes to them.
No hardcoded node IDs needed!
"""

import asyncio
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient


async def find_node_by_name(client, root_path, target_name):
    """
    Recursively search for a node by its browse name.
    
    Args:
        client: OPC UA client
        root_path: Starting node ID (e.g., "ns=2;i=1")
        target_name: Name to search for (e.g., "Vibration")
    
    Returns:
        Node ID string or None
    """
    try:
        node = await client.get_node(root_path)
        browse_name = await node.read_browse_name()
        
        # Check if this is the node we're looking for
        if target_name.lower() in str(browse_name).lower():
            return root_path
        
        # Search children
        children = await node.get_children()
        for child in children:
            child_id = str(child.nodeid)
            result = await find_node_by_name(client, child_id, target_name)
            if result:
                return result
    except Exception as e:
        pass
    
    return None


async def discover_and_map_nodes(client):
    """
    Discover all important nodes in the manufacturing plant.
    Returns a dictionary mapping friendly names to node IDs.
    """
    print("🔍 Discovering nodes...")
    
    # Start from the root ManufacturingPlant object
    root = "ns=2;i=1"  # This should be ManufacturingPlant
    
    # Nodes we want to find
    search_targets = [
        # Production
        ("line1_production_rate", "ProductionLine1", "ProductionRate"),
        ("line1_efficiency", "ProductionLine1", "Efficiency"),
        ("line1_motor_temp", "ProductionLine1", "MotorTemperature"),
        ("line1_motor_vibration", "ProductionLine1", "MotorVibration"),
        
        ("line2_production_rate", "ProductionLine2", "ProductionRate"),
        ("line2_efficiency", "ProductionLine2", "Efficiency"),
        ("line2_motor_temp", "ProductionLine2", "MotorTemperature"),
        ("line2_motor_vibration", "ProductionLine2", "MotorVibration"),
        
        # Pumps
        ("pump1_flow", "Pump1", "FlowRate"),
        ("pump1_pressure", "Pump1", "DischargePressure"),
        ("pump1_vibration", "Pump1", "Vibration"),
        ("pump1_temperature", "Pump1", "Temperature"),
        
        ("pump2_flow", "Pump2", "FlowRate"),
        ("pump2_pressure", "Pump2", "DischargePressure"),
        ("pump2_vibration", "Pump2", "Vibration"),  # CRITICAL!
        ("pump2_temperature", "Pump2", "Temperature"),  # CRITICAL!
        
        # Mixing
        ("mix_tank_level", "MixingSystem", "TankLevel"),
        ("mix_tank_temp", "MixingSystem", "TankTemperature"),
        ("mix_ph", "MixingSystem", "pH"),
        
        # Quality
        ("quality_pass_rate", "QualityControl", "PassRate"),
        ("quality_defects", "QualityControl", "DefectsFound"),
        
        # Energy
        ("total_power", "Energy", "TotalPowerConsumption"),
        ("energy_cost", "Energy", "CostTodayUSD"),
        
        # Maintenance
        ("pump1_health", "Maintenance", "Pump1HealthScore"),
        ("pump2_health", "Maintenance", "Pump2HealthScore"),
        ("line2_health", "Maintenance", "Line2HealthScore"),
        
        # Alarms
        ("active_alarms", "Alarms", "ActiveAlarms"),
        ("last_alarm", "Alarms", "LastAlarmMessage"),
    ]
    
    node_map = {}
    
    # Browse the entire tree
    print("📚 Browsing server structure...")
    tree = await client.browse_all()
    
    # Recursively search the tree
    def search_tree(tree_node, path=""):
        """Recursively search the browsed tree"""
        if isinstance(tree_node, dict):
            browse_name = tree_node.get('browse_name', '')
            node_id = tree_node.get('id', '')
            
            # Check against all search targets
            for friendly_name, parent, child in search_targets:
                if parent in browse_name and child in browse_name:
                    node_map[friendly_name] = node_id
                    print(f"  ✓ Found {friendly_name}: {node_id}")
            
            # Search children
            for child_node in tree_node.get('children', []):
                search_tree(child_node, path + "/" + str(browse_name))
        elif isinstance(tree_node, list):
            for item in tree_node:
                search_tree(item, path)
    
    search_tree(tree)
    
    print(f"\n✅ Discovered {len(node_map)} nodes")
    return node_map


async def main():
    # Connect to server
    client = OPCUAClient(server_url="opc.tcp://localhost:4840/freeopcua/server/")
    
    print("🔌 Connecting to manufacturing plant...")
    await client.connect()
    print("✅ Connected!\n")
    
    # Discover nodes automatically
    node_map = await discover_and_map_nodes(client)
    
    if not node_map:
        print("❌ No nodes discovered! Check server structure.")
        return
    
    print("\n" + "=" * 80)
    print("📡 Subscribing to discovered nodes...")
    print("=" * 80)
    
    # Subscribe to critical nodes
    critical_nodes = [
        'pump1_vibration',
        'pump2_vibration',  # CRITICAL - will fail!
        'pump2_temperature',  # CRITICAL - will fail!
        'line2_motor_temp',
        'quality_pass_rate',
    ]
    
    subscribed = []
    for name in critical_nodes:
        if name in node_map:
            try:
                node_id = node_map[name]
                await client.subscribe_to_node(node_id)
                subscribed.append((name, node_id))
                print(f"  ✓ Subscribed to {name}")
            except Exception as e:
                print(f"  ✗ Failed to subscribe to {name}: {e}")
    
    if not subscribed:
        print("❌ No subscriptions created!")
        return
    
    print(f"\n✅ Subscribed to {len(subscribed)} nodes")
    print("\n🎯 Streaming real-time data (Ctrl+C to stop)...")
    print("=" * 80)
    
    # Stream events
    event_count = 0
    values = {}
    
    try:
        async for event in client.stream():
            event_count += 1
            
            # Find the friendly name for this node
            friendly_name = None
            for name, node_id in subscribed:
                if node_id == event['node_id']:
                    friendly_name = name
                    break
            
            if friendly_name:
                value = event['value']
                timestamp = event['timestamp']
                values[friendly_name] = value
                
                # Show update
                print(f"[{event_count:4d}] {timestamp} | {friendly_name:25s} = {value:8.2f}")
                
                # Check for alerts
                if friendly_name == 'pump2_vibration' and value > 5.0:
                    print(f"       🚨 WARNING: Pump 2 vibration HIGH ({value:.2f} mm/s)")
                
                if friendly_name == 'pump2_temperature' and value > 70.0:
                    print(f"       🚨 WARNING: Pump 2 temperature HIGH ({value:.1f} °C)")
                
                # Summary every 20 events
                if event_count % 20 == 0:
                    print("\n📊 Current Status:")
                    for name, val in values.items():
                        print(f"   • {name:25s}: {val:8.2f}")
                    print("=" * 80)
    
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())