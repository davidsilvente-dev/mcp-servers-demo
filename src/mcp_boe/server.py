"""Servidor MCP de demostración: expone el sumario del BOE como herramientas para un LLM.

Transporte stdio por defecto (`python -m mcp_boe.server`). Solo lectura, solo boe.es.
Requiere mcp 1.x (`mcp<2`); la v2 renombró FastMCP a MCPServer.
"""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import boe_client

mcp = FastMCP("boe-demo")


@mcp.tool()
def sumario_boe(fecha: str = "") -> list[dict[str, Any]]:
    """Devuelve las disposiciones del sumario del BOE de una fecha (AAAAMMDD; hoy por defecto)."""
    try:
        return boe_client.sumario(fecha)
    except boe_client.ErrorBOE as e:
        return [{"error": str(e)}]


@mcp.tool()
def buscar_boe(texto: str, dias: int = 1, desde: str = "", limite: int = 10) -> list[dict[str, Any]]:
    """Busca disposiciones del BOE cuyo título contenga todas las palabras de `texto`
    en los sumarios de los últimos `dias` días (máx. 14) contados desde `desde` (AAAAMMDD; hoy por defecto).
    Devuelve como mucho `limite` resultados (máx. 50). Los días sin BOE (domingos, festivos) se omiten."""
    try:
        encontrados: list[dict[str, Any]] = []
        for fecha in boe_client.fechas_recientes(dias, desde):
            try:
                items = boe_client.sumario(fecha)
            except boe_client.ErrorBOE:
                continue  # sin BOE ese día
            for it in boe_client.filtrar(items, texto, limite):
                encontrados.append({"fecha": fecha, **it})
            if len(encontrados) >= limite:
                break
        return encontrados[:limite]
    except boe_client.ErrorBOE as e:
        return [{"error": str(e)}]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
