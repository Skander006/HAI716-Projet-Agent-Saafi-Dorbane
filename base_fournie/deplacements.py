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
    return appartement, hauteur, largeur, pos_robot, pos_residents, pos_dict, pos_armoire


def creer_carte_memoire(hauteur, largeur):
    carte = []
    for i in range(hauteur):
        ligne =[]
        for j in range(largeur):
            ligne.append("?")
        carte.append(ligne)
    return carte


if __name__ == "__main__":
    import sys
    appartement, hauteur, largeur,pos_robot, pos_residents, pos_dict, pos_armoire = charger_appartement(sys.argv[1])
    print("Hauteur : ",hauteur)
    print("Largeur : ",largeur)
    print("Position Robot : ",pos_robot)
    print("Position des residents", pos_residents)
    print("Position du dictionnaire : ", pos_dict)
    print("Position de l'armoire : ", pos_armoire)
    print(creer_carte_memoire(hauteur, largeur))

