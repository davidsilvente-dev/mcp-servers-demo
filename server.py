"""Compatibilidad: ejecuta el servidor del paquete src/mcp_boe (python server.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from mcp_boe.server import main  # noqa: E402

if __name__ == "__main__":
    main()
