# 🚀 Guía Rápida de Instalación - Ocelotl v3.0

## Instalación en 3 Pasos

### 1. Descargar
```bash
# Descargar el proyecto
cd ~/Downloads
unzip Ocelotl_v3.zip
cd Ocelotl_v3
```

### 2. Verificar Python
```bash
# Verificar versión de Python (necesitas 3.8+)
python --version
# o
python3 --version
```

### 3. ¡Usar!
```bash
# Sin instalación necesaria - sin dependencias externas
python ocelotl.py --help
```

## Primer Escaneo

```bash
# Escanear un proyecto
python ocelotl.py /path/to/your/project

# Con reporte JSON
python ocelotl.py /path/to/your/project -o report.json

# Con reporte HTML
python ocelotl.py /path/to/your/project --html
```

## Ejemplo Incluido

El proyecto incluye un `example_project/` con ejemplos de secretos:

```bash
# Probar con el ejemplo
python ocelotl.py example_project -v --html

# Ver el reporte generado
open ocelotl_report.html  # Mac
xdg-open ocelotl_report.html  # Linux
start ocelotl_report.html  # Windows
```

## Estructura del Proyecto

```
Ocelotl_v3/
├── ocelotl.py              # ← Ejecutar este archivo
├── ocelotl/                # Módulos internos
│   ├── scanner.py
│   ├── patterns.py
│   ├── validators.py
│   ├── reporters.py
│   └── utils.py
├── tests/                  # Tests unitarios
├── example_project/        # Proyecto de ejemplo
├── README.md              # Documentación completa
├── CHANGELOG.md           # Historial de cambios
├── LICENSE                # Licencia MIT
└── requirements.txt       # Sin dependencias!
```

## Comandos Útiles

### Escaneos Comunes

```bash
# Básico
python ocelotl.py /path/to/project

# Verbose (ver todo el proceso)
python ocelotl.py /path/to/project -v

# Solo hallazgos críticos
python ocelotl.py /path/to/project --min-confidence CRITICAL

# Excluir directorios
python ocelotl.py /path/to/project --exclude-dirs node_modules,vendor

# Completo (JSON + HTML)
python ocelotl.py /path/to/project -o scan.json --html -v
```

### Niveles de Confianza

- `CRITICAL` - Solo secretos con alta probabilidad de ser reales
- `HIGH` - Alta confianza
- `MEDIUM` - Confianza moderada (default)
- `LOW` - Incluye más resultados
- `VERY_LOW` - Incluye todo (muchos falsos positivos)

## Ejecutar Tests

```bash
# Ejecutar tests unitarios
python tests/test_ocelotl.py

# Ver resultados detallados
python tests/test_ocelotl.py -v
```

## Hacer Ejecutable (Linux/Mac)

```bash
# Hacer ejecutable
chmod +x ocelotl.py

# Agregar a PATH
echo 'alias ocelotl="python ~/Ocelotl_v3/ocelotl.py"' >> ~/.bashrc
source ~/.bashrc

# Usar desde cualquier lugar
ocelotl /path/to/scan
```

## Integración Git Hook

```bash
# Crear pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python /path/to/ocelotl.py . --min-confidence HIGH
if [ $? -eq 2 ]; then
    echo "❌ Secrets detected! Commit blocked."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

## Solución de Problemas

### Error: "python: command not found"
```bash
# Intenta con python3
python3 ocelotl.py --help
```

### Error: "No module named 'ocelotl'"
```bash
# Asegúrate de estar en el directorio correcto
cd Ocelotl_v3
python ocelotl.py --help
```

### Permisos en Linux/Mac
```bash
chmod +x ocelotl.py
```

## Próximos Pasos

1. Lee el `README.md` completo para documentación detallada
2. Revisa el `CHANGELOG.md` para ver todas las características
3. Ejecuta los tests para verificar la instalación
4. Escanea tu primer proyecto real
5. Revisa los reportes generados

## Soporte

- **Issues**: https://github.com/Kon3e/Ocelotl/issues
- **Documentación**: README.md
- **Ejemplos**: example_project/

## Tips Profesionales

✅ **Usa `--min-confidence HIGH` para producción** - Menos falsos positivos

✅ **Excluye `node_modules`, `vendor`, `.git`** - Mucho más rápido

✅ **Genera reporte HTML** - Más fácil de revisar visualmente

✅ **Integra en CI/CD** - Detecta secretos antes de deployment

✅ **Revisa periódicamente** - Escanea tu código regularmente

---

**¡Listo para usar! 🐆**

Para más información: `python ocelotl.py --help-full`
