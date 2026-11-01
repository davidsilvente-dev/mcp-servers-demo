# mcp-servers-demo

Servidor MCP de ejemplo sobre datos abiertos del BOE. Borrador local (S2), **sin publicar**.

## Estado
- `server.py`: herramienta `sumario_boe` (lee el sumario público del BOE). **Probado el 01/11/2026** con la API real (sumario del 30/10: 74 disposiciones) y por stdio con `test_stdio.py`. Requiere `mcp<2` (la v2 renombró `FastMCP`).

## Probar (cuando David quiera)
```bash
pip install -r requirements.txt
python server.py
```
Con el inspector: `mcp dev server.py`.

## Pendiente (milestone 1)
1. Segunda herramienta (buscar por palabra en títulos) y prueba con `pytest`.
2. Migrar a MCP v2 (`MCPServer`) cuando el curso lo cubra.
3. Fijar versión en `requirements.txt` y añadir CI de GitHub Actions.
4. Publicar como `davidsilvente-dev/mcp-servers-demo` solo con OK de David.

## Reglas
Solo datos públicos del BOE; sin nombres de clientes ni datos internos del Ayuntamiento.
