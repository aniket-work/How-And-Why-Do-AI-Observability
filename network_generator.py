from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI
from datetime import datetime
import random
import time
import duckdb

# Specify database path and static table name
DB_PATH = "network_events.db"
STATIC_TABLE_NAME = "network_events_log"

def generate_network_event():
    """Generate a simulated network event"""
    event_types = ["port_scan", "ddos", "normal_traffic", "data_exfiltration"]
    protocols = ["TCP", "UDP", "HTTP", "HTTPS"]

    event = {
        "event_type": random.choice(event_types),
        "timestamp": datetime.now().isoformat(),
        "source_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
        "destination_ip": f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
        "protocol": random.choice(protocols),
        "port": random.randint(1, 65535),
        "packet_size": random.randint(64, 1500),
        "frequency": random.randint(1, 1000)
    }

    # Set risk level based on event type
    if event["event_type"] in ["port_scan", "ddos"]:
        event["risk_level"] = "high"
    elif event["event_type"] == "data_exfiltration":
        event["risk_level"] = "medium"
    else:
        event["risk_level"] = "low"

    return event

def main():
    # Initialize the store with explicit database path
    store = DuckDBStore(path=DB_PATH)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    wrapped_client = wrap_openai(client, store=store)

    print(f"Starting network event generation... (Database: {DB_PATH})")
    print("Press Ctrl+C to stop")

    event_count = 0

    try:
        while True:
            # Generate event
            event = generate_network_event()

            # Create prompt for analysis
            prompt = f"""
            Analyze this network event:
            Event Type: {event['event_type']}
            Source IP: {event['source_ip']}
            Destination IP: {event['destination_ip']}
            Protocol: {event['protocol']}
            Port: {event['port']}
            Risk Level: {event['risk_level']}

            Provide a very brief security assessment.
            """

            try:
                # Get AI analysis
                response = wrapped_client.chat.completions.create(
                    model="llama3.2:3b",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                event_count += 1
                print(f"\rEvents generated and analyzed: {event_count}", end="")

            except Exception as e:
                print(f"\nError processing event: {e}")
                continue

            # Add small delay to avoid overwhelming the system
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped event generation.")
        print(f"Total events generated: {event_count}")


if __name__ == "__main__":
    main()
