from deplacements.verification import valider_carte

def test_fichier_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_invalide.json")
    assert resultat is False

def test_fichier_champs_manquants():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_verification_champs_manquants.json")
    assert resultat is False

def test_fichier_format_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_format_inattendu.json")
    assert resultat is False

def test_fichier_version_invalide():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_version_inattendue.json")
    assert resultat is False

def test_fichier_dimensions_incoherente():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_dimensions_incoherentes.json")
    assert resultat is False

def test_fichier_contrainte_mur():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_contrainte_murs.json")
    assert resultat is False

def test_fichier_positions_hors_grille():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_positions_hors_grille.json")
    assert resultat is False

def test_fichier_coherence_grille():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_coherence_grille.json")
    assert resultat is False

def test_fichier_symbole_inconnu():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_symbole_inconnu.json")
    assert resultat is False

def test_fichier_verification_doublons_ID():
    resultat = valider_carte("tests/tests_deplacements/verification_cartes/test_validation_doublons_ID.json")
    assert resultat is False

def test_fichier_valide():
    resultat = valider_carte("cartes/appartement_01.json")
    assert resultat is True
