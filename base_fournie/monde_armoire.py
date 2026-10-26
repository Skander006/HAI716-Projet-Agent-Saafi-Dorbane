"""Partie SIMULATEUR de l'armoire.

C'est le seul fichier qui a le droit de lire le champ "objet" des casiers
(enonce section 3.3) : il joue le role de la realite, comme le champ
"grille" pour la carte. L'agent ne voit le contenu d'un casier qu'en
demandant au monde ce qu'il y a devant son selecteur.
"""


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
