"""
Este archivo contiene ejemplos de código que NO deberían ser detectados
como secretos reales (falsos positivos)
"""

# Comentarios con ejemplos
# password = "example123"  <- Esto es solo un ejemplo
# API_KEY = "test_key_12345"  <- Esto es para testing

# Variables de ejemplo
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Documentación
"""
Para configurar la base de datos, use:
DB_PASSWORD = "your_password_here"
"""

# Valores de ejemplo
example_password = "example"
test_password = "test123"
demo_api_key = "demo_key_changeme"

# Variables sin valor
password = None
api_key = ""
secret_key: str

# Valores placeholder
REPLACE_WITH_YOUR_PASSWORD = "changeme"
TODO_ADD_REAL_PASSWORD = "placeholder"

# Constantes de validación
def validate_password(pwd):
    """
    Valida que una contraseña cumpla con:
    - Longitud mínima: 8 caracteres
    - Al menos una mayúscula
    - Al menos un número
    """
    if len(pwd) < PASSWORD_MIN_LENGTH:
        return False
    return True

# Configuración de ejemplo para desarrollo
if __name__ == "__main__":
    # Estos son solo para testing local
    dev_password = "test"
    dev_api_key = "xxx-xxx-xxx"
