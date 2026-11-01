# mcp-servers-demo

Servidor MCP de ejemplo sobre datos abiertos del BOE. Hito 1 en curso (S2, nov. 2026).

## Estado
- `server.py`: herramienta `sumario_boe` (lee el sumario público del BOE). **Probado el 01/11/2026** con la API real (sumario del 30/10: 74 disposiciones) y por stdio con `test_stdio.py`. Requiere `mcp<2` (la v2 renombró `FastMCP`).

## Despliegue en AWS (Lambda)
La carpeta `aws/` contiene el mismo servidor como **MCP HTTP sin estado** en AWS Lambda, desplegado con CloudFormation:
- `aws/mcp_lambda.py`: código legible (JSON-RPC: `initialize`, `ping`, `tools/list`, `tools/call`; sin dependencias).
- `aws/boe-mcp.yaml`: plantilla (Lambda de 128 MB, logs a 7 días, URL de función con autenticación **IAM**; no es pública).

```bash
aws cloudformation deploy --template-file aws/boe-mcp.yaml --stack-name boe-mcp --capabilities CAPABILITY_IAM
aws cloudformation delete-stack --stack-name boe-mcp   # retirar todo
```
**Probado el 01/11/2026** en una cuenta de pruebas (eu-west-1) con peticiones firmadas con SigV4: `tools/list` y `tools/call` devolvieron el sumario del 30/10 (74 disposiciones); sin firma, la URL responde 403. Aún no probado con un cliente MCP completo (haría falta un proxy que firme con SigV4).

## Probar en local
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
