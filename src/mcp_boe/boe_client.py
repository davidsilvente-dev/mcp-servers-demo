"""Cliente mínimo de la API de datos abiertos del BOE (solo lectura, solo boe.es).

Sin dependencias externas: urllib de la biblioteca estándar. Las funciones de
parseo son puras para poder probarlas con respuestas grabadas (sin red).
"""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.request
from datetime import date, timedelta
from typing import Any

HOST_PERMITIDO = "https://www.boe.es/"
URL_SUMARIO = HOST_PERMITIDO + "datosabiertos/api/boe/sumario/{fecha}"
TIMEOUT_S = 10
TAMANO_MAX_BYTES = 5_000_000


class ErrorBOE(Exception):
    """Error controlado al consultar el BOE (fecha inválida, red, formato)."""


def validar_fecha(fecha: str | None) -> str:
    """Devuelve la fecha como AAAAMMDD; vacía = hoy. Lanza ErrorBOE si no es válida."""
    if not fecha:
        return date.today().strftime("%Y%m%d")
    if not (fecha.isdigit() and len(fecha) == 8):
        raise ErrorBOE("la fecha debe tener el formato AAAAMMDD")
    try:
        date(int(fecha[:4]), int(fecha[4:6]), int(fecha[6:]))
    except ValueError as e:
        raise ErrorBOE(f"fecha inválida: {e}") from e
    return fecha


def descargar_json(url: str) -> dict[str, Any]:
    """Descarga JSON del BOE con allow-list de host, timeout y tamaño máximo."""
    if not url.startswith(HOST_PERMITIDO):
        raise ErrorBOE("solo se permiten URL de www.boe.es")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            datos = resp.read(TAMANO_MAX_BYTES + 1)
    except Exception as e:  # red, HTTP 4xx/5xx, timeout
        raise ErrorBOE(f"no se pudo consultar el BOE: {type(e).__name__}") from e
    if len(datos) > TAMANO_MAX_BYTES:
        raise ErrorBOE("respuesta demasiado grande")
    try:
        return json.loads(datos)
    except ValueError as e:
        raise ErrorBOE("la respuesta del BOE no es JSON válido") from e


def _lista(x: Any) -> list[Any]:
    """La API devuelve un dict cuando hay un solo elemento y una lista cuando hay varios."""
    if isinstance(x, dict):
        return [x]
    return list(x or [])


def parsear_sumario(datos: dict[str, Any]) -> list[dict[str, Any]]:
    """Aplana el sumario del BOE en una lista de disposiciones."""
    try:
        diarios = _lista(datos["data"]["sumario"]["diario"])
    except (KeyError, TypeError) as e:
        raise ErrorBOE("formato de sumario inesperado") from e
    resultado: list[dict[str, Any]] = []
    for diario in diarios:
        for seccion in _lista(diario.get("seccion")):
            for dep in _lista(seccion.get("departamento")):
                for epi in _lista(dep.get("epigrafe")):
                    for item in _lista(epi.get("item")):
                        resultado.append(
                            {
                                "id": item.get("identificador"),
                                "titulo": item.get("titulo"),
                                "seccion": seccion.get("nombre"),
                                "departamento": dep.get("nombre"),
                                "epigrafe": epi.get("nombre"),
                                "url_pdf": (item.get("url_pdf") or {}).get("texto"),
                                "url_html": item.get("url_html"),
                            }
                        )
    return resultado


def sumario(fecha: str | None = None) -> list[dict[str, Any]]:
    """Disposiciones del sumario del BOE de una fecha (descarga + parseo)."""
    fecha = validar_fecha(fecha)
    return parsear_sumario(descargar_json(URL_SUMARIO.format(fecha=fecha)))


def _normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para buscar 'proteccion' y encontrar 'Protección'."""
    nfkd = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def filtrar(items: list[dict[str, Any]], texto: str, limite: int = 10) -> list[dict[str, Any]]:
    """Filtra disposiciones cuyo título contiene todas las palabras de `texto`."""
    palabras = [p for p in re.split(r"\s+", _normalizar(texto)) if p]
    if not palabras:
        raise ErrorBOE("indica al menos una palabra para buscar")
    limite = max(1, min(int(limite), 50))
    encontrados = [it for it in items if all(p in _normalizar(it.get("titulo") or "") for p in palabras)]
    return encontrados[:limite]


def fechas_recientes(dias: int, desde: str | None = None) -> list[str]:
    """Lista de fechas AAAAMMDD de los últimos `dias` días (incluida `desde`, hoy por defecto)."""
    dias = max(1, min(int(dias), 14))
    fin = validar_fecha(desde)
    f = date(int(fin[:4]), int(fin[4:6]), int(fin[6:]))
    return [(f - timedelta(days=i)).strftime("%Y%m%d") for i in range(dias)]
