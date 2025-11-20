"""
Ocelotl v3.0 - Patrones de Detección
Colección optimizada de patrones regex para detectar información sensible
"""

import re
from typing import Dict, List

class PatternManager:
    """Gestor de patrones regex con compilación optimizada"""
    
    def __init__(self):
        self.patterns = self._get_patterns()
        self.compiled_patterns = self._compile_patterns()
    
    def _get_patterns(self) -> Dict[str, List[str]]:
        """Retorna diccionario con todos los patrones organizados por categoría"""
        return {
            'db_credentials': [
                r'(?i)(db|database)[_-]?(name|user|username|password|passwd|pwd|host|server)\s*[=:]\s*[\'"]([^\'"]{1,100})[\'"]',
                r'(?i)define\s*\(\s*[\'"]DB_(NAME|USER|PASSWORD|HOST)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(mysql|postgres|postgresql|mongodb|redis)[_-]?(user|username|password|passwd|pwd|host)\s*[=:]\s*[\'"]([^\'"]{1,100})[\'"]',
                r'(?i)DATABASE_URL\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)CONNECTION_STRING\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)Server\s*=\s*[^;]+;\s*Database\s*=\s*[^;]+;\s*User\s+Id\s*=\s*[^;]+;\s*Password\s*=\s*[^;]+',
            ],
            
            'admin_credentials': [
                # Credenciales administrativas específicas
                r'(?i)(admin|administrator|root|superuser)[_-]?(user|username|login|email)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                r'(?i)(admin|administrator|root|superuser)[_-]?(pass|password|passwd|pwd|secret)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                r'(?i)[\'"]admin[\'"]\s*[=:]\s*\{.*?[\'"]password[\'"].*?[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)wp[_-]?admin[_-]?(user|password)\s*[=:]\s*[\'"]([^\'"]{2,100})[\'"]',
                r'(?i)(username|user|login|email)\s*[=:]\s*[\'"]?(admin|administrator|root|sa|sysadmin)[\'"]?',
                r'(?i)[\'"]role[\'"]?\s*[=:]\s*[\'"]?(admin|administrator|superuser|root)[\'"]?',
                r'(?i)ADMIN_PASSWORD\s*[=:]\s*[\'"]([^\'"]{4,100})[\'"]',
            ],
            
            'passwords': [
                # Contraseñas en diversos formatos
                r'(?i)(?<!_MIN)(?<!_MAX)(?<!_LENGTH)(password|passwd|pwd|pass|secret)[\'"]?\s*[=:]\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)[\'"]password[\'"]?\s*:\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)(user_password|user_pass|userPassword)\s*[=:]\s*[\'"]([^\'"]{4,100})[\'"]',
                r'(?i)<password>([^<]{4,100})</password>',
                # Hashes comunes
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"]\$2[ayb]\$\d+\$[./A-Za-z0-9]{53}[\'"]',  # bcrypt
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{32}[\'"]',  # MD5
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{40}[\'"]',  # SHA1
                r'(?i)(password|passwd|pwd)[\'"]?\s*[=:]\s*[\'"][a-f0-9]{64}[\'"]',  # SHA256
            ],
            
            'api_keys': [
                # Tokens y API Keys genéricos
                r'(?i)[\'"]?api[_-]?key[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-]{10,100})[\'"]',
                r'(?i)[\'"]?secret[_-]?key[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-]{10,100})[\'"]',
                r'(?i)[\'"]?access[_-]?token[\'"]?\s*[=:]\s*[\'"]([a-zA-Z0-9_\-.]{10,100})[\'"]',
                # AWS
                r'AKIA[0-9A-Z]{16}',
                r'(?i)aws(.{0,20})?[\'"][0-9a-zA-Z\/+]{40}[\'"]',
                # GitHub
                r'gh[ops]_[0-9a-zA-Z]{36}',
                r'github_pat_[0-9a-zA-Z_]{20,}',
                r'ghp_[a-zA-Z0-9]{36}',
                # Google
                r'AIza[0-9A-Za-z\-_]{35}',
                # Slack
                r'xox[baprs]-[a-zA-Z0-9-]{10,}',
                # Stripe
                r'(sk|pk)_(live|test)_[0-9a-zA-Z]{24,}',
                # Bearer tokens
                r'Bearer\s+[a-zA-Z0-9\-_\.=]+',
                # JWT
                r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
                # Heroku
                r'(?i)heroku(.{0,20})?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                # Azure
                r'(?i)(azure|az).{0,20}[a-z0-9/+=]{40,}',
                # Twilio
                r'SK[a-z0-9]{32}',
                # SendGrid
                r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
                # MailChimp
                r'[0-9a-f]{32}-us[0-9]{1,2}',
                # Generic tokens
                r'(?i)(token|auth|secret)[\'"]\s*:\s*[\'"]([a-zA-Z0-9_\-\.]{20,})[\'"]',
            ],
            
            'config_patterns': [
                r'\$table_prefix\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|SALT)\s*,?\s*[\'"]([^\'"]{10,})[\'"]',
                r'(?i)ftp[_-]?(user|pass|password|host)\s*=\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)(client_secret|client_id|app_secret|app_id)\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)smtp[_-]?(user|password|host|port)\s*[=:]\s*[\'"]?([^\'"]+)[\'"]?',
                r'(?i)(encryption_key|secret_key_base)\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
                r'(?i)PRIVATE[_-]?KEY\s*[=:]\s*[\'"]([^\'"]+)[\'"]',
            ],
            
            'connection_strings': [
                # MongoDB
                r'mongodb(\+srv)?://[^\s\'"\)]+',
                # PostgreSQL
                r'postgres(ql)?://[^\s\'"\)]+',
                # MySQL
                r'mysql://[^\s\'"\)]+',
                # Redis
                r'redis://[^\s\'"\)]+',
                # MSSQL
                r'(?i)Server\s*=.*?;.*?Database\s*=.*?;.*?Password\s*=.*?;',
            ],
            
            'sensitive_urls': [
                # URLs locales y privadas
                r'https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d{2,5})?',
                r'https?://[a-z0-9\-]+(\.internal|\.local|\.dev|\.test|\.staging)[a-z0-9\.\-/]*',
                r'\b(10\.\d{1,3}|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b',
            ],
            
            'private_keys': [
                # RSA private keys
                r'-----BEGIN RSA PRIVATE KEY-----',
                r'-----BEGIN PRIVATE KEY-----',
                r'-----BEGIN OPENSSH PRIVATE KEY-----',
                r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
            ],
            
            'jwt_tokens': [
                # JWT más específico
                r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            ]
        }
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Pre-compila todos los patrones para mejor performance"""
        compiled = {}
        for pattern_type, patterns in self.patterns.items():
            compiled[pattern_type] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in patterns
            ]
        return compiled
    
    def get_compiled_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Retorna patrones compilados"""
        return self.compiled_patterns
    
    def get_sensitive_file_patterns(self) -> List[str]:
        """Patrones para nombres de archivos sensibles"""
        return [
            r'.*\.bak$',
            r'.*backup.*',
            r'.*~$',
            r'wp-config.*',
            r'config\.php$',
            r'\.env.*',
            r'configuration.*',
            r'.*\.log$',
            r'debug.*',
            r'.*\.sql$',
            r'.*\.dump$',
            r'.*\.db$',
            r'.*\.sqlite$',
            r'.*\.pem$',
            r'.*\.crt$',
            r'.*\.key$',
            r'.*credentials.*',
            r'.*secrets.*',
            r'.*password.*',
            r'.*\.htpasswd$',
            r'id_rsa.*',
            r'id_dsa.*',
            r'id_ecdsa.*',
            r'.*shadow$',
            r'.*passwd$',
            r'\.aws/credentials',
            r'\.ssh/config',
            r'\.git/config',
            r'\.npmrc',
            r'\.pypirc',
        ]
    
    def get_target_extensions(self) -> set:
        """Extensiones de archivo a escanear"""
        return {
            # Web
            '.asp', '.aspx', '.html', '.htm', '.jsp', '.jspx', '.php',
            # Scripts
            '.sh', '.bash', '.ps1', '.bat', '.cmd',
            # Config
            '.cfg', '.conf', '.config', '.ini', '.env', '.yaml', '.yml', '.toml', '.properties',
            # Code
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.rb', '.go', '.rs',
            '.c', '.cpp', '.h', '.hpp', '.pl', '.pm',
            # Data
            '.json', '.xml', '.csv', '.sql', '.db', '.sqlite',
            # Docs
            '.txt', '.md', '.log',
            # Certificates
            '.pem', '.crt', '.key', '.cer', '.p12', '.pfx',
            # Other
            '.htaccess', '.htpasswd', '.gitignore', '.dockerignore'
        }
