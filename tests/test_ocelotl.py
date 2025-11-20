"""
Ocelotl v3.0 - Tests Unitarios
Suite de tests para validar funcionalidad
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from ocelotl import OcelotlScanner, SecretValidator


class TestSecretValidator(unittest.TestCase):
    """Tests para el validador de secretos"""
    
    def setUp(self):
        self.validator = SecretValidator()
    
    def test_entropy_calculation(self):
        """Test cálculo de entropía"""
        # Alta entropía (aleatorio)
        high_entropy = self.validator.calculate_entropy("aK9$mP2&xL5#nQ8@wR4")
        self.assertGreater(high_entropy, 4.0)
        
        # Baja entropía (repetitivo)
        low_entropy = self.validator.calculate_entropy("aaaaaaaaaa")
        self.assertLess(low_entropy, 1.0)
    
    def test_comment_detection(self):
        """Test detección de comentarios"""
        self.assertTrue(self.validator.is_comment("# password = 'test'"))
        self.assertTrue(self.validator.is_comment("// password = 'test'"))
        self.assertTrue(self.validator.is_comment("/* password = 'test' */"))
        self.assertFalse(self.validator.is_comment("password = 'test'"))
    
    def test_false_positive_keywords(self):
        """Test detección de keywords de falsos positivos"""
        self.assertTrue(self.validator.contains_false_positive_keyword("example_password"))
        self.assertTrue(self.validator.contains_false_positive_keyword("test123"))
        self.assertTrue(self.validator.contains_false_positive_keyword("changeme"))
        self.assertFalse(self.validator.contains_false_positive_keyword("MyRealP@ssw0rd"))
    
    def test_character_variety(self):
        """Test variedad de caracteres"""
        self.assertTrue(self.validator.has_character_variety("MyP@ssw0rd123"))
        self.assertFalse(self.validator.has_character_variety("password"))
        self.assertFalse(self.validator.has_character_variety("12345678"))


class TestOcelotlScanner(unittest.TestCase):
    """Tests para el scanner principal"""
    
    def setUp(self):
        """Crear directorio temporal para tests"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Limpiar archivos de test"""
        shutil.rmtree(self.test_dir)
    
    def create_test_file(self, filename: str, content: str):
        """Helper para crear archivos de test"""
        file_path = self.test_path / filename
        file_path.write_text(content)
        return file_path
    
    def test_detect_aws_key(self):
        """Test detección de AWS keys"""
        self.create_test_file("config.py", 'AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False
        )
        results = scanner.scan()
        
        self.assertGreater(len(results['api_keys']), 0)
    
    def test_detect_password(self):
        """Test detección de contraseñas"""
        self.create_test_file("config.php", 'define("DB_PASSWORD", "MySecureP@ssw0rd");')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False
        )
        results = scanner.scan()
        
        self.assertGreater(len(results['credentials']) + len(results['passwords']), 0)
    
    def test_detect_github_token(self):
        """Test detección de GitHub tokens"""
        self.create_test_file("env.txt", 'GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False
        )
        results = scanner.scan()
        
        self.assertGreater(len(results['api_keys']), 0)
    
    def test_exclude_directories(self):
        """Test exclusión de directorios"""
        # Crear directorio node_modules
        node_modules = self.test_path / 'node_modules'
        node_modules.mkdir()
        self.create_test_file("node_modules/config.js", 'password = "test123"')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False,
            exclude_dirs={'node_modules'}
        )
        results = scanner.scan()
        
        # No debería encontrar nada en node_modules
        for finding_list in results.values():
            if isinstance(finding_list, list):
                for finding in finding_list:
                    if isinstance(finding, dict) and 'file' in finding:
                        self.assertNotIn('node_modules', finding['file'])
    
    def test_false_positive_filtering(self):
        """Test filtrado de falsos positivos"""
        self.create_test_file("example.py", '''
# This is an example password
password = "example123"
# TODO: Change this password
test_password = "test123"
''')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False,
            min_confidence='MEDIUM'
        )
        results = scanner.scan()
        
        # Debería filtrar los ejemplos
        self.assertGreater(results['stats']['false_positives_filtered'], 0)
    
    def test_binary_file_skipping(self):
        """Test que se salten archivos binarios"""
        # Crear archivo binario
        binary_file = self.test_path / 'image.png'
        binary_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False
        )
        results = scanner.scan()
        
        # No debería haber escaneado el archivo binario
        self.assertEqual(results['stats']['files_scanned'], 0)
    
    def test_sensitive_file_detection(self):
        """Test detección de archivos sensibles"""
        self.create_test_file(".env", "DB_PASSWORD=secret")
        self.create_test_file("config.bak", "old config")
        
        scanner = OcelotlScanner(
            base_path=str(self.test_path),
            verbose=False,
            use_colors=False
        )
        results = scanner.scan()
        
        self.assertGreater(len(results['sensitive_files']), 0)


class TestPatterns(unittest.TestCase):
    """Tests para los patrones de detección"""
    
    def test_jwt_pattern(self):
        """Test detección de JWT tokens"""
        from ocelotl import PatternManager
        pm = PatternManager()
        
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        patterns = pm.get_compiled_patterns()
        jwt_patterns = patterns.get('jwt_tokens', [])
        
        matched = False
        for pattern in jwt_patterns:
            if pattern.search(jwt_token):
                matched = True
                break
        
        self.assertTrue(matched)
    
    def test_connection_string_pattern(self):
        """Test detección de connection strings"""
        from ocelotl import PatternManager
        pm = PatternManager()
        
        conn_strings = [
            "mongodb://user:pass@localhost:27017/db",
            "postgres://user:pass@localhost:5432/db",
            "mysql://user:pass@localhost:3306/db"
        ]
        
        patterns = pm.get_compiled_patterns()
        conn_patterns = patterns.get('connection_strings', [])
        
        for conn_str in conn_strings:
            matched = False
            for pattern in conn_patterns:
                if pattern.search(conn_str):
                    matched = True
                    break
            self.assertTrue(matched, f"Failed to match: {conn_str}")


def run_tests():
    """Ejecutar todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestSecretValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestOcelotlScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestPatterns))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
