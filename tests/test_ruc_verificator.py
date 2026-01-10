import pytest

from massruc.ruc_utils import limpiar_ruc


def test_ruc_valido_persona_natural():
    ruc_prueba = "10123456781"  # ruc estructuralmente válido

    res = True if limpiar_ruc(ruc_prueba) == ruc_prueba else False

    assert res is True
