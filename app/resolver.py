import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path("data/stegtvc_config.json")


class StegTVCResolutionError(Exception):
    """Raised when StegTVC cannot resolve configuration."""
    pass


def load_config():
    if not CONFIG_PATH.exists():
        raise StegTVCResolutionError(
            f"Config file not found: {CONFIG_PATH}"
        )

    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        raise StegTVCResolutionError(f"Failed to read config: {e}")


def stegtvc_resolve(use_case: str, module: str, importance: str = "normal"):
    """
    Main resolver used by workflows & AI entities.
    """
    config = load_config()

    providers = config.get("providers", [])
    if not providers:
        raise StegTVCResolutionError("No providers defined in config.")

    # single pass priority selection
    for entry in providers:
        if (
            entry.get("use_case") == use_case
            and entry.get("module") == module
        ):
            return {
                "provider": entry.get("provider"),
                "model": entry.get("model"),
                "temperature": entry.get("temperature", 0.0),
                "max_tokens": entry.get("max_tokens", 1024),
                "importance": importance,
            }

    raise StegTVCResolutionError(
        f"No match found for use_case='{use_case}' module='{module}'"
    )


if __name__ == "__main__":
    # Manual CLI quick-test
    try:
        result = stegtvc_resolve(
            use_case="connectivity-check",
            module="hybrid-collab-bridge",
            importance="normal",
        )
        print("StegTVC Resolver OK:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
