#Moteur de déplacement du robot

from collections import deque

#Creation de la carte memoire
def creer_carte_memoire(hauteur, largeur):
    carte = []
    for i in range(hauteur):
        ligne =[]
        for j in range(largeur):
            ligne.append("?")
        carte.append(ligne)
    return carte

#Initialisation de la carte memoire
def initialiser_memoire(carte, pos_robot, pos_residents, pos_dict, pos_armoire):
    carte[pos_robot[0]][pos_robot[1]] = 'R'
    carte[pos_dict[0]][pos_dict[1]] = 'D'
    carte[pos_armoire[0]][pos_armoire[1]] = 'A'
    for pos_resident in pos_residents:
        carte[pos_resident[0]][pos_resident[1]] = 'P'
    return carte

#Mise à jour après perception des alentours
def update_memoire(perception, memoire, position):
    ligne = position[0]
    colonne = position[1]
    directions = {
        "N": (-1, 0),
        "S": (1, 0),
        "E": (0, 1),
        "O": (0, -1)
    }
    for direction, (dl, dc) in directions.items():
        nouvelle_ligne = ligne + dl
        nouvelle_colonne = colonne + dc
        symbole = perception[direction]
        if symbole == "R":
            symbole = "."
        memoire[nouvelle_ligne][nouvelle_colonne] = symbole
    return memoire

#Fonction pour calculer le chemin entre le robot et les autres points
def calcul_chemin(carte_memoire, position_depart, position_arrivee):
    file = deque([position_depart])
    parents = {tuple(position_depart) : None}       #Ca on le met pour optimiser la recherche et ne pas tomber sur une case déjà visitée 
    while file:
        position = file.popleft
        if position == position_arrivee:
            break
        ligne = position[0]
        colonne = position[1]
        voisins = [
            [ligne-1,colonne],
            [ligne+1,colonne],
            [ligne,colonne+1],
            [ligne,colonne-1]
        ]
        for voisin in voisins:              #Ici pour chaque voisin on doit s'assurer qu'il est accessible et qu'il n'est pas déjà visité, c'est la qu'on ajoute le voisin à la file pour l'explorer, et on met notre position actuelle dans le tuple parents
            ligne_voisin = voisin[0]
            colonne_voisin = voisin[1]
            if ligne_voisin < 0 or ligne_voisin >= len(carte_memoire):
                continue
            if colonne_voisin < 0 or colonne_voisin >= len(carte_memoire[0]):
                continue
            if carte_memoire[ligne_voisin][colonne_voisin] in ["#", "A", "D", "P"]:  #Ici le robot ne doit pas traverser les murs, l'armoire, le dictionnaire et les residents
                continue
            voisin_tuple = tuple(voisin)
            if voisin_tuple in parents:
                continue
            parents[voisin_tuple] = tuple(position)
            file.append(voisin)

    if tuple(position_arrivee) not in parents:
        return None
    position = tuple(position_arrivee)
    chemin = []
    while position is not None:
        chemin.append(list(position))
        position = parents[position]
        if position is not None:
            position = tuple(position)
    chemin.reverse()

    return chemin

#Fonction qui va trouver la meilleure case adjacente à notre destination (pour ne pas la traverser + plus court chemin)
def meilleure_destination(carte_memoire, position_actuelle, position_cible):
    ligne = position_cible[0]
    colonne = position_cible[1]
    voisins = [
        [ligne - 1, colonne],
        [ligne + 1, colonne],
        [ligne, colonne - 1],
        [ligne, colonne + 1]
    ]
    meilleur_chemin = None
    meilleure_position = None
    for voisin in voisins:
        ligne_voisin = voisin[0]
        colonne_voisin = voisin[1]
        if ligne_voisin <= 0 or ligne_voisin >= len(carte_memoire):
            continue
        if colonne_voisin <= 0 or colonne_voisin >= len(carte_memoire[0]):
            continue
        if carte_memoire[ligne_voisin][colonne_voisin] in ["#", "A", "D", "P"]:
            continue
        chemin = calcul_chemin(carte_memoire, position_actuelle, voisin)
        if chemin is None:
            continue
        if meilleur_chemin is None or len(chemin) < len(meilleur_chemin):
            meilleur_chemin = chemin
            meilleure_position = voisin
    return meilleure_position

#Fonction pour deplacer le robot
def deplacement(memoire, pos_actuelle, pos_suivante):  #Ici on ne fait pas le calcul de voisin (obstacles, etc) car on l'a déjà fait dans la fonction calcul_chemin
    memoire[pos_actuelle[0]][pos_actuelle[1]] = "."
    memoire[pos_suivante[0]][pos_suivante[1]] = "R"
    return  pos_suivante

def direction_entre(case_depart, case_arrivee):
    dl = case_arrivee[0] - case_depart[0]
    dc = case_arrivee[1] - case_depart[1]
    if dl == -1:
        return "N"
    if dl == 1:
        return "S"
    if dc == 1:
        return "E"
    return "O"
