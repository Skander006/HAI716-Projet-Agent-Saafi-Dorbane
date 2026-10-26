"""Controleur du robot de reconfort.

Usage: python main.py <carte.json> <scenario.json> <dossier_donnees> <sortie.json>
Le monde est le seul composant qui lit la grille reelle et le stock.
"""
import sys
from pathlib import Path

import reconfort_io as rio
from deplacements.verification import valider_carte
from deplacements.deplacements import (
    creer_carte_memoire, initialiser_memoire, update_memoire,
    calcul_chemin, meilleure_destination, deplacement,
)
from robot.emotions import trouver_emotion
from robot.armoire import MemoireArmoire, fouiller_armoire, determiner_repli
from monde.monde_armoire import MondeArmoire

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
SYMBOLES = {"#": "mur", ".": "libre", "R": "libre", "A": "armoire", "D": "dictionnaire", "P": "resident"}


def afficher_memoire(memoire, position):
    """Affiche les connaissances du robot, sans reveler la grille reelle."""
    print("    Carte memoire (? = inconnu) :")
    for i, ligne in enumerate(memoire):
        print("    " + " ".join("R" if [i, j] == position else ("." if case == "R" else case)
                                for j, case in enumerate(ligne)))


class MondeAppartement:
    """La grille n'est accessible qu'a travers percevoir()."""

    def __init__(self, carte):
        self._grille = carte["grille"]
        self.hauteur = len(self._grille)
        self.largeur = len(self._grille[0])

    def percevoir(self, position):
        ligne, colonne = position
        resultat = {}
        for direction, (dl, dc) in DIRECTIONS.items():
            l, c = ligne + dl, colonne + dc
            symbole = self._grille[l][c] if 0 <= l < self.hauteur and 0 <= c < self.largeur else "#"
            resultat[direction] = SYMBOLES[symbole]
        return resultat


class Robot:
    def __init__(self, carte, armoire, trace):
        self.monde = MondeAppartement(carte)
        self.position = list(carte["depart_robot"])
        self.armoire_position = list(carte["armoire"]["position"])
        self.dictionnaire_position = list(carte["dictionnaire"]["position"])
        self.residents = {r["id"]: list(r["position"]) for r in carte["residents"]}
        self.memoire = creer_carte_memoire(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"])
        self.memoire = initialiser_memoire(self.memoire, self.position,
                                           list(self.residents.values()), self.dictionnaire_position, self.armoire_position)
        self.armoire_memoire = MemoireArmoire(armoire["casier_depart"])
        self.monde_armoire = MondeArmoire(armoire)
        self.trace = trace

    def casier(self):
        return list(self.armoire_memoire.selecteur)

    def percevoir(self):
        observation = self.monde.percevoir(self.position)
        symboles = {"mur": "#", "libre": ".", "armoire": "A", "dictionnaire": "D", "resident": "P"}
        update_memoire({d: symboles[v] for d, v in observation.items()}, self.memoire, self.position)
        print(f"  [PERCEPTION] Position {self.position} : " +
              ", ".join(f"{d}={v}" for d, v in observation.items()))
        afficher_memoire(self.memoire, self.position)
        return observation

    def enregistrer(self, numero, action, argument=None, observation=None, contenu=None, commentaire=None):
        self.trace.ajouter_pas(demande=numero, position=self.position,
                               casier=self.casier(), action=action, argument=argument,
                               perception=observation, contenu_casier=contenu, commentaire=commentaire)

    def aller_a(self, cible, numero):
        """BFS sur la memoire, replanification a chaque perception."""
        # Garde-fou pour ne pas boucler indefiniment sur une cible impossible.
        print(f"\n  [DEPLACEMENT] Depart {self.position} -> cible {cible} (arret adjacent)")
        etats_vus = set()
        while True:
            observation = self.percevoir()
            if abs(self.position[0] - cible[0]) + abs(self.position[1] - cible[1]) == 1:
                print(f"  [ARRIVEE] Robot en {self.position}, adjacent a {cible}")
                return True
            signature = (tuple(self.position), tuple(''.join(l) for l in self.memoire))
            if signature in etats_vus:
                print("  [ECHEC] Etat deja rencontre : navigation bloquee")
                return False
            etats_vus.add(signature)
            destination = meilleure_destination(self.memoire, self.position, cible)
            if destination is None:
                print("  [ECHEC] Aucune destination adjacente accessible")
                return False
            chemin = calcul_chemin(self.memoire, self.position, destination)
            if chemin is None or len(chemin) < 2:
                print("  [ECHEC] Aucun chemin exploitable")
                return False
            print(f"  [BFS] Destination {destination} | chemin prevu : {chemin}")
            suivante = chemin[1]
            dl, dc = suivante[0] - self.position[0], suivante[1] - self.position[1]
            direction = next((d for d, delta in DIRECTIONS.items() if delta == (dl, dc)), None)
            if direction is None or observation[direction] != "libre":
                print(f"  [ECHEC] Deplacement interdit : {direction} vers {suivante}")
                return False
            self.enregistrer(numero, "AVANCER", direction, observation)
            ancienne = list(self.position)
            self.position = deplacement(self.memoire, self.position, suivante)
            print(f"  [AVANCER] {direction} : {ancienne} -> {self.position}")

    def chercher_objet(self, numero, emotion, intensite):
        print(f"\n  [ARMOIRE] Recherche pour emotion={emotion}, intensite={intensite}")
        objet, candidat, pas = fouiller_armoire(emotion, intensite, self.armoire_memoire, self.monde_armoire)
        # La fonction de fouille actualise deja la memoire du selecteur.
        # Reconstituer sa position avant chaque pas pour tracer correctement.
        from robot.armoire import deplacer_selecteur
        if pas:
            position_initiale = tuple(pas[0]["casier"])
        else:
            position_initiale = self.armoire_memoire.selecteur
        position = position_initiale
        for evenement in pas:
            print(f"  [CASIER] {evenement['action']} | position={position} | "
                  f"argument={evenement.get('argument')} | "
                  f"contenu={evenement.get('contenu_casier')}")
            self.trace.ajouter_pas(demande=numero, position=self.position,
                                   casier=position, action=evenement["action"], argument=evenement["argument"],
                                   contenu_casier=evenement.get("contenu_casier"))
            if evenement["action"] == "CHERCHER":
                position = deplacer_selecteur(position, evenement["argument"])
        print(f"  [SELECTION] Objet={objet} | candidat={candidat} | "
              f"selecteur final={self.casier()}")
        return objet, candidat


def main(argv):
    if len(argv) != 5:
        print("Usage : python main.py <carte.json> <scenario.json> <dossier_donnees> <sortie.json>", file=sys.stderr)
        return 2

    chemin_carte, chemin_scenario, dossier_donnees, chemin_sortie = map(Path, argv[1:])
    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        dictionnaire = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
        armoire = rio.charger_armoire(dossier_donnees / f"{scenario['armoire']}.json")
        if not valider_carte(str(chemin_carte)):
            raise ValueError("Carte invalide")
        if scenario["carte"] != carte["nom"]:
            raise ValueError("Le scenario ne correspond pas a la carte")
    except (rio.ErreurFichier, KeyError, TypeError, ValueError, OSError) as erreur:
        print(f"Erreur de chargement : {erreur}", file=sys.stderr)
        return 1

    print("=" * 70)
    print(f"[INITIALISATION] Carte : {carte['nom']} ({carte['dimensions']['hauteur']}x{carte['dimensions']['largeur']})")
    print(f"[INITIALISATION] Scenario : {scenario['nom']} | demandes : {len(scenario['demandes'])}")
    print(f"[INITIALISATION] Dictionnaire : {len(dictionnaire['entrees'])} entrees")
    print(f"[INITIALISATION] Armoire : {armoire['nom']} | casiers : {len(armoire['casiers'])}")
    trace = rio.Trace(nom_carte=carte["nom"], nom_scenario=scenario["nom"], equipe=["Saafi", "Dorbane"])
    robot = Robot(carte, armoire, trace)
    print(f"[INITIALISATION] Position robot : {robot.position} | selecteur : {robot.casier()}")
    afficher_memoire(robot.memoire, robot.position)

    for demande in scenario["demandes"]:
        numero, resident = demande["numero"], demande["resident"]
        emotion = intensite = objet = candidat = None
        motif = None
        succes = False
        print("\n" + "=" * 70)
        print(f"[DEMANDE {numero}] Resident : {resident}")
        print(f"[MESSAGE] {demande['message']}")
        print(f"[NORMALISATION] {rio.normaliser(demande['message'])}")

        if resident not in robot.residents:
            motif = "resident inconnu"
        elif not robot.aller_a(robot.dictionnaire_position, numero):
            motif = "dictionnaire inaccessible"
        else:
            robot.enregistrer(numero, "CONSULTER", observation=robot.percevoir())
            emotion, intensite = trouver_emotion(rio.normaliser(demande["message"]), dictionnaire)
            print(f"  [EMOTION] Emotion={emotion} | intensite={intensite}")
            if emotion is None:
                motif = "emotion indeterminee"
            elif not robot.aller_a(robot.armoire_position, numero):
                motif = "armoire inaccessible"
            else:
                objet, candidat = robot.chercher_objet(numero, emotion, intensite)
                if objet is None:
                    motif = "armoire vide ou aucun objet adapte"
                elif not robot.aller_a(robot.residents[resident], numero):
                    motif = "resident inaccessible"
                else:
                    print(f"  [LIVRAISON] Resident={resident} | objet={objet} | position={robot.position}")
                    robot.enregistrer(numero, "DONNER", observation=robot.percevoir(), commentaire=f"Objet : {objet}")
                    succes = True

        trace.ajouter_livraison(
            demande=numero, resident=resident, emotion=emotion, intensite=intensite,
            casier_choisi=([candidat["ligne"], candidat["colonne"]] if candidat else None),
            repli=determiner_repli(candidat) if candidat else "aucun",
            objet=objet, succes=succes, motif_echec=None if succes else motif,
        )
        print(f"[RESULTAT DEMANDE {numero}] " + (f"SUCCES - {objet}" if succes else f"ECHEC - {motif}"))
        print(f"[ETAT] Robot={robot.position} | selecteur={robot.casier()}")

    try:
        trace.ecrire(chemin_sortie)
    except (OSError, ValueError) as erreur:
        print(f"Erreur d'ecriture : {erreur}", file=sys.stderr)
        return 1
    print("\n" + "=" * 70)
    print(f"[FIN] Trace JSON ecrite : {chemin_sortie}")
    print(f"[FIN] Position finale du robot : {robot.position}")
    print("[FIN] Carte memoire finale :")
    afficher_memoire(robot.memoire, robot.position)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

