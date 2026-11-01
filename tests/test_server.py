"""Pruebas del servidor MCP en memoria (sin red, sin proceso aparte)."""
import json
from pathlib import Path

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from mcp_boe import boe_client, server

FIXTURE = Path(__file__).parent / "fixtures" / "sumario_20261030.json"


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    datos = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def falso(url):
        if "20261030" in url:
            return datos
        raise boe_client.ErrorBOE("no hay BOE")

    monkeypatch.setattr(boe_client, "descargar_json", falso)


@pytest.mark.anyio
async def test_lista_herramientas():
    async with create_connected_server_and_client_session(server.mcp._mcp_server) as cliente:
        nombres = {t.name for t in (await cliente.list_tools()).tools}
    assert nombres == {"sumario_boe", "buscar_boe"}


@pytest.mark.anyio
async def test_sumario_boe():
    async with create_connected_server_and_client_session(server.mcp._mcp_server) as cliente:
        res = await cliente.call_tool("sumario_boe", {"fecha": "20261030"})
    assert not res.isError
    assert len(res.content) == 2


@pytest.mark.anyio
async def test_buscar_boe_en_varios_dias():
    async with create_connected_server_and_client_session(server.mcp._mcp_server) as cliente:
        res = await cliente.call_tool("buscar_boe", {"texto": "resolucion", "dias": 3, "desde": "20261101"})
    assert not res.isError
    assert len(res.content) == 1
    assert json.loads(res.content[0].text)["fecha"] == "20261030"


@pytest.mark.anyio
async def test_error_controlado():
    async with create_connected_server_and_client_session(server.mcp._mcp_server) as cliente:
        res = await cliente.call_tool("sumario_boe", {"fecha": "mala"})
    assert "error" in json.loads(res.content[0].text)


def test_buscar_boe_directo():
    assert server.buscar_boe("real decreto", dias=2, desde="20261031")[0]["id"] == "BOE-A-2026-22716"
    assert server.buscar_boe("", dias=1, desde="20261030") == [{"error": "indica al menos una palabra para buscar"}]
