from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI

# Initialize the DuckDB store
store = DuckDBStore()

# Initialize OpenAI client configured for Ollama
openai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama doesn't require real API key
)

# Wrap the client with observers
client = wrap_openai(openai_client, store=store)

# Create a completion
response = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[
        {"role": "user", "content": "What is Happiness?"}
    ]
)

print(response)