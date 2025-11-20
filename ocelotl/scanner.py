"""
Ocelotl v3.0 - Scanner Principal
Motor de escaneo optimizado con detección inteligente de secretos
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from .patterns import PatternManager
from .validators import SecretValidator, CredentialStrengthAnalyzer
from .utils import Logger, Spinner, FileHelper


class OcelotlScanner:
    """Scanner principal de Ocelotl con optimizaciones de performance"""
    
    # Tamaño máximo para lectura completa en memoria (10MB)
    MAX_FILE_SIZE_FULL_READ = 10 * 1024 * 1024
    
    def __init__(
        self,
        base_path: str,
        verbose: bool = False,
        use_colors: bool = True,
        exclude_dirs: Optional[set] = None,
        exclude_extensions: Optional[set] = None,
        min_confidence: str = 'LOW'
    ):
        """
        Inicializa el scanner
        
        Args:
            base_path: Ruta base a escanear
            verbose: Modo verbose
            use_colors: Usar colores en output
            exclude_dirs: Directorios a excluir
            exclude_extensions: Extensiones a excluir
            min_confidence: Nivel mínimo de confianza para reportar
        """
        self.base_path = Path(base_path)
        self.verbose = verbose
        self.min_confidence = min_confidence
        
        # Inicializar componentes
        from .utils import Colors
        self.colors = Colors(use_colors)
        self.logger = Logger(verbose, self.colors)
        self.pattern_manager = PatternManager()
        self.validator = SecretValidator()
        self.strength_analyzer = CredentialStrengthAnalyzer()
        
        # Configurar exclusiones
        self.exclude_dirs = exclude_dirs or {
            'node_modules', '.git', '__pycache__', 'venv', 'env',
            'vendor', 'build', 'dist', '.cache', '.idea', '.vscode',
            'target', 'bin', 'obj', '.next', '.nuxt', 'coverage'
        }
        
        self.exclude_extensions = exclude_extensions or set()
        
        # Obtener extensiones y patrones
        self.target_extensions = self.pattern_manager.get_target_extensions()
        self.compiled_patterns = self.pattern_manager.get_compiled_patterns()
        self.sensitive_file_patterns = self.pattern_manager.get_sensitive_file_patterns()
        
        # Resultados
        self.results = {
            'credentials': [],
            'admin_credentials': [],
            'passwords': [],
            'api_keys': [],
            'private_keys': [],
            'jwt_tokens': [],
            'config_files': [],
            'sensitive_files': [],
            'stats': {
                'files_scanned': 0,
                'matches_found': 0,
                'false_positives_filtered': 0,
                'start_time': datetime.now().isoformat(),
                'errors': 0
            }
        }
    
    def scan(self) -> Dict[str, Any]:
        """
        Ejecuta el escaneo completo
        
        Returns:
            Dict con resultados del escaneo
        """
        self.logger.info(f"Starting scan on: {self.base_path}")
        self.logger.info(f"Excluding directories: {', '.join(list(self.exclude_dirs)[:5])}...")
        
        # Buscar archivos sensibles por nombre
        self._scan_sensitive_files()
        
        # Escanear contenido de archivos
        self._scan_file_contents()
        
        # Finalizar
        self.results['stats']['end_time'] = datetime.now().isoformat()
        self.logger.success("Scan completed!")
        
        return self.results
    
    def _scan_sensitive_files(self):
        """Busca archivos sensibles por nombre"""
        self.logger.info("Scanning for sensitive files by name...")
        spinner = Spinner("Searching sensitive files", self.colors)
        spinner.start()
        
        sensitive_count = 0
        
        try:
            for file_path in self.base_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Verificar exclusiones
                if FileHelper.should_skip_path(file_path, self.exclude_dirs):
                    continue
                
                filename = file_path.name.lower()
                
                # Verificar patrones de archivos sensibles
                for pattern in self.sensitive_file_patterns:
                    if re.match(pattern, filename, re.IGNORECASE):
                        file_info = {
                            'type': 'sensitive_file',
                            'file': str(file_path),
                            'size': file_path.stat().st_size,
                            'size_formatted': FileHelper.format_file_size(file_path.stat().st_size),
                            'pattern_matched': pattern
                        }
                        self.results['sensitive_files'].append(file_info)
                        sensitive_count += 1
                        
                        if self.verbose:
                            self.logger.warning(f"Sensitive file: {file_path.name}")
                        
                        break
        finally:
            spinner.stop()
        
        self.logger.success(f"Found {sensitive_count} sensitive files")
    
    def _scan_file_contents(self):
        """Escanea el contenido de los archivos"""
        self.logger.info("Scanning file contents for secrets...")
        
        # Contar archivos totales
        total_files = sum(
            1 for f in self.base_path.rglob('*')
            if f.is_file() 
            and f.suffix.lower() in self.target_extensions
            and not FileHelper.should_skip_path(f, self.exclude_dirs)
        )
        
        self.logger.info(f"Estimated {total_files} files to scan")
        
        spinner = Spinner("Scanning files", self.colors)
        spinner.start()
        
        try:
            for file_path in self.base_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Verificar exclusiones
                if FileHelper.should_skip_path(file_path, self.exclude_dirs):
                    if self.verbose:
                        self.logger.debug(f"Skipping excluded: {file_path}")
                    continue
                
                # Verificar extensión
                if file_path.suffix.lower() not in self.target_extensions:
                    continue
                
                # Verificar si es binario
                if FileHelper.is_binary(file_path):
                    if self.verbose:
                        self.logger.debug(f"Skipping binary: {file_path}")
                    continue
                
                # Escanear archivo
                self._scan_single_file(file_path)
        finally:
            spinner.stop()
        
        self.logger.success(f"Scanned {self.results['stats']['files_scanned']} files")
        self.logger.info(f"Found {self.results['stats']['matches_found']} potential secrets")
        self.logger.info(f"Filtered {self.results['stats']['false_positives_filtered']} false positives")
    
    def _scan_single_file(self, file_path: Path):
        """
        Escanea un archivo individual
        
        Args:
            file_path: Ruta al archivo
        """
        self.results['stats']['files_scanned'] += 1
        
        try:
            file_size = file_path.stat().st_size
            
            # Elegir método de lectura según tamaño
            if file_size > self.MAX_FILE_SIZE_FULL_READ:
                matches = self._scan_file_streaming(file_path)
            else:
                matches = self._scan_file_full(file_path)
            
            # Procesar matches
            for match_data in matches:
                self._process_match(match_data)
                
        except Exception as e:
            self.results['stats']['errors'] += 1
            if self.verbose:
                self.logger.error(f"Error scanning {file_path}: {e}")
    
    def _scan_file_full(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Escanea archivo completo en memoria (para archivos pequeños)
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de matches encontrados
        """
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Buscar patrones
                for pattern_type, compiled_patterns in self.compiled_patterns.items():
                    for compiled_pattern in compiled_patterns:
                        for match in compiled_pattern.finditer(content):
                            line_number = content[:match.start()].count('\n') + 1
                            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                            
                            match_data = {
                                'type': pattern_type,
                                'match': match.group(),
                                'file': str(file_path),
                                'line': line_number,
                                'context': line_content.strip()[:300],
                                'full_match': match.groups()
                            }
                            
                            matches.append(match_data)
        except Exception as e:
            if self.verbose:
                self.logger.error(f"Error reading {file_path}: {e}")
        
        return matches
    
    def _scan_file_streaming(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Escanea archivo línea por línea (para archivos grandes)
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de matches encontrados
        """
        matches = []
        
        if self.verbose:
            self.logger.debug(f"Streaming large file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, 1):
                    # Buscar patrones en esta línea
                    for pattern_type, compiled_patterns in self.compiled_patterns.items():
                        for compiled_pattern in compiled_patterns:
                            for match in compiled_pattern.finditer(line):
                                match_data = {
                                    'type': pattern_type,
                                    'match': match.group(),
                                    'file': str(file_path),
                                    'line': line_number,
                                    'context': line.strip()[:300],
                                    'full_match': match.groups()
                                }
                                
                                matches.append(match_data)
        except Exception as e:
            if self.verbose:
                self.logger.error(f"Error streaming {file_path}: {e}")
        
        return matches
    
    def _process_match(self, match_data: Dict[str, Any]):
        """
        Procesa un match: valida, filtra falsos positivos y categoriza
        
        Args:
            match_data: Datos del match
        """
        # Validar match
        match_data = self.validator.validate_match(match_data)
        
        validation = match_data['validation']
        
        # Filtrar falsos positivos
        if validation['is_likely_false_positive']:
            self.results['stats']['false_positives_filtered'] += 1
            if self.verbose:
                self.logger.debug(
                    f"Filtered false positive in {match_data['file']}:{match_data['line']}"
                )
            return
        
        # Verificar nivel de confianza mínimo
        if not self.validator.should_report(match_data, self.min_confidence):
            if self.verbose:
                self.logger.debug(
                    f"Confidence too low ({validation['confidence']}) in {match_data['file']}:{match_data['line']}"
                )
            return
        
        # Incrementar contador
        self.results['stats']['matches_found'] += 1
        
        # Categorizar y agregar a resultados
        match_type = match_data['type']
        
        if match_type == 'admin_credentials':
            self.results['admin_credentials'].append(match_data)
            self.logger.critical(
                f"[CRITICAL] Admin credential in {match_data['file']}:{match_data['line']} "
                f"[{validation['confidence']}]"
            )
        elif match_type == 'passwords':
            self.results['passwords'].append(match_data)
            self.logger.critical(
                f"[CRITICAL] Password in {match_data['file']}:{match_data['line']} "
                f"[{validation['confidence']}]"
            )
        elif match_type == 'api_keys':
            self.results['api_keys'].append(match_data)
            self.logger.found(
                f"API Key/Token in {match_data['file']}:{match_data['line']} "
                f"[{validation['confidence']}]"
            )
        elif match_type == 'db_credentials':
            self.results['credentials'].append(match_data)
            self.logger.warning(
                f"DB Credential in {match_data['file']}:{match_data['line']} "
                f"[{validation['confidence']}]"
            )
        elif match_type == 'private_keys':
            self.results['private_keys'].append(match_data)
            self.logger.critical(
                f"[KEY] Private Key in {match_data['file']}:{match_data['line']}"
            )
        elif match_type == 'jwt_tokens':
            self.results['jwt_tokens'].append(match_data)
            self.logger.found(
                f"JWT Token in {match_data['file']}:{match_data['line']} "
                f"[{validation['confidence']}]"
            )
        else:
            self.results['config_files'].append(match_data)
            if self.verbose:
                self.logger.info(
                    f"Config pattern in {match_data['file']}:{match_data['line']}"
                )
