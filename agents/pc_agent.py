from __future__ import annotations

import argparse
import asyncio
import platform
import socket
from typing import Any

import httpx


AGENT_VERSION = "0.1.0"


def local_capabilities() -> list[str]:
    """Capabilities this foundation can safely advertise before native adapters are installed."""
    return ["system.info"]


def system_info() -> dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
    }


async def run(base_url: str, device_id: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    hello = {
        "device_id": device_id,
        "agent_version": AGENT_VERSION,
        "system_type": "pc",
        "platform": platform.system().lower(),
        "capabilities": local_capabilities(),
    }
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=15) as client:
        response = await client.post("/api/v1/agents/hello", json=hello)
        response.raise_for_status()
        print(response.json())
        heartbeat = await client.post(f"/api/v1/agents/{device_id}/heartbeat")
        heartbeat.raise_for_status()
        print(heartbeat.json())
        print({"local_system_info": system_info()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S.-E.D.I.T.H. authorized PC agent")
    parser.add_argument("--server", required=True, help="J.A.R.V.I.S. server URL")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.server, args.device_id, args.token))
