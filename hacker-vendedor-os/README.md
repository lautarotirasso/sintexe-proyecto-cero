# Hacker Vendedor OS — MVP

Sistema de investigación y CRM **local**, separado de la web SINTEXE. No envía mensajes ni postula automáticamente.

## Inicio
```bash
cd hacker-vendedor-os
python3 hv.py init
python3 hv.py import-csv ejemplos.csv
python3 hv.py report
python3 hv.py export
python3 -m unittest discover -s tests
```

Requiere Python 3.10+ y solo usa biblioteca estándar. Los CSV importados deben contener `nombre,empresa,cargo,pais,canal,fuente,fecha,oportunidad,prioridad,estado`. Se admite `email`, `telefono`, `url` como campos adicionales cuando sean **corporativos públicos y comprobados**. Los contactos sin fuente y canal no se importan. Los duplicados se detectan por canal y valor corroborado, o por combinación de empresa y nombre. Nunca se generan contactos falsos.

Los archivos SQLite y exportaciones se mantienen localmente y están excluidos de Git. El radar diario se configura por separado en ChatGPT; este repositorio **no ejecuta búsquedas por sí solo** y no tiene credenciales ni integración Drive activa.

## Próximos pasos
Conectar fuentes oficiales de vacantes y eventos, importar historial Drive de forma autorizada, agregar scoring, cola de revisión y sincronización Drive con verificación posterior. Evitar scraping contrario a términos de servicio. No almacenar datos privados.
