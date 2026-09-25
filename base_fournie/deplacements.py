#Moteur de déplacement
import json

#Chargement de l'appartement pour récuperer sa taille exacte
def charger_appartement(chemin):
    with open(chemin, "r", encoding="utf-8") as fichier:
        appartement = json.load(fichier);
    
    hauteur = appartement["dimensions"]["hauteur"]
    largeur = appartement["dimensions"]["largeur"]
    return appartement, hauteur, largeur


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
    appartement, hauteur, largeur = charger_appartement(sys.argv[1])
    print("Hauteur : ",hauteur)
    print("Largeur : ",largeur)
    print(creer_carte_memoire(hauteur, largeur))

