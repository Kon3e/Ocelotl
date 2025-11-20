"""
Ocelotl v3.0 - Utilidades
Funciones auxiliares para UI, logging y manejo de archivos
"""

import sys
import time
import itertools
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional


class Colors:
    """Códigos ANSI para colores en terminal"""
    
    def __init__(self, use_colors: bool = True):
        self.enabled = use_colors
        
        if use_colors:
            self.RED = '\033[91m'
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
            self.BLUE = '\033[94m'
            self.MAGENTA = '\033[95m'
            self.CYAN = '\033[96m'
            self.WHITE = '\033[97m'
            self.BOLD = '\033[1m'
            self.UNDERLINE = '\033[4m'
            self.RESET = '\033[0m'
            
            # Colores de fondo
            self.BG_RED = '\033[101m'
            self.BG_GREEN = '\033[102m'
            self.BG_YELLOW = '\033[103m'
            self.BG_BLUE = '\033[104m'
        else:
            # Sin colores
            self.RED = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.BLUE = ''
            self.MAGENTA = ''
            self.CYAN = ''
            self.WHITE = ''
            self.BOLD = ''
            self.UNDERLINE = ''
            self.RESET = ''
            self.BG_RED = ''
            self.BG_GREEN = ''
            self.BG_YELLOW = ''
            self.BG_BLUE = ''
    
    def colorize(self, text: str, color: str) -> str:
        """Aplica color a un texto"""
        if not self.enabled:
            return text
        
        color_code = getattr(self, color.upper(), '')
        return f"{color_code}{text}{self.RESET}"


class Spinner:
    """Spinner animado para indicar progreso"""
    
    def __init__(self, message: str = "Procesando", colors: Optional[Colors] = None):
        self.message = message
        self.running = False
        self.thread = None
        self.colors = colors or Colors()
    
    def _spin(self):
        """Función interna del spinner"""
        chars = ['|', '/', '-', '\\']
        idx = 0
        
        while self.running:
            char = chars[idx % len(chars)]
            msg = f"\r{self.colors.CYAN}[{char}]{self.colors.RESET} {self.message}"
            sys.stdout.write(msg)
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
        
        # Limpiar línea
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
    
    def start(self):
        """Inicia el spinner"""
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Detiene el spinner"""
        self.running = False
        if self.thread:
            self.thread.join()


class Logger:
    """Sistema de logging mejorado"""
    
    def __init__(self, verbose: bool = False, colors: Optional[Colors] = None):
        self.verbose = verbose
        self.colors = colors or Colors()
        self.start_time = datetime.now()
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp formateado"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _format_message(self, level: str, message: str, color: Optional[str] = None) -> str:
        """Formatea un mensaje de log"""
        timestamp = self._get_timestamp()
        
        # Mapeo de niveles a símbolos y colores
        level_map = {
            'error': ('X', 'RED'),
            'warning': ('!', 'YELLOW'),
            'success': ('+', 'GREEN'),
            'info': ('i', 'BLUE'),
            'found': ('*', 'MAGENTA'),
            'critical': ('!', 'RED'),
            'debug': ('>', 'CYAN')
        }
        
        symbol, default_color = level_map.get(level.lower(), ('.', 'WHITE'))
        use_color = color or default_color
        
        level_tag = self.colors.colorize(f"[{level.upper()}]", use_color)
        symbol_colored = self.colors.colorize(symbol, use_color)
        
        return f"{symbol_colored} {level_tag} [{timestamp}] {message}"
    
    def log(self, message: str, level: str = 'info', color: Optional[str] = None):
        """Registra un mensaje"""
        formatted = self._format_message(level, message, color)
        print(formatted)
        sys.stdout.flush()
    
    def error(self, message: str):
        """Log de error"""
        self.log(message, 'error')
    
    def warning(self, message: str):
        """Log de advertencia"""
        self.log(message, 'warning')
    
    def success(self, message: str):
        """Log de éxito"""
        self.log(message, 'success')
    
    def info(self, message: str):
        """Log informativo"""
        self.log(message, 'info')
    
    def found(self, message: str):
        """Log de hallazgo"""
        self.log(message, 'found')
    
    def critical(self, message: str):
        """Log crítico"""
        self.log(message, 'critical')
    
    def debug(self, message: str):
        """Log de debug (solo en modo verbose)"""
        if self.verbose:
            self.log(message, 'debug')
    
    def get_elapsed_time(self) -> str:
        """Obtiene tiempo transcurrido desde el inicio"""
        elapsed = datetime.now() - self.start_time
        return str(elapsed).split('.')[0]  # Sin microsegundos


class FileHelper:
    """Utilidades para manejo de archivos"""
    
    @staticmethod
    def is_binary(file_path: Path) -> bool:
        """
        Verifica si un archivo es binario
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            bool: True si es binario
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)  # Leer primeros 8KB
                return b'\0' in chunk
        except Exception:
            return True  # Asumir binario si hay error
    
    @staticmethod
    def get_file_size_mb(file_path: Path) -> float:
        """
        Obtiene el tamaño de un archivo en MB
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            float: Tamaño en MB
        """
        try:
            size_bytes = file_path.stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formatea tamaño de archivo en formato legible
        
        Args:
            size_bytes: Tamaño en bytes
            
        Returns:
            str: Tamaño formateado (ej: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def should_skip_path(path: Path, exclude_dirs: set) -> bool:
        """
        Verifica si un path debe ser ignorado
        
        Args:
            path: Ruta a verificar
            exclude_dirs: Set de directorios a excluir
            
        Returns:
            bool: True si debe ser ignorado
        """
        parts = path.parts
        return any(excluded in parts for excluded in exclude_dirs)


def show_banner(colors: Colors):
    """Muestra el banner de Ocelotl"""
    banner = f"""
{colors.CYAN}===============================================================================
                                                                           
   {colors.BOLD}{colors.YELLOW} ___   ____ _____ _     ___ _____ _     {colors.RESET}
   {colors.BOLD}{colors.YELLOW}/ _ \ / ___| ____| |   / _ \_   _| |    {colors.RESET}
   {colors.BOLD}{colors.YELLOW}| | | | |   |  _| | |  | | | || | | |    {colors.RESET}
   {colors.BOLD}{colors.YELLOW}| |_| | |___| |___| |__| |_| || | | |___ {colors.RESET}
   {colors.BOLD}{colors.YELLOW}\___/ \____|_____|_____\___/ |_| |_____|{colors.RESET}
                                                                           
              {colors.GREEN}Advanced Security Scanner & Secret Detector{colors.RESET}
                                                                           
                  {colors.WHITE}Version: {colors.GREEN}3.0{colors.WHITE} | Build: {colors.GREEN}Production{colors.RESET}
                  {colors.WHITE}Author: {colors.GREEN}EduSec{colors.WHITE} | {colors.BLUE}github.com/Kon3e/Ocelotl{colors.RESET}
                                                                           
{colors.CYAN}==============================================================================={colors.RESET}
"""
    print(banner)


def show_help(colors: Colors):
    """Muestra el menú de ayuda"""
    help_text = f"""
{colors.CYAN}{colors.BOLD}USAGE:{colors.RESET}
    python ocelotl.py <path> [options]

{colors.CYAN}{colors.BOLD}ARGUMENTS:{colors.RESET}
    {colors.GREEN}path{colors.RESET}                    Path to directory to scan

{colors.CYAN}{colors.BOLD}OPTIONS:{colors.RESET}
    {colors.GREEN}-o, --output{colors.RESET} FILE      Save report to JSON file
    {colors.GREEN}-v, --verbose{colors.RESET}          Enable verbose mode (detailed output)
    {colors.GREEN}--no-color{colors.RESET}             Disable colored output
    {colors.GREEN}--min-confidence{colors.RESET} LEVEL Set minimum confidence level (VERY_LOW, LOW, MEDIUM, HIGH, CRITICAL)
                               Default: LOW
    {colors.GREEN}--exclude-dirs{colors.RESET} DIRS   Comma-separated directories to exclude
                               Example: node_modules,.git,vendor
    {colors.GREEN}--exclude-ext{colors.RESET} EXTS    Comma-separated extensions to exclude
                               Example: .log,.tmp
    {colors.GREEN}--html{colors.RESET}                 Generate HTML report
    {colors.GREEN}-h, --help{colors.RESET}             Show this help message

{colors.CYAN}{colors.BOLD}EXAMPLES:{colors.RESET}
    {colors.YELLOW}# Basic scan{colors.RESET}
    python ocelotl.py /path/to/project

    {colors.YELLOW}# Scan with JSON output{colors.RESET}
    python ocelotl.py /path/to/project -o report.json

    {colors.YELLOW}# Verbose mode with HTML report{colors.RESET}
    python ocelotl.py /path/to/project -v --html

    {colors.YELLOW}# Exclude directories and filter by confidence{colors.RESET}
    python ocelotl.py /path/to/project --exclude-dirs node_modules,vendor --min-confidence HIGH

{colors.CYAN}{colors.BOLD}CONFIDENCE LEVELS:{colors.RESET}
    {colors.RED}CRITICAL{colors.RESET}    - High entropy secrets (very likely real)
    {colors.MAGENTA}HIGH{colors.RESET}        - Good entropy with variety
    {colors.YELLOW}MEDIUM{colors.RESET}      - Moderate confidence
    {colors.BLUE}LOW{colors.RESET}         - Low confidence but possibly valid
    {colors.WHITE}VERY_LOW{colors.RESET}    - Likely false positive

{colors.YELLOW}⚠  WARNING:{colors.RESET}
    This tool is for {colors.BOLD}authorized security audits only{colors.RESET}.
    Unauthorized use may violate laws and regulations.
"""
    print(help_text)


def format_duration(seconds: float) -> str:
    """
    Formatea duración en formato legible
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        str: Duración formateada
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
