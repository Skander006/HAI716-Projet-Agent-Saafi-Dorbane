# les 8 emotions, dans l'ordre de la roue
ORDRE_EMOTIONS = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]
# les 3 intensites, de la plus petite a la plus grande
ORDRE_INTENSITES = ["faible", "moyenne", "forte"]
# l'armoire a 3 lignes et 8 colonnes
NB_LIGNES = 3
NB_COLONNES = 8

# ce dont le robot se souvient sur l'armoire
class MemoireArmoire:
    def __init__(self, casier_depart):
        self.selecteur = tuple(casier_depart)
        self.vus = {}
    def noter(self, casier, contenu):
        self.vus[tuple(casier)] = contenu
    def deja_vu(self, casier):
        return tuple(casier) in self.vus

# combien de pas entre deux emotions sur la roue (0 a 4)
def distance_emotion(emotion1, emotion2):
    i1 = ORDRE_EMOTIONS.index(emotion1)
    i2 = ORDRE_EMOTIONS.index(emotion2)
    ecart = abs(i1 - i2)
    # la roue tourne, donc on prend le chemin le plus court
    return min(ecart, 8 - ecart)


# la liste des casiers qu'on a le droit de prendre (15 casiers)
def casiers_candidats(emotion, intensite):
    candidats = []
    rang_intensite = ORDRE_INTENSITES.index(intensite)
    i_depart = ORDRE_EMOTIONS.index(emotion)

    for e in ORDRE_EMOTIONS:
        dist_emotion = distance_emotion(emotion, e)
        if dist_emotion > 2:
            continue
        i_arrivee = ORDRE_EMOTIONS.index(e)
        sens = 0 if (i_arrivee - i_depart) % 8 <= 4 else 1
        # on ajoute les 3 intensites de cette emotion
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
# l'ordre pour trier : d'abord la distance, puis l'ecart d'intensite,
# puis la plus faible intensite, puis le sens des aiguilles
def cle_de_tri(candidat):
    return (
        candidat["distance_emotion"],
        candidat["ecart_intensite"],
        candidat["rang_intensite"],
        candidat["sens"],
    )


# on range les candidats du meilleur au moins bon
def trier_candidats(candidats):
    return sorted(candidats, key=cle_de_tri)
# ou est le casier dans l'armoire : (ligne, colonne)
def position_casier(emotion, intensite):
    ligne = ORDRE_INTENSITES.index(intensite)
    colonne = ORDRE_EMOTIONS.index(emotion)
    return (ligne, colonne)


# la liste des mouvements pour aller d'un casier a un autre
def chemin_vers(depart, arrivee):
    l1, c1 = depart
    l2, c2 = arrivee
    mouvements = []

    # d'abord on monte ou on descend
    while l1 != l2:
        if l2 > l1:
            mouvements.append("S")
            l1 += 1
        else:
            mouvements.append("N")
            l1 -= 1

    # ensuite on va a droite ou a gauche, par le cote le plus court
    a = (c2 - c1) % 8
    if a <= 8 - a:
        for _ in range(a):
            mouvements.append("E")
    else:
        for _ in range(8 - a):
            mouvements.append("O")

    return mouvements

# bouger le selecteur d'une case
def deplacer_selecteur(casier, direction):
    ligne, colonne = casier
    if direction == "N":
        # on ne peut pas monter plus haut que la ligne 0
        if ligne == 0:
            raise ValueError("CHERCHER N impossible depuis la ligne 0")
        return (ligne - 1, colonne)
    if direction == "S":
        # on ne peut pas descendre plus bas que la derniere ligne
        if ligne == NB_LIGNES - 1:
            raise ValueError("CHERCHER S impossible depuis la derniere ligne")
        return (ligne + 1, colonne)
    # a droite et a gauche, on fait le tour (apres 7 on revient a 0)
    if direction == "E":
        return (ligne, (colonne + 1) % NB_COLONNES)
    if direction == "O":
        return (ligne, (colonne - 1) % NB_COLONNES)
    raise ValueError("direction inconnue : " + str(direction))


# choisir le casier ou aller : le premier de la liste qu'on n'a pas encore vu,
# ou qu'on a vu avec un objet dedans. Les casiers vus vides, on les saute.
def choisir_cible(candidats_tries, memoire):
    for candidat in candidats_tries:
        casier = position_casier(candidat["emotion"], candidat["intensite"])
        # pas encore regarde : on y va
        if not memoire.deja_vu(casier):
            return candidat, casier, False
        # deja regarde et il y a un objet : c'est lui
        if memoire.vus[casier] is not None:
            return candidat, casier, True
    # tous les casiers sont vides
    return None, None, False


# chercher un objet dans l'armoire, une case a la fois
# renvoie l'objet, le casier choisi, et la liste des pas faits
def fouiller_armoire(emotion, intensite, memoire, monde):
    candidats_tries = trier_candidats(casiers_candidats(emotion, intensite))
    pas = []
    memoire.noter(memoire.selecteur, monde.regarder(memoire.selecteur))
    while True:
        candidat, cible, garni = choisir_cible(candidats_tries, memoire)
        # rien a prendre : on abandonne
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
        direction = chemin_vers(memoire.selecteur, cible)[0]
        pas.append({"action": "CHERCHER", "argument": direction,
                    "casier": list(memoire.selecteur),
                    "contenu_casier": contenu_actuel})
        memoire.selecteur = deplacer_selecteur(memoire.selecteur, direction)
        memoire.noter(memoire.selecteur, monde.regarder(memoire.selecteur))

# dire si on a pris le bon casier ou un autre (pour la trace)
def determiner_repli(candidat):
    # le casier exact
    if candidat["distance_emotion"] == 0 and candidat["ecart_intensite"] == 0:
        return "aucun"
    # la meme emotion mais une autre intensite
    if candidat["distance_emotion"] == 0:
        return "intensite"
    # l'emotion juste a cote sur la roue
    if candidat["distance_emotion"] == 1:
        return "voisine_1"
    # l'emotion a deux cases sur la roue
    return "voisine_2"
