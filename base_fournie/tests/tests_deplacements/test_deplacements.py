import sys
from ftplib import all_errors

sys.path.append("")

from deplacements import calcul_chemin, aller_vers, deplacement, perception, update_memoire, initialiser_memoire, charger_appartement, creer_carte_memoire, valider_carte

def test_bfs_chemin_simple():
    appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement("tests/tests_deplacements/deplacement_cartes/test_bfs_chemin_connu.json")
    memoire = creer_carte_memoire(hauteur, largeur)
    memoire = initialiser_memoire(memoire, pos_robot, pos_residents, pos_dict, pos_armoire)
    perception_robot = perception(grille, pos_robot)
    memoire = update_memoire(perception_robot, memoire, pos_robot)
    depart = pos_robot
    arrivee = pos_residents[0]
    chemin = calcul_chemin(memoire, depart, arrivee)
    assert chemin is not None
    assert len(chemin) -1 == 3
    assert chemin[-1] == arrivee
    assert chemin[0] == depart

def test_bfs_chemin_replanification():
    appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement("tests/tests_deplacements/deplacement_cartes/test_replanification.json")
    memoire = creer_carte_memoire(hauteur, largeur)
    memoire = initialiser_memoire(memoire, pos_robot, pos_residents, pos_dict, pos_armoire)
    perception_robot = perception(grille, pos_robot)
    memoire = update_memoire(perception_robot, memoire, pos_robot)
    depart = pos_robot
    arrivee = pos_residents[0]
    #Premier chemin calculé (le robot ne sait pas qu'il y'aura un mur en [1,3])
    chemin = calcul_chemin(memoire, depart, arrivee)
    assert chemin is not None
    assert chemin[-1] == arrivee
    assert chemin[0] == depart
    assert [1, 3] in chemin

    #Le robot avance
    position_actuelle = deplacement(pos_robot, chemin[1])
    perception_actuelle = perception(grille, position_actuelle)
    memoire = update_memoire(perception_actuelle, memoire, position_actuelle)
    #Le robot recalcule le chemin
    nouveau_chemin = calcul_chemin(memoire, position_actuelle, arrivee)
    assert nouveau_chemin is not None
    assert nouveau_chemin[0] == position_actuelle
    assert nouveau_chemin[-1] == arrivee
    assert [1, 3] not in nouveau_chemin

def test_bfs_chemin_impossible():
    appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement("tests/tests_deplacements/deplacement_cartes/test_bfs_inaccessible.json")
    memoire = creer_carte_memoire(hauteur, largeur)
    memoire = initialiser_memoire(memoire, pos_robot, pos_residents, pos_dict, pos_armoire)
    perception_robot = perception(grille, pos_robot)
    memoire = update_memoire(perception_robot, memoire, pos_robot)
    depart = pos_robot
    arrivee = pos_residents[0]
    parcours = aller_vers(memoire, depart, arrivee, "tests/tests_deplacements/deplacement_cartes/test_bfs_inaccessible.json")
    assert parcours is None
