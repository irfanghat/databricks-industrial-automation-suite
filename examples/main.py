"""
Real-Time Monitoring with Alerts
=================================
Subscribe to critical equipment and trigger alerts when thresholds are exceeded.
"""

import asyncio
from datetime import datetime
from databricks_industrial_automation_suite.integrations.opcua import OPCUAClient


class PlantMonitor:
    """Real-time plant monitoring with alert system"""
    
    def __init__(self):
        self.thresholds = {
            "pump1_vibration": 5.0,      # mm/s - High vibration warning
            "pump2_vibration": 5.0,      # mm/s - High vibration warning
            "pump2_temperature": 70.0,   # °C - Temperature warning
            "line2_motor_temp": 85.0,    # °C - Motor overheating
            "quality_pass_rate": 96.0,   # % - Quality below target
        }
        
        self.alert_count = 0
        self.values = {}
        
    def check_alerts(self, name, value):
        """Check if value exceeds threshold"""
        if name in self.thresholds:
            threshold = self.thresholds[name]
            
            # For quality, alert if BELOW threshold
            if name == "quality_pass_rate":
                if value < threshold:
                    self.alert_count += 1
                    return f"🚨 ALERT {self.alert_count}: Quality rate {value:.1f}% below target {threshold}%"
            # For others, alert if ABOVE threshold
            else:
                if value > threshold:
                    self.alert_count += 1
                    return f"🚨 ALERT {self.alert_count}: {name} = {value:.2f} exceeds threshold {threshold}"
        
        return None
    
    def update_value(self, name, value):
        """Update stored value and calculate trends"""
        self.values[name] = value
    
    def get_summary(self):
        """Get current values summary"""
        return f"""
📊 Current Values:
  • Pump 1 Vibration: {self.values.get('pump1_vibration', 0):.2f} mm/s
  • Pump 2 Vibration: {self.values.get('pump2_vibration', 0):.2f} mm/s ⚠️
  • Pump 2 Temperature: {self.values.get('pump2_temperature', 0):.1f} °C
  • Line 2 Motor Temp: {self.values.get('line2_motor_temp', 0):.1f} °C
  • Quality Pass Rate: {self.values.get('quality_pass_rate', 0):.1f} %
  • Total Alerts: {self.alert_count}
"""


async def main():
    # Initialize client and monitor
    client = OPCUAClient(server_url="opc.tcp://localhost:4840/freeopcua/server/")
    monitor = PlantMonitor()
    
    print("🔌 Connecting to manufacturing plant...")
    await client.connect()
    print("✅ Connected!\n")
    
    # Map node IDs to meaningful names
    subscriptions = {
        "ns=2;i=25": "pump1_vibration",        # Pump 1 Vibration
        "ns=2;i=32": "pump2_vibration",        # Pump 2 Vibration (CRITICAL - will fail!)
        "ns=2;i=31": "pump2_temperature",      # Pump 2 Temperature
        "ns=2;i=11": "line2_motor_temp",       # Line 2 Motor Temperature
        "ns=2;i=42": "quality_pass_rate",      # Quality Pass Rate
    }
    
    print("📡 Subscribing to critical equipment...")
    for node_id, name in subscriptions.items():
        await client.subscribe_to_node(node_id)
        print(f"  ✓ {name}")
    
    print("\n🎯 Monitoring plant (Ctrl+C to stop)...")
    print("=" * 80)
    
    event_count = 0
    last_summary_time = datetime.now()
    
    async for event in client.stream():
        event_count += 1
        
        # Get the name for this node
        node_id = event['node_id']
        if node_id in subscriptions:
            name = subscriptions[node_id]
            value = event['value']
            timestamp = event['timestamp']
            
            # Update monitor
            monitor.update_value(name, value)
            
            # Check for alerts
            alert = monitor.check_alerts(name, value)
            
            if alert:
                print(f"\n{alert}")
                print(f"  Time: {timestamp}")
                print(f"  Node: {name}")
                print()
            
            # Print summary every 20 events
            if event_count % 20 == 0:
                print(monitor.get_summary())
                print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")