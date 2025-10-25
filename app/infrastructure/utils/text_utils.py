"""Utilidades para manejo de texto"""
import unicodedata


def normalizar_texto(texto: str) -> str:
    # Convertir a minúsculas
    texto = texto.lower()

    # Remover acentos
    # NFD = Normalización de Descomposición Canónica (separa caracteres base de diacríticos)
    texto_nfd = unicodedata.normalize('NFD', texto)

    # Filtrar solo caracteres que no sean marcas de combinación (acentos)
    texto_sin_acentos = ''.join(
        char for char in texto_nfd
        if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing_Mark (acentos)
    )

    return texto_sin_acentos