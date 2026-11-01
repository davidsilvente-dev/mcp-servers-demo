# Seguridad

- El servidor es **solo lectura** y solo consulta `https://www.boe.es/` (allow-list de host).
- Timeout de 10 s y tamaño máximo de respuesta de 5 MB por petición.
- No hay secretos, credenciales ni datos personales en el repositorio.
- La versión en AWS (`aws/`) expone una URL de función con autenticación IAM: no es pública.

Si encuentras un problema de seguridad, escribe a david@davidsilvente.com en lugar de abrir un issue público.
