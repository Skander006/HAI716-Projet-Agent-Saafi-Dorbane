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

