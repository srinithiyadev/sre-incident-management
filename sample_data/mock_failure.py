import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api"

FAILURE_SCENARIOS = [
    {
        "name": "RDBMS Outage",
        "signals": [
            {
                "component_id":   "RDBMS_PRIMARY_01",
                "component_type": "RDBMS",
                "error_message":  "Connection timeout after 30s — primary DB unreachable",
                "severity":       "CRITICAL"
            }
        ] * 20
    },
    {
        "name": "MCP Host Failure",
        "signals": [
            {
                "component_id":   "MCP_HOST_01",
                "component_type": "API",
                "error_message":  "MCP Host not responding — circuit breaker open",
                "severity":       "CRITICAL"
            }
        ] * 15
    },
    {
        "name": "Cache Degradation",
        "signals": [
            {
                "component_id":   "CACHE_CLUSTER_01",
                "component_type": "CACHE",
                "error_message":  "Cache miss rate exceeded 90% — fallback to DB",
                "severity":       "ERROR"
            }
        ] * 10
    },
    {
        "name": "Queue Overflow",
        "signals": [
            {
                "component_id":   "MQ_BROKER_01",
                "component_type": "MQ",
                "error_message":  "Message queue depth exceeded 100k — consumers lagging",
                "severity":       "WARNING"
            }
        ] * 10
    }
]

async def send_signal(client, signal):
    try:
        res = await client.post(f"{BASE_URL}/signals", json=signal, timeout=5)
        return res.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

async def run_scenario(scenario):
    print(f"\n🚨 Simulating: {scenario['name']}")
    async with httpx.AsyncClient() as client:
        tasks = [send_signal(client, s) for s in scenario["signals"]]
        results = await asyncio.gather(*tasks)
        success = results.count(200)
        print(f"✅ Sent {len(results)} signals — {success} accepted")

async def main():
    print("=" * 50)
    print("  IMS Mock Failure Simulation")
    print("=" * 50)

    for scenario in FAILURE_SCENARIOS:
        await run_scenario(scenario)
        await asyncio.sleep(12)  # Wait > 10s debounce window

    print("\n✅ Simulation complete! Check dashboard at http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())
