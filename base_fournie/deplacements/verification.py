#Verification des fichiers de carte pour le deplacement
import json
import sys

def verifier_fichier(chemin):
    try:
        with open(chemin ,"r", encoding="utf-8") as fichier:
            carte = json.load(fichier)
    #Fichier introuvable ou non lisable
    except FileNotFoundError:
        print("Erreur : Fichier de carte introuvable", file=sys.stderr)
        return False
    #Fichier non encodé en UTF-8
    except UnicodeDecodeError:
        print("Erreur : Fichier de carte non encodé en UTF-8", file=sys.stderr)
        return False
    except json.JSONDecodeError:
        print("Erreur : Fichier de carte contient un JSON invalide", file=sys.stderr)
        return False
    return carte
#Verification de la presence de tous les champs obligatoire du json
def verifier_presence(carte):
    champs_obligatoires = ["format", "version","nom", "dimensions", "legende", "grille", "depart_robot", "armoire", "residents", "dictionnaire"]
    for champ in champs_obligatoires:
        if not champ in carte:
            print(f"Erreur : Le champ {champ} est obligatoire", file=sys.stderr)
            return False
    #Verification pour l'hauteur et la largeur des dimensions
    if not ("hauteur" in carte["dimensions"] and "largeur" in carte["dimensions"]):
        print("Erreur : Le champ dimensions doit contenir les champs hauteur et largeur", file=sys.stderr)
        return False
    #Verification de la presence de toute la legende
    if not ("#" in carte["legende"] and "." in carte["legende"] and "R" in carte["legende"] and "A" in carte["legende"] and "D" in carte["legende"] and "P" in carte["legende"]):
        print("Erreur : Le champ legende manque quelques symboles", file=sys.stderr)
        return False
    #Verification de la presence de la position de l'armoire
    if not ("position" in carte["armoire"]):
        print("Erreur : Le champ armoire manque le champ position", file=sys.stderr)
        return False
    #Verification de la presence de la position du dictionnaire
    if not ("position" in carte["dictionnaire"]):
        print("Erreur : Le champ dictionnaire manque le champ position", file=sys.stderr)
        return False
    #Verification de la presence des champs de chaque resident
    for resident in carte["residents"]:
        if not ("id" in resident and "nom" in resident and "position" in resident):
            print("Erreur : Le champ residents manque quelques champs", file=sys.stderr)
            return False
    return True
#Verification des Types de champs
def verifier_types(carte):
    types_obligatoires = {
        "format" : str,
        "version" : int,
        "nom" : str,
        "dimensions" : dict,
        "legende" : dict,
        "grille" : list,
        "depart_robot" : list,
        "residents" : list,
        "dictionnaire" : dict,
        "armoire" : dict
    }
    for champ, type_attendu in types_obligatoires.items():
        if not isinstance(carte[champ], type_attendu):
            print(f"Erreur : Le champ {champ} est de type incohérent", file = sys.stderr)
            return False
    #Verification de la coherence de l'hauteur et de la largeur
    if type(carte["dimensions"]["hauteur"]) != int or type(carte["dimensions"]["largeur"]) != int:
        print("Erreur : Le type de l'hauteur ou de la largeur n'est pas un entier", file=sys.stderr)
        return False
    #Verification des types de la legende
    for item in carte["legende"].values():
        if type(item) != str:
            print("Erreur : les types de la legende sont incohérents (pas des chaines de caractères)", file=sys.stderr)
            return False
    #Logique de verification de la position
    position_dict = carte["dictionnaire"]["position"]
    position_armoire = carte["armoire"]["position"]
    position_robot = carte["depart_robot"]
    if type(position_dict) != list or type(position_armoire) !=list or type(position_robot) != list:
        print("Erreur : le type position est incohérent", file=sys.stderr)
        return False
    if len(position_dict) != 2 or len(position_armoire) != 2 or len(position_robot) != 2:
        print("Erreur : le type position doit contenir deux entiers", file=sys.stderr)
        return False
    if type(position_robot[0]) != int or type(position_robot[1]) != int or type(position_dict[0]) != int or type(position_dict[1]) != int or type(position_armoire[0]) != int or type(position_armoire[1]) != int:
        print("Erreur : les listes des positions ne sont pas des entiers", file=sys.stderr)
        return False
    #Logique de verification de residents
    for resident in carte["residents"]:
        if type(resident)!=dict:
            print("Erreur : Le champ resident est de type incohérent", file = sys.stderr)
            return False
        if len(resident) != 3:
            print("Erreur : Le champ resident doit contenir trois champs", file = sys.stderr)
            return False
        if type(resident["id"]) != str or type(resident["nom"]) != str or type(resident["position"]) != list:
            print("Erreur : Les champs de residents sont de types incohérents", file = sys.stderr)
            return False
        if len(resident["position"]) != 2:
            print("Erreur : Le champ position de resident doit contenir deux entiers", file = sys.stderr)
            return False
        if type(resident["position"][0]) != int or type(resident["position"][1]) != int:
            print("Erreur : La position du resident n'est pas une liste d'entiers", file=sys.stderr)
            return False
    #Verification de la grille
    for ligne in carte["grille"]:
        if type(ligne) != str:
            print("Erreur : la grille doit etre une liste de chaine de caractères", file=sys.stderr)
            return False
    return True
#Fichier contient un format inattendu
def verifier_format(carte):
    if (carte["format"] != "robot-reconfort/carte"):
        print("Erreur : Format du fichier de carte invalide", file=sys.stderr)
        return False
    return True
#Fichier contient une version inattendue
def verifier_version(carte):
    if(carte["version"] != 1):
        print("Erreur : Version du fichier de carte invalide", file=sys.stderr)
        return False
    return True
#Verification de la cohérence des dimensions
def verifier_coherence_dimensions(carte):
    #Verification de la cohérence des dimensions
    if carte["dimensions"]["hauteur"] <= 0 or carte["dimensions"]["largeur"] <= 0:
        print("Erreur : les dimensions ne sont pas cohérents", file = sys.stderr)
        return False

    #Coherence entre dimensions et grille
    if len(carte["grille"]) != carte["dimensions"]["hauteur"]:
        print("Erreur : La hauteur grille ne correspond pas à la hauteur en dimensions", file=sys.stderr)
        return False
    for ligne in carte["grille"]:
        if len(ligne) != carte["dimensions"]["largeur"]:
            print("Erreur : La largeur grille ne correspond pas à la largeur en dimensions", file=sys.stderr)
            return False
    return True
#Verification de la contrainte des murs dans les bords
def verifier_contrainte_murs(carte):
    premiere_ligne = carte["grille"][0]
    for i in premiere_ligne:
        if i != "#":
            print("Erreur : La premiere ligne doit contenir seulement des murs", file=sys.stderr)
            return False
    derniere_ligne = carte["grille"][-1]
    for i in derniere_ligne:
        if i != "#":
            print("Erreur : La derniere ligne doit contenir seulement des murs", file=sys.stderr)
            return False
    for ligne in carte["grille"]:
        if ligne[0] != "#":
            print("Erreur : La premiere colonne doit contenir seulement des murs", file=sys.stderr)
            return False
        if ligne[-1] != "#":
            print("Erreur : La derniere colonne doit contenir seulement des murs", file=sys.stderr)
            return False
    return True
#Positions hors grille
def verifier_positions_hors_grille(carte):
    position_robot = carte["depart_robot"]
    position_dict = carte["dictionnaire"]["position"]
    position_armoire = carte["armoire"]["position"]
    #Position du robot
    if position_robot[0] <= 0 or position_robot[1]  <=0 or position_robot[0] >= carte["dimensions"]["hauteur"]-1 or position_robot[1] >= carte["dimensions"]["largeur"]-1:
        print("Erreur : La position du robot n'est pas dans la grille", file=sys.stderr)
        return False
    #Position du dictionnaire
    if position_dict[0] <= 0 or position_dict[1] <= 0 or position_dict[0] >= carte["dimensions"]["hauteur"]-1 or position_dict[1] >= carte["dimensions"]["largeur"]-1:
        print("Erreur : La position du dictionnaire n'est pas dans la grille", file=sys.stderr)
        return False
    #Position de l'armoire
    if position_armoire[0] <= 0 or position_armoire[1] <= 0 or position_armoire[0]>=carte["dimensions"]["hauteur"]-1 or position_armoire[1]>=carte["dimensions"]["largeur"]-1:
        print("Erreur : La position de l'armoire n'est pas dans la grille", file=sys.stderr)
        return False
    #Position des residents
    for resident in carte["residents"]:
        if resident["position"][0] <= 0 or resident["position"][1] <= 0 or resident["position"][0] >= carte["dimensions"]["hauteur"]-1 or resident["position"][1] >= carte["dimensions"]["largeur"]-1:
            print("Erreur : La position du resident n'est pas dans la grille", file=sys.stderr)
            return False
    return True
#Coherence des positions avec la grille
def verifier_coherence_avec_grille(carte):
    position_robot = carte["depart_robot"]
    position_dict = carte["dictionnaire"]["position"]
    position_armoire = carte["armoire"]["position"]
    #Position du robot
    if carte["grille"][position_robot[0]][position_robot[1]] != "R":
        print("Erreur : La position du robot dans la grille n'est pas cohérente avec sa position de base", file=sys.stderr)
        return False
    #Position du dictionnaire
    if carte["grille"][position_dict[0]][position_dict[1]] != "D":
        print("Erreur : La position du dictionnaire dans la grille n'est pas cohérente avec sa position de base", file=sys.stderr)
        return False
    #Position de l'armoire
    if carte["grille"][position_armoire[0]][position_armoire[1]] != "A":
        print("Erreur : La position de l'armoire dans la grille n'est pas cohérente avec sa position de base", file=sys.stderr)
        return False
    #Position des residents
    for resident in carte["residents"]:
        if carte["grille"][resident["position"][0]][resident["position"][1]] != "P":
            print("Erreur : Les positions des residents dans la grille ne sont pas cohérente avec leur position de base")
            return False
    return True
#Verification des symboles de la grille
def verifier_symboles(carte):
    for ligne in carte["grille"]:
        for symbole in ligne:
            if symbole not in carte["legende"]:
                print("Erreur : La grille contient des symboles inconnus", file=sys.stderr)
                return False
    return True
#Verification des doublons d'IDs des residents
def verifier_doublons_ID(carte):
    ids_residents = []
    for resident in carte["residents"]:
        if resident["id"] in ids_residents:
            print("Erreur : Deux résidents partagent le même ID", file = sys.stderr)
            return False
        ids_residents.append(resident["id"])

    return True

#Validation du fichier de carte d'entrée
def valider_carte(chemin):
    carte = verifier_fichier(chemin)
    if carte is False:
        return False
    if not verifier_presence(carte):
        return False
    if not verifier_types(carte):
        return False
    if not verifier_format(carte):
        return False
    if not verifier_version(carte):
        return False
    if not verifier_coherence_dimensions(carte):
        return False
    if not verifier_contrainte_murs(carte):
        return False
    if not verifier_positions_hors_grille(carte):
        return False
    if not verifier_coherence_avec_grille(carte):
        return False
    if not verifier_symboles(carte):
        return False
    if not verifier_doublons_ID(carte):
        return False
    return True