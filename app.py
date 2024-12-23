from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI
import json
from datetime import datetime


class NetworkAIMonitor:
    """
    AI-powered network monitoring system with observability.
    Analyzes network events and provides intelligent insights.
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        # Initialize DuckDB store for observability
        self.store = DuckDBStore()

        # Initialize Ollama client
        self.openai_client = OpenAI(
            base_url=base_url,
            api_key="ollama"
        )

        # Wrap client with observers
        self.client = wrap_openai(self.openai_client, store=self.store)

    def analyze_network_event(self, event_data: dict) -> dict:
        """
        Analyze a network event using AI and store observations.

        Args:
            event_data: Dictionary containing network event information

        Returns:
            AI analysis results
        """
        # Format the network event for AI analysis
        prompt = self._format_event_prompt(event_data)

        # Get AI analysis
        response = self.client.chat.completions.create(
            model="llama3.2:3b",
            messages=[
                {"role": "system",
                 "content": "You are a network security AI analyst specializing in anomaly detection."},
                {"role": "user", "content": prompt}
            ]
        )

        return {
            "event_id": event_data["event_id"],
            "timestamp": datetime.now().isoformat(),
            "analysis": response.choices[0].message.content,
            "model_used": "llama3.2:3b"
        }

    def _format_event_prompt(self, event_data: dict) -> str:
        """Format network event data into a prompt for AI analysis."""
        return f"""
Analyze this network event and identify any potential security concerns:

Event ID: {event_data['event_id']}
Timestamp: {event_data['timestamp']}
Source IP: {event_data['source_ip']}
Destination IP: {event_data['destination_ip']}
Protocol: {event_data['protocol']}
Port: {event_data['port']}
Packet Size: {event_data['packet_size']}
Frequency: {event_data['frequency']} packets/sec

Please provide:
1. Risk assessment
2. Potential threats
3. Recommended actions
"""


def main():
    # Initialize the monitor
    monitor = NetworkAIMonitor()

    # Example network event
    event_data = {
        "event_id": "NET-20241223-001",
        "timestamp": datetime.now().isoformat(),
        "source_ip": "192.168.1.100",
        "destination_ip": "203.0.113.45",
        "protocol": "TCP",
        "port": 445,
        "packet_size": 1500,
        "frequency": 1000
    }

    # Analyze the event
    result = monitor.analyze_network_event(event_data)
    print("\nAnalysis Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()