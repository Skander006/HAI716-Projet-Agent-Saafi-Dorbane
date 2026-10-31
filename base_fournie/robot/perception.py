# PERCEPTION : ce que le robot recoit du monde, et rien d'autre : les 4 cases autour de lui et le contenu du casier en face du selecteur, quand il est a cote de l'armoire
from deplacements.deplacements import update_memoire
from robot.affichage import log

# les mots du monde -> les symboles de la carte mentale
SYMBOLES = {"mur": "#", "libre": ".", "armoire": "A", "dictionnaire": "D", "resident": "P"}
def a_cote(case1, case2):
    return abs(case1[0] - case2[0]) + abs(case1[1] - case2[1]) == 1

# le robot regarde autour de lui et met a jour sa carte mentale
def percevoir(memoire, monde):
    observation = monde.percevoir(memoire.position)
    update_memoire({d: SYMBOLES[v] for d, v in observation.items()}, memoire.carte, memoire.position)
    log(f"  [PERCEPTION] Position {memoire.position} : " + ", ".join(f"{d}={v}" for d, v in observation.items()))
    return observation

#regarde dans le casier
def regarder_casier(memoire, monde_armoire):
    if not a_cote(memoire.position, memoire.armoire_position):
        return None
    casier = memoire.armoire.selecteur
    contenu = monde_armoire.regarder(casier)
    memoire.armoire.noter(casier, contenu)
    return contenu