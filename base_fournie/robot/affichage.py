# l'affichage dans le terminal
# par defaut on n'affiche rien : main.py l'allume avec --afficher
# la carte est redessinee a chaque pas, avec les derniers messages en dessous => pour permettre une meilleure vision
import os
import sys
import time

ACTIF = False
# combien de secondes on attend entre deux dessins (pour qu'on puisse suivre a l'oeil)
PAUSE = 0.35
# les derniers messages, affiches sous la carte
messages = []

def activer(pause=PAUSE):
    global ACTIF, PAUSE
    ACTIF, PAUSE = True, pause
    os.system("")
    # on efface l'ecran une seule fois, au debut
    print("\033[2J", end="")
    # pour que les accents des messages s'affichent bien
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

def log(*message):
    if ACTIF:
        for ligne in " ".join(str(m) for m in message).strip("\n").split("\n"):
            messages.append(ligne)
        # on garde seulement les 10 derniers
        del messages[:-10]

def afficher_memoire(carte_memoire, position):
    if not ACTIF:
        return
    lignes = ["Carte memoire du robot   (R = robot, ? = case encore inconnue)", ""]
    for i, ligne in enumerate(carte_memoire):
        lignes.append("    " + " ".join("R" if [i, j] == position else ("." if case == "R" else case) for j, case in enumerate(ligne)))
    lignes.append("")
    lignes += messages
    # on revient en haut et on redessine par-dessus, d'un seul coup (sinon l'ecran clignote) :
    print("\033[H" + "".join(l + "\033[K\n" for l in lignes) + "\033[J", end="")
    sys.stdout.flush()
    time.sleep(PAUSE)
