# L'AGENT : a chaque tour, il percoit, il decide, puis il agit
import reconfort_io as rio
from robot.memoire import MemoireRobot
from robot.perception import percevoir
from robot.decision import ARRIVE, prochaine_direction, chemin_prevu, resident_inaccessible
from robot import affichage
from robot.action import Actions
from robot.affichage import log, afficher_memoire

class Agent:
    def __init__(self, carte, armoire, dictionnaire, monde, monde_armoire, trace):
        self.memoire = MemoireRobot(carte, armoire["casier_depart"])
        self.monde = monde
        self.dictionnaire = dictionnaire
        self.actions = Actions(self.memoire, monde_armoire, trace)
    # renvoie True si on est arrive, False si c'est impossible
    def aller_a(self, cible, numero):
        log(f"\n  [DEPLACEMENT] Depart {self.memoire.position} -> cible {cible} (arret adjacent)")
        etats_vus = set()
        self.plan = None
        while True:
            observation = percevoir(self.memoire, self.monde)
            direction = prochaine_direction(self.memoire.carte, self.memoire.position, cible)
            if direction == ARRIVE:
                log(f"  [ARRIVEE] Robot en {self.memoire.position}, adjacent a {cible}")
                return True
            signature = (tuple(self.memoire.position), tuple("".join(l) for l in self.memoire.carte))
            if direction is None or signature in etats_vus or observation[direction] != "libre":
                log(f"  [ECHEC] Impossible d'aller a cote de {cible}")
                return False
            etats_vus.add(signature)
            if affichage.ACTIF:
                self.annoncer_replanification(cible)
            self.actions.avancer(numero, direction, observation)

    def annoncer_replanification(self, cible):
        if self.plan:
            murs = [case for case in self.plan if self.memoire.carte[case[0]][case[1]] == "#"]
            if murs:
                log(f"  [REPLANIFICATION] mur decouvert en {murs[0]} sur le chemin prevu : nouveau chemin")
        self.plan = chemin_prevu(self.memoire.carte, self.memoire.position, cible)

    # renvoie le motif d'echec, ou None si c'est reussi
    def traiter_demande(self, demande):
        numero, resident = demande["numero"], demande["resident"]
        emotion = intensite = objet = candidat = None
        log("\n" + "=" * 70)
        log(f"[DEMANDE {numero}] Resident : {resident}")
        log(f"[MESSAGE] {demande['message']}")
        log(f"[NORMALISATION] {rio.normaliser(demande['message'])}")

        motif = None
        if not self.aller_a(self.memoire.dictionnaire_position, numero):
            motif = "emotion indeterminee"
        else:
            emotion, intensite = self.actions.consulter(numero, demande["message"], self.dictionnaire,
                                                        percevoir(self.memoire, self.monde))
            if emotion is None:
                motif = "emotion indeterminee"
            elif not self.aller_a(self.memoire.armoire_position, numero):
                motif = "armoire vide"
            elif resident_inaccessible(self.memoire, resident):
                motif = "resident inaccessible"
            else:
                porte_deja = self.memoire.objet
                objet, candidat = self.actions.fouiller(numero, emotion, intensite, percevoir(self.memoire, self.monde))
                if objet is None:
                    motif = "armoire vide"
                elif porte_deja is not None and objet != porte_deja:
                    motif = "armoire vide"
                    objet = candidat = None
                elif not self.aller_a(self.memoire.residents[resident], numero):
                    # le robot garde l'objet dans les mains
                    motif = "resident inaccessible"
                else:
                    self.actions.donner(numero, percevoir(self.memoire, self.monde))

        self.actions.livrer(demande, emotion, intensite, objet, candidat, motif)
        log(f"[ETAT] Robot={self.memoire.position} | selecteur={self.memoire.casier()}")
        afficher_memoire(self.memoire.carte, self.memoire.position)
        return motif
