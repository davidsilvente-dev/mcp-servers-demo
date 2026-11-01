"""Servidor MCP de ejemplo sobre datos abiertos del BOE (borrador S2).

Solo lee la API pública de datos abiertos del BOE (sumario diario). Sin datos
personales ni de ninguna entidad. Ejecutar: python server.py (transporte stdio).
"""
import json
import urllib.request
from datetime import date

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("boe-demo")

BOE_SUMARIO = "https://www.boe.es/datosabiertos/api/boe/sumario/{fecha}"


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


@mcp.tool()
def sumario_boe(fecha: str = "") -> list[dict]:
    """Devuelve las disposiciones del sumario del BOE de una fecha (AAAAMMDD; hoy por defecto)."""
    fecha = fecha or date.today().strftime("%Y%m%d")
    datos = _get_json(BOE_SUMARIO.format(fecha=fecha))
    resultado = []
    for diario in datos["data"]["sumario"]["diario"]:
        for seccion in diario.get("seccion", []):
            departamentos = seccion.get("departamento", [])
            if isinstance(departamentos, dict):
                departamentos = [departamentos]
            for dep in departamentos:
                epigrafes = dep.get("epigrafe", [])
                if isinstance(epigrafes, dict):
                    epigrafes = [epigrafes]
                for epi in epigrafes:
                    items = epi.get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    for item in items:
                        resultado.append(
                            {
                                "id": item.get("identificador"),
                                "titulo": item.get("titulo"),
                                "departamento": dep.get("nombre"),
                                "url_pdf": (item.get("url_pdf") or {}).get("texto"),
                            }
                        )
    return resultado


if __name__ == "__main__":
    mcp.run()
