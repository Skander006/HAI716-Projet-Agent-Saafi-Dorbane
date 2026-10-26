#Moteur de déplacement
import json
import sys
from math import *
from verification import valider_carte
#Chargement de l'appartement pour récuperer sa taille exacte
def charger_appartement(chemin):
    if not valider_carte(chemin):
        print("Erreur : Fichier de carte invalide", file=sys.stderr)
        sys.exit(1)
    with open(chemin, "r", encoding="utf-8") as fichier:
        appartement = json.load(fichier)
    hauteur = appartement["dimensions"]["hauteur"]
    largeur = appartement["dimensions"]["largeur"]
    pos_robot = appartement["depart_robot"]
    pos_residents = []
    for resident in appartement["residents"]:
        pos_residents.append(resident["position"])
    pos_dict = appartement["dictionnaire"]["position"]
    pos_armoire = appartement["armoire"]["position"]
    grille = appartement["grille"]
    return appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire, grille

#Creation de la carte memoire
def creer_carte_memoire(hauteur, largeur):
    carte = []
    for i in range(hauteur):
        ligne =[]
        for j in range(largeur):
            ligne.append("?")
        carte.append(ligne)
    return carte

#Initialisation de la carte memoire
def initialiser_memoire(carte, pos_robot, pos_residents, pos_dict, pos_armoire):
    carte[pos_robot[0]][pos_robot[1]] = 'R'
    carte[pos_dict[0]][pos_dict[1]] = 'D'
    carte[pos_armoire[0]][pos_armoire[1]] = 'A'
    for pos_resident in pos_residents:
        carte[pos_resident[0]][pos_resident[1]] = 'P'
    return carte

#Fonction de perception des alentours
def perception(grille, position):
    ligne = position[0]
    colonne = position[1]
    perception = {}
    perception["N"] = grille[ligne-1][colonne]
    perception["S"] = grille[ligne+1][colonne]
    perception["E"] = grille[ligne][colonne+1]
    perception["O"] = grille[ligne][colonne-1]
    return perception

#Mise à jour après perception des alentours
def update_memoire(perception, memoire, position):
    ligne = position[0]
    colonne = position[1]
    directions = {
        "N": (-1, 0),
        "S": (1, 0),
        "E": (0, 1),
        "O": (0, -1)
    }
    for direction, (dl, dc) in directions.items():
        nouvelle_ligne = ligne + dl
        nouvelle_colonne = colonne + dc
        symbole = perception[direction]
        # Le R de la carte originale représente le départ
        if symbole == "R":
            symbole = "."
        memoire[nouvelle_ligne][nouvelle_colonne] = symbole
    return memoire

#Fonction pour calculer le chemin entre le robot et les autres points
def calcul_chemin(carte_memoire, position_depart, position_arrivee):
    file = [position_depart]
    parents = {tuple(position_depart) : None}       #Ca on le met pour optimiser la recherche et ne pas tomber sur une case déjà visitée 
    while file:
        position = file.pop(0)
        if position == position_arrivee:
            break
        ligne = position[0]
        colonne = position[1]
        voisins = [
            [ligne-1,colonne],
            [ligne+1,colonne],
            [ligne,colonne+1],
            [ligne,colonne-1]
        ]
        for voisin in voisins:              #Ici pour chaque voisin on doit s'assurer qu'il est accessible et qu'il n'est pas déjà visité, c'est la qu'on ajoute le voisin à la file pour l'explorer, et on met notre position actuelle dans le tuple parents
            ligne_voisin = voisin[0]
            colonne_voisin = voisin[1]
            if ligne_voisin < 0 or ligne_voisin >= len(carte_memoire):
                continue
            if colonne_voisin < 0 or colonne_voisin >= len(carte_memoire[0]):
                continue
            if carte_memoire[ligne_voisin][colonne_voisin] in ["#", "A", "D", "P"]:  #Ici le robot ne doit pas traverser les murs, l'armoire, le dictionnaire et les residents
                continue
            voisin_tuple = tuple(voisin)
            if voisin_tuple in parents:
                continue
            parents[voisin_tuple] = tuple(position)
            file.append(voisin)

    if tuple(position_arrivee) not in parents:
        return None
    position = tuple(position_arrivee)
    chemin = []
    while position is not None:
        chemin.append(list(position))
        position = parents[position]
        if position is not None:
            position = tuple(position)
    chemin.reverse()

    return chemin

#Fonction qui va trouver la meilleure case adjacente à notre destination (pour ne pas la traverser + plus court chemin)
def meilleure_destination(carte_memoire, position_actuelle, position_cible):
    ligne = position_cible[0]
    colonne = position_cible[1]
    voisins = [
        [ligne - 1, colonne],
        [ligne + 1, colonne],
        [ligne, colonne - 1],
        [ligne, colonne + 1]
    ]
    meilleur_chemin = None
    meilleure_position = None
    for voisin in voisins:
        ligne_voisin = voisin[0]
        colonne_voisin = voisin[1]
        if ligne_voisin <= 0 or ligne_voisin >= len(carte_memoire):
            continue
        if colonne_voisin <= 0 or colonne_voisin >= len(carte_memoire[0]):
            continue
        if carte_memoire[ligne_voisin][colonne_voisin] in ["#", "A", "D", "P"]:
            continue
        chemin = calcul_chemin(carte_memoire, position_actuelle, voisin)
        if chemin is None:
            continue
        if meilleur_chemin is None or len(chemin) < len(meilleur_chemin):
            meilleur_chemin = chemin
            meilleure_position = voisin
    return meilleure_position

#Fonction pour deplacer le robot
def deplacement(memoire, pos_actuelle, pos_suivante):  #Ici on ne fait pas le calcul de voisin (obstacles, etc) car on l'a déjà fait dans la fonction calcul_chemin
    memoire[pos_actuelle[0]][pos_actuelle[1]] = "."
    memoire[pos_suivante[0]][pos_suivante[1]] = "R"
    return  pos_suivante

#Permet l'affichage de la memoire
def afficher_memoire(memoire):
    print("\nCarte mémoire du robot :")
    for ligne in memoire:
        print(" ".join(ligne))
    print()

#Fonction finale pour le deplacement
def aller_vers(memoire, position_actuelle, point, chemin):
    #Initialisation
    appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement(chemin)
    while True:
        #Perception
        perception_memoire = perception(grille, position_actuelle)
        #Update
        memoire = update_memoire(perception_memoire, memoire, position_actuelle)
        # Distance de Manhattan entre le robot et la cible
        distance = (abs(position_actuelle[0] - point[0]) + abs(position_actuelle[1] - point[1]))
        # Le robot est déjà adjacent à la cible
        if distance == 1:
            print("Robot arrivé à côté de la cible :", point)
            return memoire, position_actuelle
        #Trouver meilleure position adjacente de la destination (car on ne peut pas la traverser)
        meilleure_position = meilleure_destination(memoire, position_actuelle, point)
        if meilleure_position is None:
            print("Aucune case adjacente accessible à la cible : ", point)
            return memoire, None
        #Calculer BFS
        chemin = calcul_chemin(memoire, position_actuelle, meilleure_position)
        if chemin is None or len(chemin) < 2:
            print("Chemin impossible à trouver !", file=sys.stderr)
            return memoire, None
        print("Chemin à parcourir : ",chemin)
        #Deplacement
        prochain_point = chemin[1]
        position_actuelle = deplacement(memoire, position_actuelle, prochain_point)
        print("Position actuelle : ",position_actuelle)
        afficher_memoire(memoire)


#Tests dans le main
if __name__ == "__main__":
    appartement, hauteur, largeur,pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement(sys.argv[1])
    print("Hauteur : ",hauteur)
    print("Largeur : ",largeur)
    print("Position Robot : ",pos_robot)
    print("Position des residents", pos_residents)
    print("Position du dictionnaire : ", pos_dict)
    print("Position de l'armoire : ", pos_armoire)
    carte = creer_carte_memoire(hauteur, largeur)
    """
    print(carte_init)
    print("Perception actuelle : ",perception)
    carte_updated = update_memoire(perception, carte_init, pos_robot)
    print("Memoire mise à jour : ", carte_updated)
    print(calcul_chemin(carte_updated, pos_robot, pos_dict))
    pos_suivante = calcul_chemin(carte_updated, pos_robot, pos_dict)[0]
    print(deplacement(pos_robot, pos_suivante))
    """
    perception_robot = perception(grille, pos_robot)
    carte_init = initialiser_memoire(carte, pos_robot, pos_residents, pos_dict, pos_armoire)
    carte_updated = update_memoire(perception_robot, carte_init, pos_robot)
    memoire, pos_actuelle = aller_vers(carte_updated, pos_robot, pos_armoire, sys.argv[1])
    afficher_memoire(memoire)
    memoire, position_actuelle = aller_vers(carte_updated, pos_actuelle, pos_dict, sys.argv[1])
    afficher_memoire(memoire)
