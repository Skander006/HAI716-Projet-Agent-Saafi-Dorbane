# verifier les 4 fichiers d'entree avant de lancer le robot
# s'il y a un probleme : message sur la sortie d'erreur, et on renvoie None
import sys
import reconfort_io as rio
from validation.carte import valider_carte
from validation.armoire_dictionnaire import valider_armoire, valider_dictionnaire

# le scenario : les champs, et qu'il va bien avec la carte
def verifier_scenario(scenario, carte):
    # reconfort_io accepte "version": true (en Python True == 1) : on le refuse
    if type(scenario["version"]) != int:
        raise ValueError("La version du scenario doit etre le nombre 1")
    for champ in ["nom", "carte", "armoire", "demandes"]:
        if champ not in scenario:
            raise ValueError(f"Le champ {champ} du scenario est obligatoire")
    if type(scenario["nom"]) != str or type(scenario["carte"]) != str \
            or type(scenario["armoire"]) != str or type(scenario["demandes"]) != list:
        raise ValueError("Le scenario a un champ du mauvais type")
    if scenario["carte"] != carte["nom"]:
        raise ValueError(f"Le scenario est prevu pour la carte {scenario['carte']}, pas pour {carte['nom']}")
    ids = [r["id"] for r in carte["residents"]]
    for demande in scenario["demandes"]:
        if type(demande) != dict or type(demande.get("numero")) != int \
                or type(demande.get("resident")) != str or type(demande.get("message")) != str:
            raise ValueError("Une demande du scenario est mal ecrite (numero, resident, message)")
        if demande["resident"] not in ids:
            raise ValueError(f"Le resident {demande['resident']} n'est pas sur la carte")


# renvoie (carte, scenario, dictionnaire, armoire), ou None s'il y a une erreur
def charger_fichiers(chemin_carte, chemin_scenario, dossier_donnees):
    try:
        if not valider_carte(str(chemin_carte)):
            raise ValueError("Carte invalide")
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        verifier_scenario(scenario, carte)
    except (rio.ErreurFichier, KeyError, TypeError, ValueError, OSError) as erreur:
        print(f"Erreur de chargement : {erreur}", file=sys.stderr)
        return None
    dictionnaire = valider_dictionnaire(dossier_donnees / "dictionnaire.json")
    if dictionnaire is False:
        return None
    armoire = valider_armoire(dossier_donnees / f"{scenario['armoire']}.json")
    if armoire is False:
        return None
    return carte, scenario, dictionnaire, armoire
