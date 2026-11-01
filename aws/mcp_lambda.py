import json, urllib.request
from datetime import date

U = "https://www.boe.es/datosabiertos/api/boe/sumario/{}"
T = [{"name": "sumario_boe", "description": "Disposiciones del sumario del BOE de una fecha (AAAAMMDD; hoy por defecto).",
      "inputSchema": {"type": "object", "properties": {"fecha": {"type": "string"}}}}]


def L(x):
    return [x] if isinstance(x, dict) else (x or [])


def sumario(fecha):
    fecha = fecha or date.today().strftime("%Y%m%d")
    if not (fecha.isdigit() and len(fecha) == 8):
        raise ValueError("fecha debe ser AAAAMMDD")
    r = urllib.request.Request(U.format(fecha), headers={"Accept": "application/json"})
    d = json.load(urllib.request.urlopen(r, timeout=10))
    out = []
    for di in d["data"]["sumario"]["diario"]:
        for s in L(di.get("seccion")):
            for dep in L(s.get("departamento")):
                for e in L(dep.get("epigrafe")):
                    for i in L(e.get("item")):
                        out.append({"id": i.get("identificador"), "titulo": i.get("titulo"), "departamento": dep.get("nombre")})
    return {"fecha": fecha, "total": len(out), "items": out[:50]}


def rpc(m):
    k, p, i = m.get("method"), m.get("params") or {}, m.get("id")
    if i is None:
        return None
    ok = lambda r: {"jsonrpc": "2.0", "id": i, "result": r}
    if k == "initialize":
        return ok({"protocolVersion": p.get("protocolVersion", "2025-03-26"), "capabilities": {"tools": {}},
                   "serverInfo": {"name": "boe-demo", "version": "0.1.0"}})
    if k == "ping":
        return ok({})
    if k == "tools/list":
        return ok({"tools": T})
    if k == "tools/call":
        if p.get("name") != "sumario_boe":
            return {"jsonrpc": "2.0", "id": i, "error": {"code": -32602, "message": "herramienta desconocida"}}
        try:
            t = json.dumps(sumario((p.get("arguments") or {}).get("fecha")), ensure_ascii=False)
            return ok({"content": [{"type": "text", "text": t}]})
        except Exception as e:
            return ok({"content": [{"type": "text", "text": type(e).__name__ + ": " + str(e)}], "isError": True})
    return {"jsonrpc": "2.0", "id": i, "error": {"code": -32601, "message": "metodo no soportado"}}


def handler(event, context):
    if (event.get("requestContext", {}).get("http", {}).get("method")) != "POST":
        return {"statusCode": 405, "body": "usar POST"}
    try:
        m = json.loads(event.get("body") or "{}")
    except ValueError:
        return {"statusCode": 400, "body": "JSON no valido"}
    rs = [x for x in (rpc(q) for q in (m if isinstance(m, list) else [m])) if x]
    if not rs:
        return {"statusCode": 202, "body": ""}
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(rs if isinstance(m, list) else rs[0], ensure_ascii=False)}
