"""
Ocelotl v3.0 - Advanced Security Scanner
Sistema avanzado de detección de credenciales y secretos expuestos

Author: EduSec
Repository: https://github.com/Kon3e/Ocelotl
"""

__version__ = '3.0.0'
__author__ = 'EduSec'

from .scanner import OcelotlScanner
from .patterns import PatternManager
from .validators import SecretValidator, CredentialStrengthAnalyzer
from .reporters import ReportGenerator
from .utils import Colors, Logger, Spinner, FileHelper

__all__ = [
    'OcelotlScanner',
    'PatternManager',
    'SecretValidator',
    'CredentialStrengthAnalyzer',
    'ReportGenerator',
    'Colors',
    'Logger',
    'Spinner',
    'FileHelper'
]
