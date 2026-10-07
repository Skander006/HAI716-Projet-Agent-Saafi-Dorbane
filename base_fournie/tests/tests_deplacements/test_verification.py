import sys

sys.path.append("")

from deplacements import valider_carte
def test_fichier_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_invalide.json")
    assert resultat is False

def test_fichier_champs_manquants():
    resultat = valider_carte("tests/test_deplacements/verification_cartes/test_verification_champs_manquants.json")
    assert resultat is False

def test_fichier_format_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_format_inattendu.json")
    assert resultat is False

def test_fichier_version_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_version_inattendue.json")
    assert resultat is False

