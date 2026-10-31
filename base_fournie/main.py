"""Point d'entree du robot de reconfort.

Usage: python main.py <carte.json> <scenario.json> <dossier_donnees> <sortie.json> [--afficher]
Avec --afficher, la carte memoire est redessinee a chaque pas.
Organisation :
  validation/  verifier les 4 fichiers
  monde/       le simulateur : seul a lire la grille et le contenu des casiers
  robot/       l'agent : perception, memoire, decision, action
  tests/       contient tous les tests à propos de l'agent, l'armoire, les emotions, les donnees, les cartes et les deplacements
  deplacements/ contient le fichier contenant les fonctions pour se deplacer : creation de la carte memoire, mise à jour de la carte, trouver le chemin BFS, etc.
  cartes/      contient toutes les cartes fournies de base
  donnees/     contient les données pour l'armoire et pour le dictionnaire fournies de base
"""
import sys
from pathlib import Path
import reconfort_io as rio
from monde.monde_appartement import MondeAppartement
from monde.monde_armoire import MondeArmoire
from robot import affichage
from robot.agent import Agent
from validation.fichiers import charger_fichiers

EQUIPE = ["SAAFI Skander", "DORBANE Abdellah"]
def main(argv):
    if "--afficher" in argv:
        affichage.activer()
        argv = [a for a in argv if a != "--afficher"]
    if len(argv) != 5:
        print("Usage : python main.py <carte.json> <scenario.json> <dossier_donnees> <sortie.json> [--afficher]",file=sys.stderr)
        return 2
    chemin_carte, chemin_scenario, dossier_donnees, chemin_sortie = map(Path, argv[1:])
    fichiers = charger_fichiers(chemin_carte, chemin_scenario, dossier_donnees)
    # un fichier est faux : on s'arrete sans ecrire de trace
    if fichiers is None:
        return 1
    carte, scenario, dictionnaire, armoire = fichiers

    trace = rio.Trace(nom_carte=carte["nom"], nom_scenario=scenario["nom"], equipe=EQUIPE)
    # le monde (la realite) et l'agent (le robot) sont separés
    monde = MondeAppartement(chemin_carte)
    monde_armoire = MondeArmoire(armoire)
    agent = Agent(carte, armoire, dictionnaire, monde, monde_armoire, trace)
    affichage.log(f"[INITIALISATION] Carte : {carte['nom']} | scenario : {scenario['nom']} "f"| demandes : {len(scenario['demandes'])}")
    for demande in scenario["demandes"]:
        agent.traiter_demande(demande)
    try:
        trace.ecrire(chemin_sortie)
    except (OSError, ValueError) as erreur:
        print(f"Erreur d'ecriture : {erreur}", file=sys.stderr)
        return 1
    affichage.log(f"\n[FIN] Trace JSON ecrite : {chemin_sortie}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))