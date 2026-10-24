"""Thin localhost HTTP controllers for DFD Studio."""

import logging

from vela.api import api

from apps.dfd.app import get_application

LOGGER = logging.getLogger(__name__)


def payload(context):
    obj = (context or {}).get("json") or {}
    if not isinstance(obj, dict):
        raise ValueError("Payload JSON deve ser um objeto.")
    return obj


def result(fn):
    try:
        return {"ok": True, "result": fn()}
    except (ValueError, KeyError, TypeError) as err:
        return {"ok": False, "error": str(err)}
    except Exception:
        LOGGER.exception("DFD application operation failed")
        return {"ok": False, "error": "Erro interno. Consulte o terminal para detalhes."}


def _service():
    return get_application().diagrams


@api.get("/dfd/example")
def example(context=None):
    return result(_service().example)


@api.get("/dfd/projects")
def projects(context=None):
    return result(_service().list_projects)


@api.post("/dfd/projects/load")
def load(context=None):
    return result(lambda: _service().load(payload(context)["name"]))


@api.post("/dfd/projects/save")
def save(context=None):
    data = payload(context)
    return result(lambda: _service().save(data["name"], data["diagram"]))


@api.post("/dfd/export")
def export(context=None):
    data = payload(context)
    return result(
        lambda: _service().export(
            data.get("name", "diagrama"), data["type"], data["diagram"]
        )
    )
