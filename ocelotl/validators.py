"""
Ocelotl v3.0 - Validadores
Sistema de validación para filtrar falsos positivos y evaluar confiabilidad
"""

import math
import re
from collections import Counter
from typing import Dict, Any


class SecretValidator:
    """Validador para filtrar falsos positivos y evaluar confiabilidad de secretos"""
    
    def __init__(self):
        # Palabras que indican falsos positivos
        self.false_positive_keywords = {
            'example', 'sample', 'test', 'demo', 'placeholder', 'your_password',
            'changeme', '123456', 'password', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', 'dragon', 'master', 'sunshine', 'princess',
            'min_length', 'max_length', 'validation', 'validate', 'check',
            'xxxxx', '*****', 'xxxxxxxx', 'xxxxxxxxxxxxxxxx',
            'todo', 'fixme', 'hack', 'temp', 'temporary',
            'lorem', 'ipsum', 'dolor', 'dummy', 'fake'
        }
        
        # Patrones que indican comentarios
        self.comment_patterns = [
            r'^\s*#',           # Python, Ruby, Shell
            r'^\s*//',          # JavaScript, Java, C++
            r'^\s*/\*',         # Multiline comment start
            r'^\s*\*',          # Multiline comment middle
            r'^\s*<!--',        # HTML, XML
            r'^\s*--',          # SQL, Lua
            r'^\s*;',           # Assembly, INI
            r'^\s*%',           # LaTeX, Erlang
        ]
        
        self.compiled_comment_patterns = [
            re.compile(pattern) for pattern in self.comment_patterns
        ]
    
    def calculate_entropy(self, text: str) -> float:
        """
        Calcula la entropía de Shannon de un texto.
        Mayor entropía = mayor aleatoriedad = más probable que sea un secreto real
        
        Args:
            text: Texto a analizar
            
        Returns:
            float: Entropía calculada (0.0 - ~8.0)
        """
        if not text:
            return 0.0
        
        # Contar frecuencia de caracteres
        counter = Counter(text)
        length = float(len(text))
        
        # Calcular entropía
        entropy = -sum(
            (count / length) * math.log2(count / length)
            for count in counter.values()
        )
        
        return entropy
    
    def is_comment(self, context: str) -> bool:
        """
        Verifica si el match está en un comentario
        
        Args:
            context: Línea de contexto donde se encontró el match
            
        Returns:
            bool: True si está en un comentario
        """
        context_stripped = context.strip()
        
        for pattern in self.compiled_comment_patterns:
            if pattern.match(context_stripped):
                return True
        
        return False
    
    def contains_false_positive_keyword(self, text: str) -> bool:
        """
        Verifica si el texto contiene palabras clave de falsos positivos
        
        Args:
            text: Texto a verificar
            
        Returns:
            bool: True si contiene keywords de falsos positivos
        """
        text_lower = text.lower()
        
        for keyword in self.false_positive_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def is_variable_declaration(self, context: str) -> bool:
        """
        Detecta si es solo una declaración de variable sin valor real
        
        Args:
            context: Contexto de la línea
            
        Returns:
            bool: True si parece ser solo una declaración
        """
        # Patrones de declaraciones comunes
        declaration_patterns = [
            r'(const|let|var)\s+\w+\s*;',                    # JS sin valor
            r'(String|int|boolean)\s+\w+\s*;',               # Java sin valor
            r'^\s*\w+\s*:\s*str\s*$',                        # Python type hint
            r'^\s*(public|private|protected)?\s*\w+\s+\w+\s*;',  # Java/C# declaration
        ]
        
        for pattern in declaration_patterns:
            if re.search(pattern, context):
                return True
        
        return False
    
    def has_sufficient_length(self, text: str, min_length: int = 8) -> bool:
        """
        Verifica si el texto tiene longitud suficiente para ser un secreto real
        
        Args:
            text: Texto a verificar
            min_length: Longitud mínima requerida
            
        Returns:
            bool: True si cumple con la longitud mínima
        """
        # Limpiar comillas y espacios
        cleaned = text.strip('\'"').strip()
        return len(cleaned) >= min_length
    
    def has_character_variety(self, text: str) -> bool:
        """
        Verifica si el texto tiene variedad de caracteres
        (no es solo números, no es solo letras, etc.)
        
        Args:
            text: Texto a verificar
            
        Returns:
            bool: True si tiene buena variedad de caracteres
        """
        has_upper = any(c.isupper() for c in text)
        has_lower = any(c.islower() for c in text)
        has_digit = any(c.isdigit() for c in text)
        has_special = any(not c.isalnum() for c in text)
        
        # Al menos 2 tipos diferentes de caracteres
        variety_count = sum([has_upper, has_lower, has_digit, has_special])
        
        return variety_count >= 2
    
    def validate_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida un match y agrega información de confiabilidad
        
        Args:
            match_data: Diccionario con información del match
            
        Returns:
            Dict con información de validación agregada
        """
        match_text = match_data.get('match', '')
        context = match_data.get('context', '')
        
        # Calcular entropía
        entropy = self.calculate_entropy(match_text)
        
        # Verificar falsos positivos
        is_false_positive = False
        false_positive_reasons = []
        
        if self.is_comment(context):
            is_false_positive = True
            false_positive_reasons.append('in_comment')
        
        if self.contains_false_positive_keyword(match_text):
            is_false_positive = True
            false_positive_reasons.append('contains_test_keyword')
        
        if self.contains_false_positive_keyword(context):
            is_false_positive = True
            false_positive_reasons.append('context_has_test_keyword')
        
        if self.is_variable_declaration(context):
            is_false_positive = True
            false_positive_reasons.append('variable_declaration')
        
        # Determinar nivel de confianza
        confidence = self._calculate_confidence(
            entropy, 
            match_text, 
            is_false_positive
        )
        
        # Agregar información de validación
        match_data['validation'] = {
            'entropy': round(entropy, 2),
            'confidence': confidence,
            'is_likely_false_positive': is_false_positive,
            'false_positive_reasons': false_positive_reasons,
            'has_sufficient_length': self.has_sufficient_length(match_text),
            'has_character_variety': self.has_character_variety(match_text)
        }
        
        return match_data
    
    def _calculate_confidence(
        self, 
        entropy: float, 
        text: str, 
        is_false_positive: bool
    ) -> str:
        """
        Calcula el nivel de confianza basado en varios factores
        
        Args:
            entropy: Entropía calculada del texto
            text: Texto del match
            is_false_positive: Si fue marcado como falso positivo
            
        Returns:
            str: Nivel de confianza (CRITICAL, HIGH, MEDIUM, LOW, VERY_LOW)
        """
        if is_false_positive:
            return 'VERY_LOW'
        
        # Criterios para alta confianza
        has_good_length = len(text) >= 16
        has_variety = self.has_character_variety(text)
        
        # Clasificación por entropía y otros factores
        if entropy >= 4.5 and has_good_length:
            return 'CRITICAL'
        elif entropy >= 4.0 and has_variety:
            return 'HIGH'
        elif entropy >= 3.0:
            return 'MEDIUM'
        elif entropy >= 2.0:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def should_report(self, match_data: Dict[str, Any], min_confidence: str = 'LOW') -> bool:
        """
        Determina si un match debe ser reportado basado en el nivel de confianza mínimo
        
        Args:
            match_data: Datos del match con validación
            min_confidence: Nivel mínimo de confianza requerido
            
        Returns:
            bool: True si debe ser reportado
        """
        confidence_levels = {
            'VERY_LOW': 0,
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        
        validation = match_data.get('validation', {})
        match_confidence = validation.get('confidence', 'VERY_LOW')
        
        return confidence_levels.get(match_confidence, 0) >= confidence_levels.get(min_confidence, 1)


class CredentialStrengthAnalyzer:
    """Analiza la fortaleza de credenciales encontradas"""
    
    @staticmethod
    def analyze_password_strength(password: str) -> Dict[str, Any]:
        """
        Analiza la fortaleza de una contraseña
        
        Args:
            password: Contraseña a analizar
            
        Returns:
            Dict con análisis de fortaleza
        """
        analysis = {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'strength': 'unknown'
        }
        
        # Calcular score
        score = 0
        if analysis['length'] >= 8:
            score += 1
        if analysis['length'] >= 12:
            score += 1
        if analysis['has_uppercase']:
            score += 1
        if analysis['has_lowercase']:
            score += 1
        if analysis['has_digits']:
            score += 1
        if analysis['has_special']:
            score += 1
        
        # Determinar fortaleza
        if score <= 2:
            analysis['strength'] = 'weak'
        elif score <= 4:
            analysis['strength'] = 'medium'
        else:
            analysis['strength'] = 'strong'
        
        return analysis
