#Moteur de déplacement
import json

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


def creer_carte_memoire(hauteur, largeur):
    carte = []
    for i in range(hauteur):
        ligne =[]
        for j in range(largeur):
            ligne.append("?")
        carte.append(ligne)
    return carte

def initialiser_memoire(carte, pos_robot, pos_residents, pos_dict, pos_armoire):
    carte[pos_robot[0]][pos_robot[1]] = 'R'
    carte[pos_dict[0]][pos_dict[1]] = 'D'
    carte[pos_armoire[0]][pos_armoire[1]] = 'A'
    for pos_resident in pos_residents:
        carte[pos_resident[0]][pos_resident[1]] = 'P'
    return carte

def perception(grille, position):
    ligne = position[0]
    colonne = position[1]
    perception = {}
    perception["N"] = grille[ligne-1][colonne]
    perception["S"] = grille[ligne+1][colonne]
    perception["E"] = grille[ligne][colonne+1]
    perception["W"] = grille[ligne][colonne-1]
    return perception

def update_memoire(perception, memoire, position):
    ligne = position[0]
    colonne = position[1]
    memoire[ligne-1][colonne] = perception["N"]
    memoire[ligne+1][colonne] = perception["S"]
    memoire[ligne][colonne+1] = perception["E"]
    memoire[ligne][colonne-1] = perception["W"]
    return memoire
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
    print("Memoire mise à jour : ", update_memoire(perception, carte_init, pos_robot))

