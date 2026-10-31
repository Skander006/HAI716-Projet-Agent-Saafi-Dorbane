# ACTION : executer une action et l'ecrire dans la trace
import reconfort_io as rio
from deplacements.deplacements import deplacement
from robot.armoire import fouiller_armoire, determiner_repli
from robot.emotions import trouver_emotion
from robot.perception import regarder_casier
from robot.affichage import log, afficher_memoire

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}


class Actions:

    def __init__(self, memoire, monde_armoire, trace):
        self.memoire = memoire
        self.monde_armoire = monde_armoire
        self.trace = trace

    # ecrire un pas dans la trace : position et casier sont ceux d'AVANT l'action
    def journaliser(self, numero, action, argument, observation, casier=None, contenu=None):
        if casier is None:
            casier = self.memoire.casier()
            contenu = regarder_casier(self.memoire, self.monde_armoire)
        self.trace.ajouter_pas(demande=numero, position=self.memoire.position, casier=casier,
                               action=action, argument=argument,
                               perception=observation, contenu_casier=contenu)

    def avancer(self, numero, direction, observation):
        self.journaliser(numero, "AVANCER", direction, observation)
        dl, dc = DIRECTIONS[direction]
        ancienne = list(self.memoire.position)
        suivante = [ancienne[0] + dl, ancienne[1] + dc]
        self.memoire.position = deplacement(self.memoire.carte, ancienne, suivante)
        log(f"  [AVANCER] {direction} : {ancienne} -> {self.memoire.position}")
        afficher_memoire(self.memoire.carte, self.memoire.position)

    # lire l'emotion du message dans le dictionnaire (enonce 6.1)
    def consulter(self, numero, message, dictionnaire, observation):
        self.journaliser(numero, "CONSULTER", None, observation)
        emotion, intensite = trouver_emotion(rio.normaliser(message), dictionnaire)
        log(f"  [CONSULTER] Emotion={emotion} | intensite={intensite}")
        afficher_memoire(self.memoire.carte, self.memoire.position)
        return emotion, intensite

    # fouiller l'armoire (enonce 6.2) : CHERCHER ... puis PRENDRE
    def fouiller(self, numero, emotion, intensite, observation):
        log(f"\n  [ARMOIRE] Recherche pour emotion={emotion}, intensite={intensite}")
        objet, candidat, pas = fouiller_armoire(emotion, intensite, self.memoire.armoire, self.monde_armoire)
        # le robot porte deja un objet : il n'a pas le droit de PRENDRE (un seul objet a la fois, enonce 3.4)
        mains_vides = self.memoire.objet is None
        if not mains_vides and pas and pas[-1]["action"] == "PRENDRE":
            pas = pas[:-1]
        # chaque pas de la fouille connait deja son casier (avant l'action) et ce qu'il y avait dedans
        for p in pas:
            log(f"  [CASIER] {p['action']} | casier={p['casier']} | argument={p['argument']} | contenu={p['contenu_casier']}")
            self.journaliser(numero, p["action"], p["argument"], observation, casier=p["casier"], contenu=p["contenu_casier"])
        if objet is not None and mains_vides:
            self.memoire.objet = objet
        afficher_memoire(self.memoire.carte, self.memoire.position)
        return objet, candidat

    def donner(self, numero, observation):
        objet = self.memoire.objet
        self.journaliser(numero, "DONNER", objet, observation)
        self.memoire.objet = None
        log(f"  [DONNER] {objet} | position={self.memoire.position}")
        afficher_memoire(self.memoire.carte, self.memoire.position)
        return objet

    # le resultat de la demande, reussie ou non
    def livrer(self, demande, emotion, intensite, objet, candidat, motif):
        succes = motif is None
        self.trace.ajouter_livraison(
            demande=demande["numero"], resident=demande["resident"], emotion=emotion, intensite=intensite,
            casier_choisi=([candidat["ligne"], candidat["colonne"]] if candidat else None),
            repli=determiner_repli(candidat) if candidat else "aucun",
            objet=objet, succes=succes, motif_echec=motif,
        )
        log(f"[RESULTAT DEMANDE {demande['numero']}] " + (f"SUCCES - {objet}" if succes else f"ECHEC - {motif}"))
