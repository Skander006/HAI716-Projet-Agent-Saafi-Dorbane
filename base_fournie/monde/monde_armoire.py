# la vraie armoire : c'est le seul fichier qui sait ce qu'il y a dans les casiers
# le robot, lui, doit regarder pour savoir


# verifier que chaque casier a bien un objet (un texte) ou rien (null)
def verifier_objets(donnees_armoire):
    for casier in donnees_armoire["casiers"]:
        if "objet" not in casier:
            return "un casier n'a pas de champ objet"
        if casier["objet"] is not None and type(casier["objet"]) != str:
            return "le champ objet d'un casier doit etre un texte ou null"
    # tout est bon
    return None


class MondeArmoire:

    def __init__(self, donnees_armoire):
        # pour chaque casier (ligne, colonne), l'objet dedans (None = vide)
        self.objets = {}
        for casier in donnees_armoire["casiers"]:
            self.objets[(casier["ligne"], casier["colonne"])] = casier["objet"]

    # le robot regarde un casier : on lui dit ce qu'il y a dedans
    def regarder(self, casier):
        return self.objets.get(tuple(casier))
