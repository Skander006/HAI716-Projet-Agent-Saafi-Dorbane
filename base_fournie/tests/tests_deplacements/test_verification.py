import copy
import json
from validation.carte import valider_carte

DOSSIER = "tests/tests_deplacements/verification_cartes/"
BONNE_CARTE = json.load(open("cartes/appartement_01.json", encoding="utf-8"))

# La carte doit etre refusee avec le bon message d'erreur
# (on regarde le message : sinon un mauvais chemin de fichier ferait passer le test pour rien)
def refusee(capsys, chemin, morceau_du_message):
    assert valider_carte(chemin) is False
    erreur = capsys.readouterr().err
    assert "Erreur" in erreur
    assert morceau_du_message in erreur

# Ecrire une carte modifiee dans un fichier temporaire
def ecrire(tmp_path, carte):
    chemin = tmp_path / "carte.json"
    chemin.write_text(json.dumps(carte), encoding="utf-8")
    return str(chemin)

def test_fichier_invalide(capsys):
    refusee(capsys, DOSSIER + "test_validation_invalide.json", "JSON invalide")

def test_fichier_introuvable(capsys):
    refusee(capsys, DOSSIER + "cette_carte_n_existe_pas.json", "introuvable")

def test_fichier_champs_manquants(capsys):
    refusee(capsys, DOSSIER + "test_verification_champs_manquants.json", "obligatoire")

def test_fichier_format_invalide(capsys):
    refusee(capsys, DOSSIER + "test_validation_format_inattendu.json", "Format")

def test_fichier_version_invalide(capsys):
    refusee(capsys, DOSSIER + "test_validation_version_inattendue.json", "Version")

def test_fichier_dimensions_incoherente(capsys):
    refusee(capsys, DOSSIER + "test_validation_dimensions_incoherentes.json", "dimensions")

def test_fichier_contrainte_mur(capsys):
    refusee(capsys, DOSSIER + "test_validation_contrainte_murs.json", "murs")

def test_fichier_positions_hors_grille(capsys):
    refusee(capsys, DOSSIER + "test_validation_positions_hors_grille.json", "pas dans la grille")

def test_fichier_coherence_grille(capsys):
    refusee(capsys, DOSSIER + "test_validation_coherence_grille.json", "cohérente")

def test_fichier_symbole_inconnu(capsys):
    refusee(capsys, DOSSIER + "test_validation_symbole_inconnu.json", "symboles inconnus")

def test_fichier_verification_doublons_ID(capsys):
    refusee(capsys, DOSSIER + "test_validation_doublons_ID.json", "même ID")

def test_fichier_valide():
    assert valider_carte("cartes/appartement_01.json") is True

# Les cas ajoutes : avant, ils passaient (ou faisaient planter le programme)
def test_dimensions_pas_un_objet(tmp_path, capsys):
    carte = copy.deepcopy(BONNE_CARTE)
    carte["dimensions"] = 5
    refusee(capsys, ecrire(tmp_path, carte), "dimensions doit etre un objet")

def test_version_true(tmp_path, capsys):
    # en Python True vaut 1 : il faut quand meme le refuser
    carte = copy.deepcopy(BONNE_CARTE)
    carte["version"] = True
    refusee(capsys, ecrire(tmp_path, carte), "Version")

def test_deux_robots(tmp_path, capsys):
    carte = copy.deepcopy(BONNE_CARTE)
    carte["grille"][2] = carte["grille"][2].replace(".", "R", 1)
    refusee(capsys, ecrire(tmp_path, carte), "2 cases R")

def test_p_qui_n_est_aucun_resident(tmp_path, capsys):
    carte = copy.deepcopy(BONNE_CARTE)
    carte["grille"][2] = carte["grille"][2].replace(".", "P", 1)
    refusee(capsys, ecrire(tmp_path, carte), "aucun resident")

def test_resident_pas_un_objet(tmp_path, capsys):
    carte = copy.deepcopy(BONNE_CARTE)
    carte["residents"] = [5]
    refusee(capsys, ecrire(tmp_path, carte), "resident doit etre un objet")
