"""
StegTVC Client – lightweight import layer for GitHub Actions.

Workflow example:
    from stegtvc_client import resolve

"""

from app.resolver import stegtvc_resolve as resolve

__all__ = ["resolve"]
