# DECISION : choisir la prochaine action, seulement a partir de la memoire du robot
from deplacements.deplacements import calcul_chemin, meilleure_destination, direction_entre
from robot.perception import a_cote

ARRIVE = "ARRIVE"
# la prochaine direction pour aller a cote de la cible
def prochaine_direction(carte_memoire, position, cible):
    if a_cote(position, cible):
        return ARRIVE
    chemin = chemin_prevu(carte_memoire, position, cible)
    if chemin is None or len(chemin) < 2:
        return None
    return direction_entre(position, chemin[1])

# le plus court chemin (BFS sur la carte mentale) jusqu'a la case a cote de la cible la plus proche
def chemin_prevu(carte_memoire, position, cible):
    destination = meilleure_destination(carte_memoire, position, cible)
    if destination is None:
        return None
    return calcul_chemin(carte_memoire, position, destination)

# dans ce cas le robot ne prend pas d'objet, car il ne pourrait jamais le donner
def resident_inaccessible(memoire, resident):
    cible = memoire.residents[resident]
    if a_cote(memoire.position, cible):
        return False
    return meilleure_destination(memoire.carte, memoire.position, cible) is None
