#!/usr/bin/env python3
"""
Ocelotl v3.0 - Advanced Security Scanner
Herramienta profesional para detectar credenciales, API keys y secretos expuestos

Usage:
    python ocelotl.py <path> [options]

Examples:
    python ocelotl.py /path/to/project
    python ocelotl.py /path/to/project -o report.json -v --html
    python ocelotl.py /path/to/project --exclude-dirs node_modules,vendor --min-confidence HIGH
"""

import sys
import argparse
from pathlib import Path

from ocelotl import OcelotlScanner, ReportGenerator
from ocelotl.utils import Colors, show_banner, show_help


def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Ocelotl v3.0 - Advanced Security Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocelotl.py /path/to/project
  python ocelotl.py /path/to/project -o report.json
  python ocelotl.py /path/to/project -v --html
  python ocelotl.py /path/to/project --exclude-dirs node_modules,vendor
  python ocelotl.py /path/to/project --min-confidence HIGH

For detailed help: python ocelotl.py --help-full
        """
    )
    
    # Argumento posicional
    parser.add_argument(
        'path',
        nargs='?',
        help='Path to directory to scan'
    )
    
    # Opciones de output
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Save report to JSON file'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML report (default: ocelotl_report.html)'
    )
    
    # Opciones de escaneo
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose mode (detailed output)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--min-confidence',
        choices=['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        default='LOW',
        help='Minimum confidence level to report (default: LOW)'
    )
    
    # Opciones de exclusión
    parser.add_argument(
        '--exclude-dirs',
        metavar='DIRS',
        help='Comma-separated directories to exclude (e.g., node_modules,.git,vendor)'
    )
    
    parser.add_argument(
        '--exclude-ext',
        metavar='EXTS',
        help='Comma-separated extensions to exclude (e.g., .log,.tmp)'
    )
    
    # Ayuda extendida
    parser.add_argument(
        '--help-full',
        action='store_true',
        help='Show detailed help with examples'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_arguments()
    
    # Inicializar colores
    colors = Colors(use_colors=not args.no_color)
    
    # Mostrar banner
    show_banner(colors)
    
    # Ayuda extendida
    if args.help_full:
        show_help(colors)
        return 0
    
    # Validar path
    if not args.path:
        print(f"{colors.RED}Error: Path argument is required{colors.RESET}")
        print(f"Use: python ocelotl.py <path> [options]")
        print(f"For help: python ocelotl.py --help-full")
        return 1
    
    if not Path(args.path).exists():
        print(f"{colors.RED}Error: Path '{args.path}' does not exist{colors.RESET}")
        return 1
    
    # Parsear exclusiones
    exclude_dirs = None
    if args.exclude_dirs:
        exclude_dirs = set(d.strip() for d in args.exclude_dirs.split(','))
    
    exclude_extensions = None
    if args.exclude_ext:
        exclude_extensions = set(e.strip() for e in args.exclude_ext.split(','))
    
    try:
        # Crear scanner
        scanner = OcelotlScanner(
            base_path=args.path,
            verbose=args.verbose,
            use_colors=not args.no_color,
            exclude_dirs=exclude_dirs,
            exclude_extensions=exclude_extensions,
            min_confidence=args.min_confidence
        )
        
        # Ejecutar escaneo
        results = scanner.scan()
        
        # Generar reportes
        reporter = ReportGenerator(results, colors)
        
        # Mostrar resumen en consola
        reporter.print_summary()
        
        # Guardar reporte JSON
        if args.output:
            if reporter.generate_json_report(args.output):
                print(f"{colors.GREEN}✓ JSON report saved to: {args.output}{colors.RESET}")
            else:
                print(f"{colors.RED}✖ Failed to save JSON report{colors.RESET}")
        
        # Generar reporte HTML
        if args.html:
            html_file = 'ocelotl_report.html'
            if reporter.generate_html_report(html_file):
                print(f"{colors.GREEN}✓ HTML report saved to: {html_file}{colors.RESET}")
            else:
                print(f"{colors.RED}✖ Failed to save HTML report{colors.RESET}")
        
        # Mensaje final
        critical_count = sum(
            1 for item in (results['admin_credentials'] + results['passwords'] + results['api_keys'])
            if item.get('validation', {}).get('confidence') in ['CRITICAL', 'HIGH']
        )
        
        if critical_count > 0:
            print(f"\n{colors.RED}{colors.BOLD}⚠️  WARNING: {critical_count} critical/high confidence findings detected!{colors.RESET}")
            print(f"{colors.YELLOW}   Please review and remediate these security issues.{colors.RESET}\n")
            return 2
        else:
            print(f"\n{colors.GREEN}✓ Scan completed successfully{colors.RESET}\n")
            return 0
            
    except KeyboardInterrupt:
        print(f"\n{colors.YELLOW}Scan interrupted by user{colors.RESET}")
        return 130
    except Exception as e:
        print(f"\n{colors.RED}Fatal error: {e}{colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
