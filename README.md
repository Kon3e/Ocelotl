# 🐆 Ocelotl - Escaner de contenido

**Ocelotl** es una herramienta de análisis de contenido, diseñada para detectar credenciales expuestas, claves API, archivos sensibles y configuraciones inseguras dentro de archivos. Este script realiza un escaneo profundo de archivos con extensiones relevantes y genera un reporte detallado en formato JSON.

📦 Repositorio oficial: [https://github.com/Kon3e/Ocelotl.git]

- Detección de credenciales de base de datos (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.).
- Identificación de claves API y tokens de acceso ( Slack, etc.).
- Reconocimiento de archivos sensibles por nombre (`.env`, `wp-config.php`, `.bak`, `.sql`, etc.).
- Extracción de configuraciones relevantes (`AUTH_KEY`, `ftp_user`, etc.).
- Soporte para colores en consola y modo verbose.
- Generación de reportes en formato JSON.

## 🧰 Requisitos

- Python 3.8+
- Dependencias incluidas en `requirements.txt`

Instalación de dependencias:


pip install -r requirements.txt

USO :

python ocelotl.py <ruta> [-o reporte.json] [-v] [--no-color]

-v  Modo verbose, muestra todo el proceso.

-o  <archivo> Guarda el reporte en formato JSON.

--no-color  Desactiva colores en la salida.

--exclude-ext  Coma-separado: extensiones a excluir (ej: .log,.sql).

--exclude-path  Coma-separado: subdirectorios a excluir (ej: logs,tmp).

--help  Muestra el menú de ayuda.

EJEMPLO : python ocelotl.py "C:\\Documentos\\Carpeta" -o reporte.json -v --exclude-ext .log,.sql --exclude-path logs,tmp

======== MEJORAS =========

Mejoras Implementadas
Nuevos Patrones de Detección
Credenciales de Administrador[gitguardian +1]
•	Detecta usuarios admin, administrator, root, superuser con sus contraseñas
•	Identifica roles administrativos en JSON/configuraciones
•	Busca patrones específicos de WordPress admin
Contraseñas Mejoradas[blogs.jsmon]
•	Detección de passwords en múltiples formatos (JSON, XML, variables)
•	Reconoce hashes comunes: bcrypt, MD5, SHA1, SHA256
•	Captura contraseñas en contextos diversos
Connection Strings[github +1]
•	MongoDB, PostgreSQL, MySQL, Redis URIs completas
•	Detecta strings de conexión con credenciales embebidas
URLs Sensibles[blogs.jsmon]
•	IPs privadas (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
•	Dominios internos (.internal, .local, .dev, .staging)
•	Localhost y endpoints de desarrollo
Características Añadidas
Categorización Mejorada
•	Nueva categoría `admin_credentials` separada de credenciales normales
•	Categoría `passwords` independiente para contraseñas generales
•	Mejor organización en el reporte JSON
Alertas Visuales
•	Credenciales admin y passwords se marcan con 🔴 y nivel “CRITICAL”
•	Mayor visibilidad para hallazgos importantes
Archivos Sensibles Expandidos
•	Detecta archivos `.key`, `credentials`, `secrets`, `id_rsa`
•	Incluye archivos shadow, passwd, htpasswd

CASOS DE USO

El script ahora detecta efectivamente:
•	Credenciales hardcodeadas en código fuente
•	Tokens de servicios cloud (AWS, Azure, GCP)
•	API keys de servicios populares (Stripe, GitHub, Slack)
•	Contraseñas de bases de datos en archivos de configuración
•	Usuarios administrativos con sus credenciales
•	JWT tokens y Bearer tokens
•	Connection strings con credenciales
Los patrones están basados en colecciones de regex validadas por la comunidad de seguridad y cubren más de 100 tipos diferentes de secretos sensibles.

Este software está destinado exclusivamente para fines educativos y auditorías autorizadas. El uso en sistemas sin consentimiento explícito puede constituir una violación legal. El autor no se responsabiliza por el uso indebido de esta herramienta.
