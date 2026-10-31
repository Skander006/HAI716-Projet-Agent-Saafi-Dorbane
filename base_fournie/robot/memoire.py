# MEMOIRE : tout ce dont le robot se souvient, d'un tour a l'autre et d'une demande a l'autre
from deplacements.deplacements import creer_carte_memoire, initialiser_memoire
from robot.armoire import MemoireArmoire

class MemoireRobot:

    def __init__(self, carte, casier_depart):
        # ce que le robot a le droit de savoir au depart (enonce 3.2) : pas les murs
        self.position = list(carte["depart_robot"])
        self.armoire_position = list(carte["armoire"]["position"])
        self.dictionnaire_position = list(carte["dictionnaire"]["position"])
        self.residents = {r["id"]: list(r["position"]) for r in carte["residents"]}
        # la carte mentale : des "?" partout, sauf le robot, l'armoire, le dictionnaire et les residents
        self.carte = creer_carte_memoire(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"])
        self.carte = initialiser_memoire(self.carte, self.position, list(self.residents.values()),
                                         self.dictionnaire_position, self.armoire_position)
        # ce qu'il sait de l'armoire : ou est le selecteur, et les casiers deja vus
        self.armoire = MemoireArmoire(casier_depart)
        # l'objet qu'il porte (None = mains vides)
        self.objet = None

    def casier(self):
        return list(self.armoire.selecteur)

