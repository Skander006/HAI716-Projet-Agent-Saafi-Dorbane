import reconfort_io as rio
from monde_armoire import MondeArmoire

ORDRE_EMOTIONS = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]
ORDRE_INTENSITES = ["faible", "moyenne", "forte"]
NB_LIGNES = 3
NB_COLONNES = 8


class MemoireArmoire:
    """Memoire de l'agent sur l'armoire : ou est le selecteur, et ce qu'il a
    deja vu dans chaque casier. Elle persiste d'une demande a l'autre
    (enonce section 4)."""

    def __init__(self, casier_depart):
        self.selecteur = tuple(casier_depart)
        self.vus = {}  # (ligne, colonne) -> objet vu, ou None si vu vide

    def noter(self, casier, contenu):
        self.vus[tuple(casier)] = contenu

    def deja_vu(self, casier):
        return tuple(casier) in self.vus


def distance_emotion(emotion1, emotion2):
    i1 = ORDRE_EMOTIONS.index(emotion1)
    i2 = ORDRE_EMOTIONS.index(emotion2)
    ecart = abs(i1 - i2)
    return min(ecart, 8 - ecart)


def casiers_candidats(emotion, intensite):
    candidats = []
    rang_intensite = ORDRE_INTENSITES.index(intensite)
    i_depart = ORDRE_EMOTIONS.index(emotion)

    for e in ORDRE_EMOTIONS:
        dist_emotion = distance_emotion(emotion, e)
        if dist_emotion > 2:
            continue

        i_arrivee = ORDRE_EMOTIONS.index(e)
        # 0 = sens horaire (on avance), 1 = sens antihoraire (on recule)
        sens = 0 if (i_arrivee - i_depart) % 8 <= 4 else 1

        for i, autre_intensite in enumerate(ORDRE_INTENSITES):
            ecart_intensite = abs(rang_intensite - i)
            candidats.append({
                "emotion": e,
                "intensite": autre_intensite,
                "distance_emotion": dist_emotion,
                "ecart_intensite": ecart_intensite,
                "rang_intensite": i,
                "sens": sens,
            })

    return candidats
def cle_de_tri(candidat):
    return (
        candidat["distance_emotion"],
        candidat["ecart_intensite"],
        candidat["rang_intensite"],
        candidat["sens"],
    )


def trier_candidats(candidats):
    return sorted(candidats, key=cle_de_tri)
def position_casier(emotion, intensite):
    ligne = ORDRE_INTENSITES.index(intensite)
    colonne = ORDRE_EMOTIONS.index(emotion)
    return (ligne, colonne)


def chemin_vers(depart, arrivee):
    l1, c1 = depart
    l2, c2 = arrivee
    mouvements = []

    while l1 != l2:
        if l2 > l1:
            mouvements.append("S")
            l1 += 1
        else:
            mouvements.append("N")
            l1 -= 1

    a = (c2 - c1) % 8
    if a <= 8 - a:
        for _ in range(a):
            mouvements.append("E")
    else:
        for _ in range(8 - a):
            mouvements.append("O")

    return mouvements

def deplacer_selecteur(casier, direction):
    """Action CHERCHER : un casier dans la direction donnee. Les colonnes
    bouclent (7 <-> 0), les lignes non (annexe C.2)."""
    ligne, colonne = casier
    if direction == "N":
        if ligne == 0:
            raise ValueError("CHERCHER N impossible depuis la ligne 0")
        return (ligne - 1, colonne)
    if direction == "S":
        if ligne == NB_LIGNES - 1:
            raise ValueError("CHERCHER S impossible depuis la derniere ligne")
        return (ligne + 1, colonne)
    if direction == "E":
        return (ligne, (colonne + 1) % NB_COLONNES)
    if direction == "O":
        return (ligne, (colonne - 1) % NB_COLONNES)
    raise ValueError("direction inconnue : " + str(direction))


def choisir_cible(candidats_tries, memoire):
    """Decision : le premier candidat (dans l'ordre de priorite) qui est soit
    pas encore vu, soit vu et garni. Les candidats deja vus vides sont sautes.
    Retourne (candidat, casier, garni) ou (None, None, False) si les 15
    candidats sont tous vus vides."""
    for candidat in candidats_tries:
        casier = position_casier(candidat["emotion"], candidat["intensite"])
        if not memoire.deja_vu(casier):
            return candidat, casier, False
        if memoire.vus[casier] is not None:
            return candidat, casier, True
    return None, None, False


def fouiller_armoire(emotion, intensite, memoire, monde):
    """Fouille l'armoire pour (emotion, intensite), un casier a la fois.
    A chaque tour : l'agent decide d'un mouvement d'apres sa memoire, le
    monde lui montre le casier ou il arrive, et il le note dans sa memoire.

    Retourne (objet, candidat_choisi, pas) ; (None, None, pas) si l'armoire
    est vide pour cette demande. Chaque pas est un dictionnaire avec action,
    argument, casier (AVANT l'action) et contenu_casier, pour la trace."""
    candidats_tries = trier_candidats(casiers_candidats(emotion, intensite))
    pas = []

    # perception : le robot voit le casier devant lequel est deja le selecteur
    memoire.noter(memoire.selecteur, monde.regarder(memoire.selecteur))

    while True:
        candidat, cible, garni = choisir_cible(candidats_tries, memoire)
        if candidat is None:
            return None, None, pas

        contenu_actuel = memoire.vus[memoire.selecteur]

        if garni and memoire.selecteur == cible:
            pas.append({"action": "PRENDRE", "argument": contenu_actuel,
                        "casier": list(memoire.selecteur),
                        "contenu_casier": contenu_actuel})
            candidat["ligne"] = cible[0]
            candidat["colonne"] = cible[1]
            return contenu_actuel, candidat, pas

        # un seul mouvement vers la cible, puis on regarde le nouveau casier
        direction = chemin_vers(memoire.selecteur, cible)[0]
        pas.append({"action": "CHERCHER", "argument": direction,
                    "casier": list(memoire.selecteur),
                    "contenu_casier": contenu_actuel})
        memoire.selecteur = deplacer_selecteur(memoire.selecteur, direction)
        memoire.noter(memoire.selecteur, monde.regarder(memoire.selecteur))


def determiner_repli(candidat):
    if candidat["distance_emotion"] == 0 and candidat["ecart_intensite"] == 0:
        return "aucun"
    if candidat["distance_emotion"] == 0:
        return "intensite"
    if candidat["distance_emotion"] == 1:
        return "voisine_1"
    return "voisine_2"


if __name__ == "__main__":
    donnees = rio.charger_armoire("donnees/armoire_standard.json")
    monde = MondeArmoire(donnees)
    memoire = MemoireArmoire(donnees["casier_depart"])

    print("=== Cas 1 : tiroir exact garni (tristesse/moyenne) ===")
    objet, casier, pas = fouiller_armoire("tristesse", "moyenne", memoire, monde)
    print("objet:", objet, "| repli:", determiner_repli(casier), "| pas:", len(pas))

    print("\n=== Cas 2 : repli (surprise/forte, colonne vide), le selecteur repart de", memoire.selecteur, "===")
    objet, casier, pas = fouiller_armoire("surprise", "forte", memoire, monde)
    print("objet:", objet, "| repli:", determiner_repli(casier), "| pas:", len(pas))

    print("\n=== Cas 3 : echec, armoire totalement vide ===")
    vide = {"casier_depart": [1, 0], "casiers": []}
    objet, casier, pas = fouiller_armoire("tristesse", "moyenne", MemoireArmoire([1, 0]), MondeArmoire(vide))
    print("objet:", objet, "| casier:", casier, "| pas:", len(pas))