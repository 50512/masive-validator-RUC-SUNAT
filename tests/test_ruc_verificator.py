import pytest

from massruc.ruc_utils import limpiar_ruc


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("10123456781", "10123456781"),  # Caso base
        (" 10123456781 ", "10123456781"),  # Con espacios
        ("10123456780", "10123456781"),  # Corregir digito verificador
        (10123456781, "10123456781"),  # Input número
    ],
)
def test_limpiar_ruc_exitoso(entrada, esperado):
    assert limpiar_ruc(entrada) == esperado


@pytest.mark.parametrize(
    "entrada_invalida",
    [
        ("1234567"),  # Corto
        ("1012345678i"),  # Letras
        ("10-12345678-1"),  # Guiones
        (""),  # Vacío
        (None),  # Nulo
    ],
)
def test_limpiar_ruc_fallido(entrada_invalida):
    assert limpiar_ruc(entrada_invalida) is None
