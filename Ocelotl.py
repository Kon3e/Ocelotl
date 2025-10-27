import os
import re
import sys
import json
import time
import argparse
import itertools
import threading
from datetime import datetime
from pathlib import Path

spinner_running = False

def spinner_task(message="Procesando..."):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if not spinner_running:
            break
        sys.stdout.write(f'\r{message} {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')

def show_logo():
    logo = r"""
       *******     ******  ******** **         *******   ********** **      
  **/////**   **////**/**///// /**        **/////** /////**/// /**      
 **     //** **    // /**      /**       **     //**    /**    /**      
/**      /**/**       /******* /**      /**      /**    /**    /**      
/**      /**/**       /**////  /**      /**      /**    /**    /**      
//**     ** //**    **/**      /**      //**     **     /**    /**      
 //*******   //****** /********/******** //*******      /**    /********
  ///////     //////  //////// ////////   ///////       //     //////// 

                Ocelotl - Escaner de contenido v2.0
                Github : https://github.com/Kon3e/Ocelotl.git
                    Autor: EduSec - Mejorado
    """
    print(logo)

def show_help():
    print("\nComandos disponibles:")
    print("  python ocelotl.py <ruta> [-o reporte.json] [-v] [--no-color]")
    print("\nOpciones:")
    print("  -v            Modo verbose, muestra todo el proceso")
    print("  -o <archivo>  Guarda el reporte en formato JSON")
    print("  --no-color    Desactiva colores en la salida")
    print("  --help        Muestra este menú de ayuda\n")

class UniversalScanner:
    def __init__(self, base_path, verbose=False, use_colors=True):
        self.base_path = Path(base_path)
        self.verbose = verbose
        self.results = {
            'credentials': [],
            'admin_credentials': [],
            'api_keys': [],
            'config_files': [],
            'sensitive_files': [],
            'passwords': [],
            'stats': {
                'files_scanned': 0,
                'matches_found': 0,
                'start_time': datetime.now().isoformat(),
                'errors': 0
            }
        }

        self.colors = {
            'red': '\033[91m' if use_colors else '',
            'green': '\033[92m' if use_colors else '',
            'yellow': '\033[93m' if use_colors else '',
            'blue': '\033[94m' if use_colors else '',
            'magenta': '\033[95m' if use_colors else '',
            'cyan': '\033[96m' if use_colors else '',
            'reset': '\033[0m' if use_colors else ''
        }

        # Patrones mejorados con más cobertura
        self.patterns = {
            'db_credentials': [
                r'(?i)(db|database)[_-]?(name|user|username|password|passwd|pwd|host|server)\s*[=:]\s*[\'"]([^\'"]{1,100})[\'"]',
                r'(?i)define\s*\(\s*[\'"]DB_(NAME|USER|PASSWORD|HOST)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(mysql|postgres|postgresql|mongodb|redis)[_-]?(user|username|password|passwd|pwd|host)\s*[=:]\s*[\'"]([^\'"]{1,100})[\'"]',
                r'(?i)DATABASE_URL\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)CONNECTION_STRING\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            ],
            'admin_credentials': [
                # Credenciales de admin específicas
                r'(?i)(admin|administrator|root|superuser)[_-]?(user|username|login|email)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                r'(?i)(admin|administrator|root|superuser)[_-]?(pass|password|passwd|pwd|secret)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                r'(?i)[\'"]admin[\'"]\s*[=:]\s*[{].*?[\'"]password[\'"].*?[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)wp[_-]?admin[_-]?(user|password)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                # Usuarios administrativos comunes
                r'(?i)(username|user|login|email)\s*[=:]\s*[\'"]?(admin|administrator|root|sa|sysadmin)[\'"]?',
                r'(?i)[\'"]role[\'"]?\s*[=:]\s*[\'"]?(admin|administrator|superuser)[\'"]?',
            ],
            'passwords': [
                # Contraseñas en general
                r'(?i)(password|passwd|pwd|pass|secret)[\'"]?\s*[=:]\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)[\'"]password[\'"]?\s*:\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)(user_password|user_pass|userPassword)\s*[=:]\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)<password>([^<]{4,100})</password>',
                # Contraseñas con hashes comunes
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"]\$2[ayb]\$\d+\$[./A-Za-z0-9]{53}[\'"]',  # bcrypt
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{32}[\'"]',  # MD5
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{40}[\'"]',  # SHA1
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{64}[\'"]',  # SHA256
            ],
            'api_keys': [
                # Tokens y API Keys específicos
                r'(?i)[\'"]?api[_-]?key[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-]{10,100})[\'"]',
                r'(?i)[\'"]?secret[_-]?key[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-]{10,100})[\'"]',
                r'(?i)[\'"]?access[_-]?token[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-.]{10,100})[\'"]',
                # AWS Keys
                r'AKIA[0-9A-Z]{16}',
                r'(?i)aws(.{0,20})?[\'"][0-9a-zA-Z\/+]{40}[\'"]',
                # GitHub Tokens
                r'gh[ops]_[0-9a-zA-Z]{36}',
                r'github_pat_[0-9a-zA-Z_]{20,}',
                # Google API
                r'AIza[0-9A-Za-z\-_]{35}',
                # Slack
                r'xox[baprs]-[a-zA-Z0-9-]{10,}',
                # Stripe
                r'(sk|pk)_live_[0-9a-zA-Z]{24}',
                # Bearer tokens
                r'Bearer\s+[a-zA-Z0-9\-_\.=]+',
                # JWT
                r'eyJ[A-Za-z0-9-_=]+?\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
                # Otros tokens comunes
                r'(?i)(token|auth|secret)[\'"]\s*:\s*[\'"]([a-zA-Z0-9_\-\.]{15,})[\'"]',
            ],
            'config_patterns': [
                r'\$table_prefix\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY)\s*,?\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)ftp[_-]?(user|pass|password|host)\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(client_secret|client_id|app_secret|app_id)\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)smtp[_-]?(user|password|host|port)\s*[=:]\s*[\'"]?([^\'"]+)[\'"]?',
                r'(?i)(encryption_key|secret_key_base)\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            ],
            'connection_strings': [
                # MongoDB
                r'mongodb(\+srv)?://[^\'"\s]+',
                # PostgreSQL
                r'postgres(ql)?://[^\'"\s]+',
                # MySQL
                r'mysql://[^\'"\s]+',
                # Redis
                r'redis://[^\'"\s]+',
            ],
            'sensitive_urls': [
                # URLs internas y privadas
                r'https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):\d{2,5}',
                r'https?://[a-z0-9\-]+(\.internal|\.local|\.dev|\.test|\.staging)[a-z\.]{2,}',
                r'\b(10\.\d{1,3}|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}',
            ]
        }

        self.target_extensions = {
            '.asp', '.aspx', '.bat', '.cfg', '.cfm', '.cgi', '.cmd', '.conf', '.config', '.crt', '.cs', '.csv',
            '.db', '.dump', '.env', '.htaccess', '.htm', '.html', '.ini', '.js', '.json', '.jsp', '.jspx', '.jsx',
            '.log', '.md', '.pem', '.php', '.pl', '.ps1', '.py', '.rb', '.sh', '.sql', '.sqlite', '.ts', '.tsx',
            '.txt', '.vb', '.xml', '.yaml', '.yml', '.properties', '.toml'
        }

    def log(self, message, level="info", color=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix_map = {
            "error": f"{self.colors['red']}[ERROR]{self.colors['reset']}",
            "warning": f"{self.colors['yellow']}[WARNING]{self.colors['reset']}",
            "success": f"{self.colors['green']}[SUCCESS]{self.colors['reset']}",
            "info": f"{self.colors['blue']}[INFO]{self.colors['reset']}",
            "found": f"{self.colors['magenta']}[FOUND]{self.colors['reset']}",
            "critical": f"{self.colors['red']}[CRITICAL]{self.colors['reset']}"
        }
        prefix = prefix_map.get(level, "[INFO]")
        if color and color in self.colors:
            message = f"{self.colors[color]}{message}{self.colors['reset']}"
        print(f"{prefix} [{timestamp}] {message}")
        sys.stdout.flush()

    def is_text_file(self, file_path: Path) -> bool:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' not in chunk
        except Exception as e:
            self.results['stats']['errors'] += 1
            if self.verbose:
                self.log(f"No se pudo verificar {file_path}: {e}", "error")
            return False

    def search_patterns_in_file(self, file_path: Path):
        matches = []
        if not self.is_text_file(file_path):
            return matches
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern_type, patterns in self.patterns.items():
                    for pattern in patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                            line_number = content[:match.start()].count('\n') + 1
                            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                            
                            match_data = {
                                'type': pattern_type,
                                'pattern': pattern,
                                'match': match.group(),
                                'file': str(file_path),
                                'line': line_number,
                                'context': line_content.strip()[:200],
                                'full_match': match.groups()
                            }
                            matches.append(match_data)
                            
                            # Log con nivel crítico para admin/passwords
                            if pattern_type in ['admin_credentials', 'passwords']:
                                self.log(f"🔴 {pattern_type.upper()} en {file_path}:{line_number}", "critical", "red")
                            else:
                                self.log(f"{pattern_type.upper()} en {file_path}:{line_number}", "found", "magenta")
                            
                            if self.verbose:
                                self.log(f"   Match: {match.group()[:100]}", "info")
                                
        except Exception as e:
            self.results['stats']['errors'] += 1
            if self.verbose:
                self.log(f"Error leyendo {file_path}: {e}", "error")
        return matches

    def find_sensitive_files(self):
        self.log("Buscando archivos sensibles por nombre...", "info")
        sensitive_files = []
        sensitive_patterns = [
            r'.*\.bak$', r'.*backup.*', r'.*~$', r'wp-config.*', r'config.*',
            r'\.env.*', r'configuration.*', r'.*\.log$', r'debug.*',
            r'.*\.sql$', r'.*\.dump$', r'.*\.db$', r'.*\.sqlite$', 
            r'.*\.pem$', r'.*\.crt$', r'.*\.key$', r'.*credentials.*',
            r'.*secrets.*', r'.*password.*', r'.*\.htpasswd$',
            r'id_rsa.*', r'id_dsa.*', r'.*shadow$', r'.*passwd$'
        ]
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                filename = file_path.name.lower()
                for pattern in sensitive_patterns:
                    if re.match(pattern, filename):
                        file_info = {
                            'type': 'sensitive_file',
                            'file': str(file_path),
                            'size': file_path.stat().st_size,
                            'pattern_matched': pattern
                        }
                        sensitive_files.append(file_info)
                        self.log(f"Archivo sensible: {file_path}", "warning", "yellow")
                        break
        
        self.log(f"Encontrados {len(sensitive_files)} archivos sensibles", "success")
        return sensitive_files

    def scan_directory(self):
        self.log(f"Iniciando escaneo en: {self.base_path}", "info")
        self.log(f"Extensiones objetivo: {', '.join(list(self.target_extensions)[:10])}...", "info")
        
        global spinner_running
        spinner_running = True
        spinner_thread = threading.Thread(target=spinner_task, args=("Escaneando archivos...",))
        spinner_thread.start()

        self.results['sensitive_files'] = self.find_sensitive_files()
        
        total_files = sum(1 for _ in self.base_path.rglob('*') 
                         if _.is_file() and _.suffix.lower() in self.target_extensions)
        self.log(f"Estimados {total_files} archivos a escanear", "info")
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.target_extensions:
                self.results['stats']['files_scanned'] += 1
                matches = self.search_patterns_in_file(file_path)
                
                if matches:
                    self.results['stats']['matches_found'] += len(matches)
                    for match in matches:
                        match_type = match['type']
                        if match_type == 'db_credentials':
                            self.results['credentials'].append(match)
                        elif match_type == 'admin_credentials':
                            self.results['admin_credentials'].append(match)
                        elif match_type == 'passwords':
                            self.results['passwords'].append(match)
                        elif match_type == 'api_keys':
                            self.results['api_keys'].append(match)
                        else:
                            self.results['config_files'].append(match)

        spinner_running = False
        spinner_thread.join()
        
        self.results['stats']['end_time'] = datetime.now().isoformat()
        self.log("Escaneo completado!", "success")
        return self.results

    def generate_report(self, output_file=None):
        report = {
            'scan_summary': self.results['stats'],
            'admin_credentials_found': self.results['admin_credentials'],
            'passwords_found': self.results['passwords'],
            'credentials_found': self.results['credentials'],
            'api_keys_found': self.results['api_keys'],
            'config_matches': self.results['config_files'],
            'sensitive_files': self.results['sensitive_files']
        }
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                self.log(f"Reporte guardado en: {output_file}", "success")
            except Exception as e:
                self.log(f"Error guardando reporte: {e}", "error")
        
        self.print_summary()
        return report

    def print_summary(self):
        start = datetime.fromisoformat(self.results['stats']['start_time'])
        end = datetime.fromisoformat(self.results['stats'].get('end_time', datetime.now().isoformat()))
        duration = end - start
        
        print("\n" + "="*60)
        print(f" {self.colors['cyan']}RESUMEN FINAL DEL ESCANEO{self.colors['reset']}")
        print("="*60)
        print(f"{self.colors['blue']}• Duración:{self.colors['reset']} {duration}")
        print(f"{self.colors['blue']}• Archivos escaneados:{self.colors['reset']} {self.results['stats']['files_scanned']}")
        print(f"{self.colors['blue']}• Coincidencias encontradas:{self.colors['reset']} {self.results['stats']['matches_found']}")
        print(f"{self.colors['blue']}• Errores:{self.colors['reset']} {self.results['stats']['errors']}")
        
        print(f"\n{self.colors['yellow']}HALLAZGOS IMPORTANTES:{self.colors['reset']}")
        print(f"{self.colors['red']}🔴 Credenciales Admin:{self.colors['reset']} {len(self.results['admin_credentials'])}")
        print(f"{self.colors['red']}🔴 Contraseñas:{self.colors['reset']} {len(self.results['passwords'])}")
        print(f"{self.colors['red']}• Credenciales DB:{self.colors['reset']} {len(self.results['credentials'])}")
        print(f"{self.colors['magenta']}• API Keys/Tokens:{self.colors['reset']} {len(self.results['api_keys'])}")
        print(f"{self.colors['yellow']}• Archivos sensibles:{self.colors['reset']} {len(self.results['sensitive_files'])}")
        print(f"{self.colors['blue']}• Configuraciones:{self.colors['reset']} {len(self.results['config_files'])}")
        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Ocelotl v2.0 - Escáner de Seguridad Universal')
    parser.add_argument('path', nargs='?', help='Ruta al directorio a escanear')
    parser.add_argument('-o', '--output', help='Archivo de salida para el reporte')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    parser.add_argument('--no-color', action='store_true', help='Desactivar colores')
    args = parser.parse_args()

    show_logo()

    if not args.path:
        show_help()
        return

    if not os.path.exists(args.path):
        print(f"[-] Error: La ruta {args.path} no existe")
        return

    scanner = UniversalScanner(args.path, verbose=args.verbose, use_colors=not args.no_color)
    scanner.scan_directory()
    scanner.generate_report(args.output)

if __name__ == "__main__":
    main()

