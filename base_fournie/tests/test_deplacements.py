import sys
sys.path.append(".")

from deplacements import calcul_chemin, initialiser_memoire

def test_bfs_chemin_simple():
    grille = [
        "#####",
        "#R..#",
        "#..P#",
        "#AD.#"
    ]
    hauteur = 4
    largeur = 5
    memoire = creer_carte_memoire(4,5)

    depart = [1,1]
    arrivee = [2,3]

    chemin = calcul_chemin(carte, depart, arrivee)

    assert chemin is not None
    assert len(chemin) -1 == 3
    assert chemin[-1] == arrivee
    assert chemin[0] == depart

def test_bfs_chemin_replanification():
    
    memoire = [
        "#R.....P#",
        "?????????",
        "?????????",
        "?????????",
        "?????????"
    ]

    depart = [0,1]
    arrivee = [0,7]

    chemin = calcul_chemin(memoire, depart, arrivee)

    assert len(chemin) - 1 == 6
    