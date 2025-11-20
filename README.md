# 🐆 Ocelotl v3.0 - Advanced Security Scanner

<div align="center">

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

**Herramienta profesional para detectar credenciales expuestas, API keys y secretos en código fuente**

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Ejemplos](#-ejemplos) • [Documentación](#-documentación)

</div>

---

## 📋 Tabla de Contenidos

- [¿Qué es Ocelotl?](#-qué-es-ocelotl)
- [Características](#-características)
- [Novedades v3.0](#-novedades-v30)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Ejemplos](#-ejemplos)
- [Tipos de Secretos Detectados](#-tipos-de-secretos-detectados)
- [Sistema de Confianza](#-sistema-de-confianza)
- [Configuración Avanzada](#️-configuración-avanzada)
- [Reportes](#-reportes)
- [Casos de Uso](#-casos-de-uso)
- [Roadmap](#-roadmap)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Disclaimer](#️-disclaimer)

---

## 🎯 ¿Qué es Ocelotl?

**Ocelotl** (náhuatl: jaguar/ocelote) es un scanner de seguridad avanzado diseñado para identificar información sensible expuesta en código fuente, archivos de configuración y documentación. 

### ¿Por qué Ocelotl?

- ✅ **Sin dependencias externas** - Solo librerías estándar de Python
- ✅ **Detección inteligente** - Sistema de validación con cálculo de entropía
- ✅ **Reducción de falsos positivos** - Filtrado automático de casos comunes
- ✅ **Performance optimizado** - Manejo eficiente de archivos grandes
- ✅ **Reportes profesionales** - JSON y HTML interactivo
- ✅ **Fácil de usar** - Interfaz CLI intuitiva

---

## ✨ Características

### 🔍 Detección Avanzada

- **Credenciales de Base de Datos**
  - MySQL, PostgreSQL, MongoDB, Redis, MSSQL
  - Connection strings completas
  - Variables de entorno
  
- **Credenciales Administrativas**
  - Usuarios admin/root/superuser
  - WordPress admin credentials
  - Configuraciones de sistemas

- **API Keys & Tokens**
  - AWS (Access Keys, Secret Keys)
  - GitHub (Personal Access Tokens, OAuth)
  - Google Cloud (API Keys)
  - Slack (Bot Tokens, Webhooks)
  - Stripe (API Keys)
  - JWT Tokens
  - Bearer Tokens
  - +50 tipos de tokens más

- **Claves Privadas**
  - RSA Private Keys
  - SSH Keys (id_rsa, id_dsa, id_ecdsa)
  - PGP Private Keys
  - SSL/TLS Certificates

- **Archivos Sensibles**
  - `.env`, `config.php`, `wp-config.php`
  - Backups (`.bak`, `.sql`, `.dump`)
  - Logs con información sensible
  - Archivos de credenciales (`.aws/credentials`, `.npmrc`)

### 🧠 Validación Inteligente

- **Cálculo de Entropía de Shannon**
  - Determina aleatoriedad del secreto
  - Mayor entropía = mayor probabilidad de ser real

- **Filtrado de Falsos Positivos**
  - Detecta comentarios automáticamente
  - Identifica valores de ejemplo/test/demo
  - Reconoce declaraciones de variables vacías
  - Filtra contraseñas débiles comunes

- **Sistema de Confianza Multi-nivel**
  - CRITICAL: Alta entropía, alta probabilidad
  - HIGH: Buena entropía con variedad de caracteres
  - MEDIUM: Confianza moderada
  - LOW: Baja confianza pero posiblemente válido
  - VERY_LOW: Probablemente falso positivo

### ⚡ Performance

- **Escaneo Optimizado**
  - Pre-compilación de regex
  - Detección de archivos binarios
  - Lectura streaming para archivos grandes (>10MB)
  - Exclusión inteligente de directorios

- **Exclusiones por Defecto**
  - `node_modules`, `.git`, `__pycache__`
  - `venv`, `vendor`, `build`, `dist`
  - Configurable vía CLI

### 📊 Reportes

- **Consola Interactiva**
  - Colores y símbolos para fácil lectura
  - Resumen estadístico
  - Indicadores de criticidad

- **JSON Estructurado**
  - Formato estandarizado
  - Fácil integración con CI/CD
  - Incluye metadatos completos

- **HTML Interactivo**
  - Dashboard visual
  - Gráficos y estadísticas
  - Filtros por tipo y confianza
  - Responsivo y profesional

---

## 🎉 Novedades v3.0

### Arquitectura Modular
```
Ocelotl_v3/
├── ocelotl/
│   ├── __init__.py          # Package principal
│   ├── scanner.py           # Motor de escaneo
│   ├── patterns.py          # Patrones regex optimizados
│   ├── validators.py        # Sistema de validación
│   ├── reporters.py         # Generadores de reportes
│   └── utils.py             # Utilidades y UI
├── tests/                   # Tests unitarios
├── ocelotl.py              # CLI principal
├── requirements.txt
└── README.md
```

### Mejoras Técnicas

1. **Pre-compilación de Regex** (+300% velocidad)
2. **Sistema de Validación Avanzado**
3. **Streaming para Archivos Grandes**
4. **Exclusión Inteligente de Directorios**
5. **Reporte HTML Profesional**
6. **Sistema de Logging Mejorado**
7. **Manejo de Errores Robusto**

---

## 📦 Instalación

### Requisitos

- Python 3.8 o superior
- Sin dependencias externas

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/Kon3e/Ocelotl.git
cd Ocelotl

# Sin instalación de dependencias necesaria!
python ocelotl.py --help
```

### Instalación Global (Opcional)

```bash
# Hacer ejecutable
chmod +x ocelotl.py

# Crear symlink (Linux/Mac)
sudo ln -s $(pwd)/ocelotl.py /usr/local/bin/ocelotl

# Usar desde cualquier lugar
ocelotl /path/to/scan
```

---

## 🚀 Uso

### Sintaxis Básica

```bash
python ocelotl.py <path> [options]
```

### Opciones Disponibles

```
Argumentos:
  path                    Directorio a escanear

Opciones de Output:
  -o, --output FILE       Guardar reporte en JSON
  --html                  Generar reporte HTML

Opciones de Escaneo:
  -v, --verbose           Modo verbose (output detallado)
  --no-color              Desactivar colores
  --min-confidence LEVEL  Nivel mínimo de confianza
                          (VERY_LOW, LOW, MEDIUM, HIGH, CRITICAL)
                          Default: LOW

Exclusiones:
  --exclude-dirs DIRS     Directorios a excluir (separados por coma)
  --exclude-ext EXTS      Extensiones a excluir (separadas por coma)

Ayuda:
  -h, --help              Mostrar ayuda básica
  --help-full             Mostrar ayuda completa con ejemplos
```

---

## 💡 Ejemplos

### Escaneo Básico

```bash
# Escanear un proyecto
python ocelotl.py /path/to/project
```

### Con Reporte JSON

```bash
# Guardar resultados en JSON
python ocelotl.py /path/to/project -o security_report.json
```

### Modo Verbose + HTML

```bash
# Output detallado y reporte HTML
python ocelotl.py /path/to/project -v --html
```

### Filtrar por Confianza

```bash
# Solo mostrar hallazgos críticos y altos
python ocelotl.py /path/to/project --min-confidence HIGH
```

### Excluir Directorios

```bash
# Excluir node_modules y vendor
python ocelotl.py /path/to/project --exclude-dirs node_modules,vendor,build
```

### Escaneo de Producción

```bash
# Escaneo completo para CI/CD
python ocelotl.py /path/to/project \
  --min-confidence MEDIUM \
  --exclude-dirs node_modules,.git,vendor \
  -o report.json \
  --html
```

---

## 🔐 Tipos de Secretos Detectados

### Base de Datos

| Tipo | Ejemplos |
|------|----------|
| MySQL | `DB_PASSWORD`, `mysql://user:pass@host` |
| PostgreSQL | `postgres://user:pass@host/db` |
| MongoDB | `mongodb://user:pass@host:27017` |
| Redis | `redis://user:pass@host:6379` |
| MSSQL | `Server=...;Database=...;Password=...` |

### Cloud Providers

| Proveedor | Patrones |
|-----------|----------|
| AWS | `AKIA...`, Secret Access Keys |
| Google Cloud | `AIza...` |
| Azure | Varias claves y tokens |
| Heroku | API Keys |
| DigitalOcean | Personal Access Tokens |

### Servicios Populares

| Servicio | Tipos |
|----------|-------|
| GitHub | PAT, OAuth Tokens |
| Slack | Bot Tokens, Webhooks |
| Stripe | API Keys (live/test) |
| Twilio | Account SID, Auth Token |
| SendGrid | API Keys |
| MailChimp | API Keys |

### Otros

- JWT Tokens
- Bearer Tokens
- SSH Private Keys
- SSL/TLS Certificates
- API Keys Genéricos
- Contraseñas en código

---

## 🎯 Sistema de Confianza

Ocelotl utiliza múltiples factores para determinar la confianza:

### Niveles de Confianza

```
🔴 CRITICAL
   - Entropía > 4.5
   - Longitud suficiente (>16 caracteres)
   - Alta variedad de caracteres
   - Ejemplo: "aK9$mP2&xL5#nQ8@wR4"

🟣 HIGH
   - Entropía > 4.0
   - Buena variedad de caracteres
   - Ejemplo: "MyP@ssw0rd!2024"

🟡 MEDIUM
   - Entropía > 3.0
   - Variedad moderada
   - Ejemplo: "password123"

🔵 LOW
   - Entropía > 2.0
   - Poca variedad
   - Ejemplo: "admin"

⚪ VERY_LOW
   - Entropía baja
   - Probablemente falso positivo
   - Ejemplo: "example", "test123"
```

### Factores Considerados

1. **Entropía de Shannon** - Medida de aleatoriedad
2. **Longitud del secreto** - Mínimo 8 caracteres
3. **Variedad de caracteres** - Mayús, minús, números, especiales
4. **Contexto** - Comentarios, variables de ejemplo
5. **Palabras clave** - test, demo, example, sample

---

## ⚙️ Configuración Avanzada

### Crear Alias (Linux/Mac)

```bash
# Agregar a ~/.bashrc o ~/.zshrc
alias ocelotl='python /path/to/Ocelotl/ocelotl.py'

# Usar
ocelotl /path/to/scan -v --html
```

### Integración con Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
python ocelotl.py . --min-confidence HIGH -o /tmp/scan.json
if [ $? -eq 2 ]; then
    echo "❌ Security issues detected!"
    exit 1
fi
```

### Integración CI/CD (GitHub Actions)

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Ocelotl
        run: |
          git clone https://github.com/Kon3e/Ocelotl.git
          python Ocelotl/ocelotl.py . --min-confidence HIGH -o report.json
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: report.json
```

---

## 📈 Reportes

### Reporte de Consola

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                          OCELOTL                                          ║
║              🐆 Advanced Security Scanner & Secret Detector 🐆            ║
╚═══════════════════════════════════════════════════════════════════════════╝

✓ [SUCCESS] [12:34:56] Scan completed!

════════════════════════════════════════════════════════════════════════════
                        SCAN SUMMARY
════════════════════════════════════════════════════════════════════════════
⏱  Duration: 0:01:23
📂 Files Scanned: 1,234
🔍 Total Matches: 45
❌ Errors: 0

FINDINGS BY CONFIDENCE:
  ⚡ CRITICAL: 5
  ◆ HIGH:     8
  ⚠ MEDIUM:   12
  ℹ LOW:      15
  • VERY_LOW: 5

FINDINGS BY TYPE:
  👤 Admin Credentials: 3
  🔑 Passwords: 7
  🎫 API Keys/Tokens: 12
  🗄️  DB Credentials: 8
  📄 Sensitive Files: 15
════════════════════════════════════════════════════════════════════════════
```

### Reporte JSON

```json
{
  "metadata": {
    "tool": "Ocelotl",
    "version": "3.0",
    "scan_time": "2024-01-15T12:34:56",
    "duration": "0:01:23"
  },
  "summary": {
    "files_scanned": 1234,
    "matches_found": 45,
    "false_positives_filtered": 23
  },
  "findings": {
    "api_keys": [
      {
        "type": "api_keys",
        "match": "AKIA...",
        "file": "/path/to/config.py",
        "line": 42,
        "validation": {
          "confidence": "CRITICAL",
          "entropy": 4.8,
          "is_likely_false_positive": false
        }
      }
    ]
  }
}
```

### Reporte HTML

El reporte HTML incluye:
- Dashboard interactivo con estadísticas
- Gráficos visuales
- Hallazgos organizados por tipo
- Badges de confianza con colores
- Responsivo para móviles
- Código con syntax highlighting

---

## 🎯 Casos de Uso

### 1. Auditoría de Seguridad

```bash
# Escaneo completo de un proyecto antes de deploy
python ocelotl.py /var/www/project \
  --min-confidence MEDIUM \
  -o audit_$(date +%Y%m%d).json \
  --html
```

### 2. Code Review

```bash
# Revisar un pull request
python ocelotl.py ./branch-feature \
  --min-confidence HIGH \
  -v
```

### 3. Limpieza de Repositorios

```bash
# Encontrar todos los secretos antes de hacer público un repo
python ocelotl.py . \
  --exclude-dirs .git,node_modules \
  -o secrets_to_remove.json
```

### 4. Compliance & Regulations

```bash
# Escaneo para cumplimiento (PCI-DSS, HIPAA, etc)
python ocelotl.py /app/src \
  --min-confidence CRITICAL \
  -o compliance_report.json
```

---

## 🗺️ Roadmap

### v3.1 (Próximo)
- [ ] Soporte para más cloud providers (Alibaba, IBM, Oracle)
- [ ] Detección de secrets en imágenes Docker
- [ ] Plugin para VSCode
- [ ] Base de datos de secretos conocidos

### v3.2
- [ ] Machine Learning para detección de patrones custom
- [ ] API REST para integración
- [ ] Dashboard web en tiempo real
- [ ] Modo diff (solo cambios recientes)

### v4.0
- [ ] Análisis de flujo de datos
- [ ] Detección de exposición indirecta
- [ ] Remediación automática
- [ ] Integración con vaults (HashiCorp, AWS Secrets Manager)

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

### Cómo Contribuir

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Áreas de Contribución

- 🐛 Reportar bugs
- 💡 Sugerir nuevas características
- 📝 Mejorar documentación
- 🔧 Agregar nuevos patrones de detección
- ✅ Escribir tests
- 🌍 Traducciones

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## ⚠️ Disclaimer

**IMPORTANTE: USO RESPONSABLE**

- ✅ **Permitido**: Auditorías de seguridad autorizadas
- ✅ **Permitido**: Análisis de tus propios proyectos
- ✅ **Permitido**: Investigación y educación

- ❌ **Prohibido**: Escaneo de sistemas sin autorización
- ❌ **Prohibido**: Uso malicioso o ilegal
- ❌ **Prohibido**: Violación de términos de servicio

**El autor no se responsabiliza por el uso indebido de esta herramienta.**

El uso no autorizado puede constituir una violación de leyes locales, nacionales e internacionales. Esta herramienta se proporciona "tal cual" sin garantías de ningún tipo.

---

## 📞 Contacto & Soporte

- **GitHub**: [@Kon3e](https://github.com/Kon3e)
- **Issues**: [GitHub Issues](https://github.com/Kon3e/Ocelotl/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Kon3e/Ocelotl/discussions)

---

<div align="center">

**Hecho con ❤️ por EduSec**

⭐ Si te gusta Ocelotl, dale una estrella en GitHub!

[⬆ Volver arriba](#-ocelotl-v30---advanced-security-scanner)

</div>
