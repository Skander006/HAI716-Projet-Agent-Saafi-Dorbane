# verifier que les fichiers armoire et dictionnaire sont corrects
# si un fichier a un probleme : on affiche l'erreur et on renvoie False
import sys

import reconfort_io as rio
from monde.monde_armoire import verifier_objets

# les emotions et les intensites qu'on attend, dans le bon ordre
EMOTIONS = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]
INTENSITES = ["faible", "moyenne", "forte"]


# afficher le message d'erreur et dire non
def erreur(nom_fichier, message):
    print(f"Erreur ({nom_fichier}) : {message}", file=sys.stderr)
    return False


# est-ce un nombre entier ? (True et False ne comptent pas comme des nombres)
def est_entier(valeur):
    return type(valeur) == int


# est-ce une position du genre [1, 4] ?
def est_position(valeur):
    return type(valeur) == list and len(valeur) == 2 and est_entier(valeur[0]) and est_entier(valeur[1])


# est-ce une liste de mots ?
def est_liste_de_textes(valeur):
    return type(valeur) == list and all(type(x) == str for x in valeur)


# ---------------------------------------------------------------------------
# Armoire
# ---------------------------------------------------------------------------

# tous les champs sont la et du bon type ?
def verifier_champs_armoire(armoire):
    for champ in ["nom", "emotions", "intensites", "casier_depart", "casiers"]:
        if champ not in armoire:
            return erreur("armoire", f"le champ {champ} est obligatoire")
    if type(armoire["nom"]) != str:
        return erreur("armoire", "le champ nom doit etre un texte")
    if not est_liste_de_textes(armoire["emotions"]):
        return erreur("armoire", "le champ emotions doit etre une liste de textes")
    if not est_liste_de_textes(armoire["intensites"]):
        return erreur("armoire", "le champ intensites doit etre une liste de textes")
    if not est_position(armoire["casier_depart"]):
        return erreur("armoire", "casier_depart doit etre une liste de deux entiers")
    if type(armoire["casiers"]) != list:
        return erreur("armoire", "le champ casiers doit etre une liste")
    # on regarde chaque casier
    for casier in armoire["casiers"]:
        if type(casier) != dict:
            return erreur("armoire", "chaque casier doit etre un objet JSON")
        for champ in ["ligne", "colonne", "emotion", "intensite"]:
            if champ not in casier:
                return erreur("armoire", f"un casier n'a pas de champ {champ}")
        if not est_entier(casier["ligne"]) or not est_entier(casier["colonne"]):
            return erreur("armoire", "ligne et colonne d'un casier doivent etre des entiers")
        if type(casier["emotion"]) != str or type(casier["intensite"]) != str:
            return erreur("armoire", "emotion et intensite d'un casier doivent etre des textes")
    # le champ objet est verifie dans le monde (le robot n'a pas le droit de le lire)
    message = verifier_objets(armoire)
    if message is not None:
        return erreur("armoire", message)
    return True


# les emotions et les intensites sont les bonnes, dans le bon ordre ?
def verifier_roue_armoire(armoire):
    if armoire["emotions"] != EMOTIONS:
        return erreur("armoire", "la liste des emotions est inconnue ou pas dans l'ordre de la roue")
    if armoire["intensites"] != INTENSITES:
        return erreur("armoire", "la liste des intensites est inconnue ou pas dans l'ordre faible, moyenne, forte")
    return True


# chaque casier est bien dans l'armoire, pas en double, et bien etiquete ?
def verifier_casiers(armoire):
    nb_lignes = len(INTENSITES)
    nb_colonnes = len(EMOTIONS)
    deja_vus = []
    for casier in armoire["casiers"]:
        ligne, colonne = casier["ligne"], casier["colonne"]
        # en dehors de l'armoire
        if not (0 <= ligne < nb_lignes and 0 <= colonne < nb_colonnes):
            return erreur("armoire", f"le casier [{ligne}, {colonne}] est hors de l'armoire")
        # deux fois le meme casier
        if (ligne, colonne) in deja_vus:
            return erreur("armoire", f"le casier [{ligne}, {colonne}] apparait deux fois")
        deja_vus.append((ligne, colonne))
        if casier["emotion"] not in EMOTIONS:
            return erreur("armoire", f"emotion inconnue : {casier['emotion']}")
        if casier["intensite"] not in INTENSITES:
            return erreur("armoire", f"intensite inconnue : {casier['intensite']}")
        # l'etiquette ne va pas avec la place du casier
        if casier["emotion"] != EMOTIONS[colonne] or casier["intensite"] != INTENSITES[ligne]:
            return erreur("armoire", f"l'etiquette du casier [{ligne}, {colonne}] ne correspond pas a sa position "
                                     f"({casier['emotion']}/{casier['intensite']})")
    return True


# le casier de depart est bien dans l'armoire ?
def verifier_casier_depart(armoire):
    ligne, colonne = armoire["casier_depart"]
    if not (0 <= ligne < len(INTENSITES) and 0 <= colonne < len(EMOTIONS)):
        return erreur("armoire", f"casier_depart [{ligne}, {colonne}] est hors de l'armoire")
    return True


# toutes les verifications de l'armoire, une apres l'autre
# des qu'une rate, on s'arrete
def valider_donnees_armoire(armoire):
    return (verifier_champs_armoire(armoire)
            and verifier_roue_armoire(armoire)
            and verifier_casiers(armoire)
            and verifier_casier_depart(armoire))


# ouvrir le fichier armoire et le verifier
# renvoie l'armoire si tout va bien, sinon False
def valider_armoire(chemin):
    try:
        armoire = rio.charger_armoire(chemin)
    except rio.ErreurFichier as err:
        # fichier absent, mal ecrit, mauvais format ou mauvaise version
        return erreur("armoire", str(err))
    if not valider_donnees_armoire(armoire):
        return False
    return armoire


# ---------------------------------------------------------------------------
# Dictionnaire
# ---------------------------------------------------------------------------

# tous les champs sont la et du bon type ?
def verifier_champs_dictionnaire(dico):
    for champ in ["nom", "emotions", "intensites", "entrees"]:
        if champ not in dico:
            return erreur("dictionnaire", f"le champ {champ} est obligatoire")
    if type(dico["nom"]) != str:
        return erreur("dictionnaire", "le champ nom doit etre un texte")
    if not est_liste_de_textes(dico["emotions"]):
        return erreur("dictionnaire", "le champ emotions doit etre une liste de textes")
    if not est_liste_de_textes(dico["intensites"]):
        return erreur("dictionnaire", "le champ intensites doit etre une liste de textes")
    if type(dico["entrees"]) != list:
        return erreur("dictionnaire", "le champ entrees doit etre une liste")
    # on regarde chaque entree
    for entree in dico["entrees"]:
        if type(entree) != dict:
            return erreur("dictionnaire", "chaque entree doit etre un objet JSON")
        for champ in ["formes", "emotion", "intensite"]:
            if champ not in entree:
                return erreur("dictionnaire", f"une entree n'a pas de champ {champ}")
        if not est_liste_de_textes(entree["formes"]) or len(entree["formes"]) == 0:
            return erreur("dictionnaire", "formes doit etre une liste de textes non vide")
        if type(entree["emotion"]) != str or type(entree["intensite"]) != str:
            return erreur("dictionnaire", "emotion et intensite d'une entree doivent etre des textes")
    return True


# les emotions et les intensites sont les bonnes, dans le bon ordre ?
def verifier_roue_dictionnaire(dico):
    if dico["emotions"] != EMOTIONS:
        return erreur("dictionnaire", "la liste des emotions est inconnue ou pas dans l'ordre de la roue")
    if dico["intensites"] != INTENSITES:
        return erreur("dictionnaire", "la liste des intensites est inconnue ou pas dans l'ordre faible, moyenne, forte")
    return True


# chaque entree a une emotion connue, et aucun mot n'est dans deux entrees ?
def verifier_entrees(dico):
    # pour chaque mot, le numero de l'entree ou on l'a vu
    mots_vus = {}
    for numero, entree in enumerate(dico["entrees"]):
        if entree["emotion"] not in EMOTIONS:
            return erreur("dictionnaire", f"emotion inconnue : {entree['emotion']}")
        if entree["intensite"] not in INTENSITES:
            return erreur("dictionnaire", f"intensite inconnue : {entree['intensite']}")
        for mot in entree["formes"]:
            # le mot est deja dans une autre entree
            if mot in mots_vus and mots_vus[mot] != numero:
                return erreur("dictionnaire", f"le mot '{mot}' apparait dans deux entrees")
            mots_vus[mot] = numero
    return True


# toutes les verifications du dictionnaire, une apres l'autre
def valider_donnees_dictionnaire(dico):
    return (verifier_champs_dictionnaire(dico)
            and verifier_roue_dictionnaire(dico)
            and verifier_entrees(dico))


# ouvrir le fichier dictionnaire et le verifier
# renvoie le dictionnaire si tout va bien, sinon False
def valider_dictionnaire(chemin):
    try:
        dico = rio.charger_dictionnaire(chemin)
    except rio.ErreurFichier as err:
        return erreur("dictionnaire", str(err))
    if not valider_donnees_dictionnaire(dico):
        return False
    return dico
