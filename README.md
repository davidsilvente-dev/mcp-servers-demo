# mcp-servers-demo

Servidor MCP de ejemplo sobre datos abiertos del BOE. Hito 1 en curso (S2, nov. 2026).

## Estado
- `server.py`: herramienta `sumario_boe` (lee el sumario público del BOE). **Probado el 01/11/2026** con la API real (sumario del 30/10: 74 disposiciones) y por stdio con `test_stdio.py`. Requiere `mcp<2` (la v2 renombró `FastMCP`).

## Probar
```bash
pip install -r requirements.txt
python server.py
```
Con el inspector: `mcp dev server.py`.

## Pendiente (milestone 1)
1. Segunda herramienta (buscar por palabra en títulos) y prueba con `pytest`.
2. Migrar a MCP v2 (`MCPServer`) cuando el curso lo cubra.
3. Fijar versión en `requirements.txt` y añadir CI de GitHub Actions.
4. Enlazarlo desde el README del perfil cuando tenga la segunda herramienta y CI.

## Reglas
Solo datos públicos del BOE; sin nombres de clientes ni datos internos del Ayuntamiento.
