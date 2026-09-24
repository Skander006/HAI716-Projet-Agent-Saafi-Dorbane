import json;
#Moteur de déplacement

#Chargement de l'appartement pour récuperer sa taille exacte
def charger_appartement(chemin):
    with open(chemin, "r", encoding="utf-8") as fichier:
        appartement = json.loads(fichier);
    
    hauteur = appartement["dimentions"]["hauteur"]
    largeur = appartement["dimensions"]["largeur"]
    return appartement, hauteur, largeur


if __name__ == "__main__":
    import sys;
    appartement, hauteur, largeur = charger_appartement(sys.argv[1])
    print("Hauteur : "+hauteur)
    print("Largeur : "+largeur)

