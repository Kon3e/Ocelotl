# 🐆 Ocelotl -

**Ocelotl** es una herramienta de análisis de seguridad web, diseñada para detectar credenciales expuestas, claves API, archivos sensibles y configuraciones inseguras dentro de directorios PATHS. Este script realiza un escaneo profundo de archivos con extensiones relevantes y genera un reporte detallado en formato JSON.

📦 Repositorio oficial: [https://github.com/Kon3e/Ocelotl.git](https://githubsticas

- Detección de credenciales de base de datos (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.).
- Identificación de claves API y tokens de acceso (Stripe, Google, GitHub, Slack, etc.).
- Reconocimiento de archivos sensibles por nombre (`.env`, `wp-config.php`, `.bak`, `.sql`, etc.).
- Extracción de configuraciones relevantes (`AUTH_KEY`, `ftp_user`, etc.).
- Soporte para colores en consola y modo verbose.
- Generación de reportes en formato JSON.
- Spinner animado durante el escaneo para mejorar la experiencia visual.

## 🧰 Requisitos

- Python 3.8+
- Dependencias incluidas en `requirements.txt`

Instalación de dependencias:


pip install -r requirements.txt

USO :

python ocelotl.py <ruta> [-o reporte.json] [-v] [--no-color]

-v : Modo verbose, muestra todo el proceso.
-o <archivo> : Guarda el reporte en formato JSON.
--no-color : Desactiva colores en la salida.
--help : Muestra el menú de ayuda.

Este software está destinado exclusivamente para fines educativos y auditorías autorizadas. El uso en sistemas sin consentimiento explícito puede constituir una violación legal. El autor no se responsabiliza por el uso indebido de esta herramienta.
