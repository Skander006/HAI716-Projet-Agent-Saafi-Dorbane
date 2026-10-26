from pathlib import Path
from deplacements.deplacements import calcul_chemin,aller_vers,deplacement,perception,update_memoire,initialiser_memoire,charger_appartement,creer_carte_memoire,meilleure_destination

# Dossier contenant les cartes utilisées pour les tests
DOSSIER_CARTES = Path(__file__).parent/"deplacement_cartes"
def initialiser_test(nom_fichier):
    chemin_fichier = DOSSIER_CARTES/nom_fichier
    assert chemin_fichier.is_file(),(f"Carte de test introuvable : {chemin_fichier}")
    appartement,hauteur,largeur,pos_robot,pos_residents,pos_dict,pos_armoire,grille = charger_appartement(str(chemin_fichier))
    memoire = creer_carte_memoire(hauteur, largeur)
    memoire = initialiser_memoire(memoire,pos_robot,pos_residents,pos_dict,pos_armoire)
    perception_robot = perception(grille, pos_robot)
    memoire = update_memoire(perception_robot,memoire,pos_robot)
    return memoire,pos_robot,pos_residents,pos_dict,pos_armoire,grille,str(chemin_fichier)

# TEST 1 : BFS - CHEMIN SIMPLE
def test_bfs_chemin_simple():
    memoire,pos_robot,pos_residents,pos_dict,pos_armoire,grille,chemin_fichier = initialiser_test("test_bfs_chemin_connu.json")
    depart = pos_robot
    cible = pos_residents[0]
    # Trouver une case adjacente au résident
    arrivee = meilleure_destination(memoire,depart,cible)
    assert arrivee is not None
    # Calculer le chemin vers cette case
    chemin = calcul_chemin(memoire,depart,arrivee)
    assert chemin is not None
    assert chemin[0] == depart
    assert chemin[-1] == arrivee
    # Le robot doit s'arrêter à une case du résident
    distance = (abs(arrivee[0] - cible[0])+ abs(arrivee[1] - cible[1]))
    assert distance == 1
    # Vérifier que le chemin ne traverse aucun obstacle connu
    for ligne, colonne in chemin:
        assert memoire[ligne][colonne] not in ["#", "A", "D", "P"]

# TEST 2 : BFS - REPLANIFICATION APRÈS DÉCOUVERTE D'UN MUR
def test_bfs_chemin_replanification():
    memoire,pos_robot,pos_residents,pos_dict,pos_armoire,grille,chemin_fichier= initialiser_test("test_replanification.json")
    depart = pos_robot
    cible = pos_residents[0]
    # Destination adjacente au résident
    arrivee = meilleure_destination(memoire,depart,cible)
    assert arrivee is not None
    # Premier chemin : le mur en [1, 3] est encore inconnu
    chemin = calcul_chemin(memoire,depart,arrivee)
    assert chemin is not None
    assert chemin[0] == depart
    assert chemin[-1] == arrivee
    assert [1, 3] in chemin
    # Le robot avance d'une case
    position_actuelle = deplacement(memoire,depart,chemin[1],)
    assert position_actuelle == chemin[1]
    # Il découvre son nouvel environnement
    perception_actuelle = perception(grille,position_actuelle,)
    memoire = update_memoire(perception_actuelle,memoire,position_actuelle,)
    # Vérifier que le mur a bien été découvert
    assert memoire[1][3] == "#"
    # Recalculer la meilleure destination
    nouvelle_arrivee = meilleure_destination(memoire,position_actuelle,cible,)
    assert nouvelle_arrivee is not None
    nouveau_chemin = calcul_chemin(memoire,position_actuelle, nouvelle_arrivee,)
    assert nouveau_chemin is not None
    assert nouveau_chemin[0] == position_actuelle
    assert nouveau_chemin[-1] == nouvelle_arrivee
    # Le nouveau chemin ne doit plus passer par le mur
    assert [1, 3] not in nouveau_chemin
# TEST 3 : DESTINATION INACCESSIBLE
def test_bfs_chemin_impossible():
    memoire,pos_robot,pos_residents, pos_dict,pos_armoire,grille,chemin_fichier = initialiser_test("test_bfs_inaccessible.json")
    cible = pos_residents[0]
    memoire_finale, position_finale = aller_vers(memoire,pos_robot,cible,chemin_fichier,)
    # Le robot doit signaler que la destination est inaccessible
    assert position_finale is None
    assert memoire_finale is not None

# TEST 4 : DÉPLACEMENT VISUEL DU ROBOT
def test_deplacement_robot():
    memoire = [
        ["#", "#", "#", "#", "#"],
        ["#", "R", ".", ".", "#"],
        ["#", ".", ".", ".", "#"],
        ["#", "#", "#", "#", "#"],
    ]
    position_depart = [1, 1]
    position_suivante = [1, 2]
    nouvelle_position = deplacement(
        memoire,
        position_depart,
        position_suivante,
    )
    # Vérifier la nouvelle position
    assert nouvelle_position == [1, 2]
    # L'ancienne position doit être libre
    assert memoire[1][1] == "."
    # La nouvelle position doit contenir R
    assert memoire[1][2] == "R"
    # Il ne doit rester qu'un seul R
    nombre_robots = sum(
        ligne.count("R")
        for ligne in memoire
    )

    assert nombre_robots == 1

# TEST 5 : MEILLEURE DESTINATION ADJACENTE
def test_meilleure_destination():
    memoire,pos_robot,pos_residents, pos_dict,pos_armoire,grille,chemin_fichier = initialiser_test("test_bfs_inaccessible.json")
    depart = [1, 1]
    cible = [2, 3]
    destination = meilleure_destination(memoire,depart,cible,)
    assert destination is not None
    # Le robot doit choisir la case [1, 3]
    # qui est l'une des destinations les plus proches
    assert destination == [1, 3]
    # La destination doit être adjacente à l'armoire
    distance = (abs(destination[0] - cible[0])+ abs(destination[1] - cible[1]))
    assert distance == 1
    # Le robot ne doit pas entrer sur l'armoire
    assert destination != cible
