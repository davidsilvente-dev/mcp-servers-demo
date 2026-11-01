"""Pruebas sin red: usan una respuesta grabada del BOE (tests/fixtures)."""
import json
from pathlib import Path

import pytest

from mcp_boe import boe_client

FIXTURE = Path(__file__).parent / "fixtures" / "sumario_20261030.json"


@pytest.fixture
def datos():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parsear_sumario_aplana_items(datos):
    items = boe_client.parsear_sumario(datos)
    assert len(items) == 2
    assert items[0]["id"] == "BOE-A-2026-22716"
    assert items[0]["seccion"].startswith("I.")
    assert items[0]["url_pdf"].startswith("https://www.boe.es/")


def test_parsear_sumario_acepta_dict_en_vez_de_lista():
    dep = {"nombre": "X", "epigrafe": {"item": {"identificador": "A"}}}
    datos = {"data": {"sumario": {"diario": {"seccion": {"departamento": dep}}}}}
    assert [i["id"] for i in boe_client.parsear_sumario(datos)] == ["A"]


def test_parsear_sumario_formato_inesperado():
    with pytest.raises(boe_client.ErrorBOE):
        boe_client.parsear_sumario({"data": {}})


@pytest.mark.parametrize("fecha", ["2026-10-30", "abc", "20261332", "2026103"])
def test_validar_fecha_rechaza_formatos(fecha):
    with pytest.raises(boe_client.ErrorBOE):
        boe_client.validar_fecha(fecha)


def test_validar_fecha_vacia_es_hoy():
    assert len(boe_client.validar_fecha("")) == 8


def test_filtrar_sin_acentos_y_todas_las_palabras(datos):
    items = boe_client.parsear_sumario(datos)
    assert [i["id"] for i in boe_client.filtrar(items, "real decreto")] == ["BOE-A-2026-22716"]
    assert boe_client.filtrar(items, "RESOLUCION direccion")[0]["id"] == "BOE-A-2026-22721"
    assert boe_client.filtrar(items, "palabra-inexistente") == []


def test_filtrar_respeta_limite(datos):
    items = boe_client.parsear_sumario(datos)
    assert len(boe_client.filtrar(items, "de", limite=1)) == 1
    assert len(boe_client.filtrar(items, "de", limite=999)) <= 50


def test_filtrar_texto_vacio():
    with pytest.raises(boe_client.ErrorBOE):
        boe_client.filtrar([], "   ")


def test_fechas_recientes():
    assert boe_client.fechas_recientes(3, "20261101") == ["20261101", "20261031", "20261030"]
    assert len(boe_client.fechas_recientes(99, "20261101")) == 14


def test_descargar_json_solo_boe():
    with pytest.raises(boe_client.ErrorBOE):
        boe_client.descargar_json("https://example.com/x")


def test_sumario_usa_el_parseo(monkeypatch, datos):
    monkeypatch.setattr(boe_client, "descargar_json", lambda url: datos)
    assert len(boe_client.sumario("20261030")) == 2
