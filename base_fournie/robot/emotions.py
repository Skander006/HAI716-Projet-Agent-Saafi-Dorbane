import reconfort_io as rio


def trouver_emotion(mots, dictionnaire):
    for mot in mots:
        for entree in dictionnaire["entrees"]:
            if mot in entree["formes"]:
                return entree["emotion"], entree["intensite"]
    return None, None


if __name__ == "__main__":
    dictionnaire = rio.charger_dictionnaire("donnees/dictionnaire.json")

    print("=== Cas 1 : mot reconnu ===")
    mots = rio.normaliser("Je me sens tellement seule ce soir, personne n'est passé.")
    emotion, intensite = trouver_emotion(mots, dictionnaire)
    print("mots:", mots)
    print("emotion:", emotion, "| intensite:", intensite)

    print("\n=== Cas 2 : aucun mot reconnu (echec attendu) ===")
    mots = rio.normaliser("Bldjfk qsdflmk azerty.")
    emotion, intensite = trouver_emotion(mots, dictionnaire)
    print("mots:", mots)
    print("emotion:", emotion, "| intensite:", intensite)