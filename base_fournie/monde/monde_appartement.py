# le vrai appartement : seul le monde connait les murs
# le robot ne lit jamais la grille, il demande au monde ce qu'il voit autour de lui
import reconfort_io as rio

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
SYMBOLES = {"#": "mur", ".": "libre", "R": "libre", "A": "armoire", "D": "dictionnaire", "P": "resident"}

class MondeAppartement:
    def __init__(self, chemin_carte):
        # le monde lit lui-meme la grille dans le fichier carte
        self._grille = rio.charger_carte(chemin_carte)["grille"]
        self.hauteur = len(self._grille)
        self.largeur = len(self._grille[0])

    def percevoir(self, position):
        ligne, colonne = position
        resultat = {}
        for direction, (dl, dc) in DIRECTIONS.items():
            l, c = ligne + dl, colonne + dc
            symbole = self._grille[l][c] if 0 <= l < self.hauteur and 0 <= c < self.largeur else "#"
            resultat[direction] = SYMBOLES[symbole]
        return resultat
