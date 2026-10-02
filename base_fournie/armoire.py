import reconfort_io as rio

ORDRE_EMOTIONS = ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]
ORDRE_INTENSITES = ["faible", "moyenne", "forte"]


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

def fouiller_armoire(emotion, intensite, armoire):
    """Simule le sélecteur qui visite les casiers candidats, dans l'ordre de
    priorité, jusqu'à trouver un objet. Retourne (objet, casier_choisi, actions).
    Si rien n'est trouvé : (None, None, actions)."""
    candidats = casiers_candidats(emotion, intensite)
    candidats_tries = trier_candidats(candidats)

    position_actuelle = tuple(armoire["casier_depart"])
    actions = []

    for candidat in candidats_tries:
        cible = position_casier(candidat["emotion"], candidat["intensite"])
        mouvements = chemin_vers(position_actuelle, cible)

        for direction in mouvements:
            actions.append(("CHERCHER", direction, None))
        position_actuelle = cible

        contenu = None
        for casier in armoire["casiers"]:
            if casier["emotion"] == candidat["emotion"] and casier["intensite"] == candidat["intensite"]:
                contenu = casier["objet"]
                break

        if actions:
            actions[-1] = (actions[-1][0], actions[-1][1], contenu)

        if contenu is not None:
            candidat["ligne"] = cible[0]
            candidat["colonne"] = cible[1]
            return contenu, candidat, actions

    return None, None, actions


def determiner_repli(candidat):
    if candidat["distance_emotion"] == 0 and candidat["ecart_intensite"] == 0:
        return "aucun"
    if candidat["distance_emotion"] == 0:
        return "intensite"
    if candidat["distance_emotion"] == 1:
        return "voisine_1"
    return "voisine_2"


if __name__ == "__main__":
    armoire = rio.charger_armoire("donnees/armoire_standard.json")

    print("=== Cas 1 : tiroir exact garni (tristesse/moyenne) ===")
    objet, casier, actions = fouiller_armoire("tristesse", "moyenne", armoire)
    print("objet:", objet, "| repli:", determiner_repli(casier), "| actions:", len(actions))

    print("\n=== Cas 2 : repli necessaire (surprise/forte, colonne vide) ===")
    objet, casier, actions = fouiller_armoire("surprise", "forte", armoire)
    print("objet:", objet, "| repli:", determiner_repli(casier), "| actions:", len(actions))

    print("\n=== Cas 3 : echec, armoire totalement vide ===")
    armoire_vide = {"casier_depart": [1, 0], "casiers": []}
    objet, casier, actions = fouiller_armoire("tristesse", "moyenne", armoire_vide)
    print("objet:", objet, "| casier:", casier, "| actions:", len(actions))