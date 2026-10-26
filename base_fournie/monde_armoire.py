"""Partie SIMULATEUR de l'armoire.

C'est le seul fichier qui a le droit de lire le champ "objet" des casiers
(enonce section 3.3) : il joue le role de la realite, comme le champ
"grille" pour la carte. L'agent ne voit le contenu d'un casier qu'en
demandant au monde ce qu'il y a devant son selecteur.
"""


def verifier_objets(donnees_armoire):
    """Validation du champ objet de chaque casier (present, texte ou null).
    Elle est ici et pas dans la verification, car c'est le seul fichier qui
    a le droit de lire ce champ. Retourne un message d'erreur, ou None."""
    for casier in donnees_armoire["casiers"]:
        if "objet" not in casier:
            return "un casier n'a pas de champ objet"
        if casier["objet"] is not None and type(casier["objet"]) != str:
            return "le champ objet d'un casier doit etre un texte ou null"
    return None


class MondeArmoire:

    def __init__(self, donnees_armoire):
        # (ligne, colonne) -> nom de l'objet, ou None si le casier est vide
        self.objets = {}
        for casier in donnees_armoire["casiers"]:
            self.objets[(casier["ligne"], casier["colonne"])] = casier["objet"]

    def regarder(self, casier):
        """Perception : le contenu du casier devant lequel est le selecteur.
        Un casier absent du fichier est considere comme vide."""
        return self.objets.get(tuple(casier))
