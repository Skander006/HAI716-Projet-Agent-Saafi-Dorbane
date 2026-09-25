#Moteur de déplacement
import json
from math import *

#Chargement de l'appartement pour récuperer sa taille exacte
def charger_appartement(chemin):
    with open(chemin, "r", encoding="utf-8") as fichier:
        appartement = json.load(fichier);
    
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
    perception["W"] = grille[ligne][colonne-1]
    return perception

#Mise à jour après perception des alentours
def update_memoire(perception, memoire, position):
    ligne = position[0]
    colonne = position[1]
    memoire[ligne-1][colonne] = perception["N"]
    memoire[ligne+1][colonne] = perception["S"]
    memoire[ligne][colonne+1] = perception["E"]
    memoire[ligne][colonne-1] = perception["W"]
    return memoire

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
            if carte_memoire[ligne_voisin][colonne_voisin] == "#":
                continue
            voisin_tuple = tuple(voisin)
            if voisin_tuple in parents:
                continue
            parents[voisin_tuple] = position
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

#Tests dans le main
if __name__ == "__main__":
    import sys
    appartement, hauteur, largeur,pos_robot, pos_residents, pos_dict, pos_armoire, grille = charger_appartement(sys.argv[1])
    print("Hauteur : ",hauteur)
    print("Largeur : ",largeur)
    print("Position Robot : ",pos_robot)
    print("Position des residents", pos_residents)
    print("Position du dictionnaire : ", pos_dict)
    print("Position de l'armoire : ", pos_armoire)
    carte = creer_carte_memoire(hauteur, largeur)
    perception = perception(grille, pos_robot)
    carte_init = initialiser_memoire(carte, pos_robot, pos_residents, pos_dict, pos_armoire)
    print(carte_init)
    print("Perception actuelle : ",perception)
    carte_updated = update_memoire(perception, carte_init, pos_robot)
    print("Memoire mise à jour : ", carte_updated)
    print(calcul_chemin(carte_updated, pos_robot, pos_dict))

