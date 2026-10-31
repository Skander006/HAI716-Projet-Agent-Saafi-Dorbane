# tests du robot en entier : on lance main.py et on verifie la trace contre la realite
import copy
import json
import os
import subprocess
import sys
import reconfort_io as rio
from main import main
import random
from collections import deque
from robot.decision import prochaine_direction, resident_inaccessible, ARRIVE
from robot.memoire import MemoireRobot

CARTE = rio.charger_carte("cartes/appartement_01.json")
SCENARIO = rio.charger_scenario("cartes/scenario_01.json")
ARMOIRE = rio.charger_armoire("donnees/armoire_standard.json")
OBJETS = {(c["ligne"], c["colonne"]): c["objet"] for c in ARMOIRE["casiers"]}
NOMS = {"#": "mur", ".": "libre", "R": "libre", "A": "armoire", "D": "dictionnaire", "P": "resident"}
DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}
PETITE_CARTE = rio.charger_carte("tests/tests_agent/exemples_jsons/petite_carte.json")
PETIT_SCENARIO = rio.charger_scenario("tests/tests_agent/exemples_jsons/petit_scenario.json")
GRANDE_GRILLE = rio.charger_carte("tests/tests_agent/exemples_jsons/grande_grille.json")["grille"]

def faire_carte(nom, grille, armoire, dictionnaire, residents):
    depart = next([i, j] for i, l in enumerate(grille) for j, c in enumerate(l) if c == "R")
    return {"format": "robot-reconfort/carte", "version": 1, "nom": nom,
            "dimensions": {"hauteur": len(grille), "largeur": len(grille[0])},
            "legende": {"#": "mur", ".": "libre", "R": "depart du robot", "A": "armoire", "D": "dictionnaire", "P": "resident"},
            "grille": grille, "depart_robot": depart, "armoire": {"position": armoire},
            "dictionnaire": {"position": dictionnaire},
            "residents": [{"id": f"R{k + 1}", "nom": f"Resident {k + 1}", "position": p} for k, p in enumerate(residents)]}

def accessible_en_vrai(grille, depart, cible):
    vus, file = {tuple(depart)}, deque([tuple(depart)])
    while file:
        l, c = file.popleft()
        if abs(l - cible[0]) + abs(c - cible[1]) == 1:
            return True
        for dl, dc in DIRECTIONS.values():
            v = (l + dl, c + dc)
            if v not in vus and grille[v[0]][v[1]] in ".R":
                vus.add(v)
                file.append(v)
    return False

def lancer(tmp_path, carte=CARTE, scenario=SCENARIO):
    (tmp_path / "carte.json").write_text(json.dumps(carte), encoding="utf-8")
    (tmp_path / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
    sortie = tmp_path / "trace.json"
    code = main(["main.py", str(tmp_path / "carte.json"), str(tmp_path / "scenario.json"), "donnees", str(sortie)])
    trace = json.loads(sortie.read_text(encoding="utf-8")) if sortie.exists() else None
    return code, trace

def rejouer(trace, carte, scenario):
    grille = carte["grille"]
    position, selecteur, porte = list(carte["depart_robot"]), list(ARMOIRE["casier_depart"]), None
    armoire = carte["armoire"]["position"]
    residents = {r["id"]: r["position"] for r in carte["residents"]}
    pour_qui = {d["numero"]: d["resident"] for d in scenario["demandes"]}
    for pas in trace["pas"]:
        assert pas["position"] == position
        assert pas["casier"] == selecteur
        vraie = {d: NOMS[grille[position[0] + dl][position[1] + dc]] for d, (dl, dc) in DIRECTIONS.items()}
        assert pas["perception"] == vraie
        a_cote_armoire = abs(position[0] - armoire[0]) + abs(position[1] - armoire[1]) == 1
        assert pas["contenu_casier"] == (OBJETS.get(tuple(selecteur)) if a_cote_armoire else None)
        if pas["action"] == "AVANCER":
            assert vraie[pas["argument"]] == "libre"
            dl, dc = DIRECTIONS[pas["argument"]]
            position = [position[0] + dl, position[1] + dc]
        elif pas["action"] == "CHERCHER":
            assert a_cote_armoire
            ligne, colonne = selecteur
            if pas["argument"] in "NS":
                ligne += 1 if pas["argument"] == "S" else -1
                assert 0 <= ligne <= 2
            else:
                colonne = (colonne + (1 if pas["argument"] == "E" else -1)) % 8
            selecteur = [ligne, colonne]
        elif pas["action"] == "PRENDRE":
            assert a_cote_armoire and porte is None
            assert pas["argument"] == OBJETS[tuple(selecteur)]
            porte = pas["argument"]
        elif pas["action"] == "DONNER":
            resident = residents[pour_qui[pas["demande"]]]
            assert abs(position[0] - resident[0]) + abs(position[1] - resident[1]) == 1
            assert porte is not None and pas["argument"] == porte
            porte = None

def test_scenario_complet(tmp_path):
    code, trace = lancer(tmp_path)
    assert code == 0
    rejouer(trace, CARTE, SCENARIO)
    assert trace["resume"]["reussies"] == 4
    livraison = trace["livraisons"][0]
    assert (livraison["emotion"], livraison["intensite"]) == ("tristesse", "moyenne")
    assert (livraison["objet"], livraison["repli"], livraison["casier_choisi"]) == ("couverture", "aucun", [1, 4])

def test_les_5_scenarios_fournis(tmp_path):
    for n in range(1, 6):
        carte = rio.charger_carte(f"cartes/appartement_0{n}.json")
        scenario = rio.charger_scenario(f"cartes/scenario_0{n}.json")
        dossier = tmp_path / str(n)
        dossier.mkdir()
        code, trace = lancer(dossier, carte, scenario)
        assert code == 0
        rejouer(trace, carte, scenario)
        assert trace["resume"]["echecs"] == 0

def test_resident_inaccessible(tmp_path):
    code, trace = lancer(tmp_path, PETITE_CARTE, PETIT_SCENARIO)
    assert code == 0
    rejouer(trace, PETITE_CARTE, PETIT_SCENARIO)
    l1, l2, l3, l4 = trace["livraisons"]
    actions = lambda n: [p["action"] for p in trace["pas"] if p["demande"] == n]
    #1 : il prend la couverture, puis decouvre que R1 est mure : il garde la couverture
    assert l1["motif_echec"] == "resident inaccessible" and l1["objet"] == "couverture"
    assert actions(1).index("CONSULTER") < actions(1).index("PRENDRE")
    #2 : il a deja la preuve que R1 est mure : il ne fouille meme pas, et ne prend rien
    assert l2["motif_echec"] == "resident inaccessible" and l2["objet"] is None
    assert "CHERCHER" not in actions(2) and "PRENDRE" not in actions(2)
    #3 : R2 a besoin d'une couverture, il l'a deja dans les mains : il la donne sans PRENDRE
    assert l3["succes"] is True and l3["objet"] == "couverture"
    assert "PRENDRE" not in actions(3) and "DONNER" in actions(3)
    #4 : mains vides de nouveau, tout remarche
    assert l4["succes"] is True and "PRENDRE" in actions(4)

def test_les_motifs_sont_ceux_de_l_enonce(tmp_path):
    # dictionnaire mure : le robot ne peut pas lire l'emotion
    carte = copy.deepcopy(PETITE_CARTE)
    carte["grille"] = ["#######",
                       "#R.A..#",
                       "#####.#",
                       "#D#P.P#",
                       "#######"]
    carte["dictionnaire"]["position"] = [3, 1]
    carte["residents"] = [{"id": "R1", "nom": "A", "position": [3, 3]}, {"id": "R2", "nom": "B", "position": [3, 5]}]
    code, trace = lancer(tmp_path, carte, PETIT_SCENARIO)
    assert code == 0
    rejouer(trace, carte, PETIT_SCENARIO)
    for livraison in trace["livraisons"]:
        assert livraison["motif_echec"] == "emotion indeterminee"

def test_grande_carte(tmp_path):
    carte = faire_carte("grande", GRANDE_GRILLE, [9, 5], [13, 7], [[7, 15], [11, 15], [13, 2], [13, 12]])
    messages = ["Je me sens seule.", "Je suis un peu inquiet.", "Ce bouton m'agace.", "Je suis vraiment heureux."]
    scenario = {"format": "robot-reconfort/scenario", "version": 1, "nom": "grand", "carte": "grande",
                "armoire": "armoire_standard",
                "demandes": [{"numero": k + 1, "resident": f"R{k % 4 + 1}", "message": messages[k % 4]} for k in range(8)]}
    code, trace = lancer(tmp_path, carte, scenario)
    assert code == 0
    rejouer(trace, carte, scenario)
    for demande, livraison in zip(scenario["demandes"], trace["livraisons"]):
        cible = carte["residents"][int(demande["resident"][1:]) - 1]["position"]
        assert livraison["succes"] == accessible_en_vrai(GRANDE_GRILLE, carte["depart_robot"], cible)


def test_cartes_au_hasard(tmp_path):
    hasard = random.Random(716)
    for essai in range(40):
        hauteur, largeur = hasard.randint(6, 14), hasard.randint(6, 20)
        g = [["#"] * largeur for _ in range(hauteur)]
        for i in range(1, hauteur - 1):
            for j in range(1, largeur - 1):
                g[i][j] = "#" if hasard.random() < 0.25 else "."
        libres = [[i, j] for i in range(1, hauteur - 1) for j in range(1, largeur - 1) if g[i][j] == "."]
        if len(libres) < 6:
            continue
        hasard.shuffle(libres)
        (r, a, d), residents = libres[:3], libres[3:6]
        g[r[0]][r[1]], g[a[0]][a[1]], g[d[0]][d[1]] = "R", "A", "D"
        for p in residents:
            g[p[0]][p[1]] = "P"
        grille = ["".join(l) for l in g]
        carte = faire_carte(f"hasard{essai}", grille, a, d, residents)
        scenario = {"format": "robot-reconfort/scenario", "version": 1, "nom": "s", "carte": carte["nom"],
                    "armoire": "armoire_standard",
                    "demandes": [{"numero": k + 1, "resident": f"R{k % 3 + 1}", "message": "Je me sens seule."}
                                 for k in range(4)]}
        dossier = tmp_path / str(essai)
        dossier.mkdir()
        code, trace = lancer(dossier, carte, scenario)
        assert code == 0
        rejouer(trace, carte, scenario)
        peut_dico = accessible_en_vrai(grille, r, d)
        peut_armoire = accessible_en_vrai(grille, r, a)
        for demande, livraison in zip(scenario["demandes"], trace["livraisons"]):
            peut_resident = accessible_en_vrai(grille, r, carte["residents"][int(demande["resident"][1:]) - 1]["position"])
            if livraison["motif_echec"] == "resident inaccessible":
                assert not peut_resident
            if livraison["motif_echec"] == "emotion indeterminee":
                assert not peut_dico
            if peut_dico and peut_armoire and peut_resident:
                # tout est accessible : seul un objet garde d'une demande ratee peut faire echouer
                assert livraison["succes"] or livraison["motif_echec"] == "armoire vide"


def test_emotion_indeterminee(tmp_path):
    scenario = copy.deepcopy(SCENARIO)
    scenario["demandes"] = [{"numero": 1, "resident": "R1", "message": "blablabla azerty"}]
    code, trace = lancer(tmp_path, scenario=scenario)
    assert code == 0
    assert trace["livraisons"][0]["motif_echec"] == "emotion indeterminee"
    assert [p["action"] for p in trace["pas"]][-1] == "CONSULTER"

def test_armoire_vide(tmp_path):
    armoire = copy.deepcopy(ARMOIRE)
    for casier in armoire["casiers"]:
        casier["objet"] = None
    os.makedirs(tmp_path / "donnees")
    (tmp_path / "donnees" / "armoire_standard.json").write_text(json.dumps(armoire), encoding="utf-8")
    (tmp_path / "donnees" / "dictionnaire.json").write_text(open("donnees/dictionnaire.json", encoding="utf-8").read(),                                                            encoding="utf-8")
    (tmp_path / "carte.json").write_text(json.dumps(CARTE), encoding="utf-8")
    (tmp_path / "scenario.json").write_text(json.dumps(SCENARIO), encoding="utf-8")
    code = main(["main.py", str(tmp_path / "carte.json"), str(tmp_path / "scenario.json"),str(tmp_path / "donnees"), str(tmp_path / "trace.json")])
    trace = json.loads((tmp_path / "trace.json").read_text(encoding="utf-8"))
    assert code == 0
    assert all(l["motif_echec"] == "armoire vide" for l in trace["livraisons"])
    assert not [p for p in trace["pas"] if p["action"] == "PRENDRE"]

def refuse(tmp_path, capsys, carte=CARTE, scenario=SCENARIO, morceau=""):
    code, trace = lancer(tmp_path, carte, scenario)
    assert code != 0
    assert trace is None
    erreur = capsys.readouterr().err
    assert "Erreur" in erreur and morceau in erreur

def test_scenario_pour_une_autre_carte(tmp_path, capsys):
    scenario = copy.deepcopy(SCENARIO)
    scenario["carte"] = "appartement_02"
    refuse(tmp_path, capsys, scenario=scenario, morceau="prevu pour la carte")

def test_demande_pour_un_resident_absent(tmp_path, capsys):
    scenario = copy.deepcopy(SCENARIO)
    scenario["demandes"][0]["resident"] = "R9"
    refuse(tmp_path, capsys, scenario=scenario, morceau="R9")

def test_scenario_version_true(tmp_path, capsys):
    scenario = copy.deepcopy(SCENARIO)
    scenario["version"] = True
    refuse(tmp_path, capsys, scenario=scenario, morceau="version")

def test_scenario_champ_absent(tmp_path, capsys):
    scenario = copy.deepcopy(SCENARIO)
    del scenario["demandes"]
    refuse(tmp_path, capsys, scenario=scenario, morceau="demandes")

def test_scenario_message_pas_texte(tmp_path, capsys):
    scenario = copy.deepcopy(SCENARIO)
    scenario["demandes"][0]["message"] = 5
    refuse(tmp_path, capsys, scenario=scenario, morceau="mal ecrite")

def test_carte_cassee_refusee(tmp_path, capsys):
    carte = copy.deepcopy(CARTE)
    carte["dimensions"] = 5
    refuse(tmp_path, capsys, carte=carte, morceau="dimensions")

def test_programme_en_ligne_de_commande(tmp_path):
    sortie = tmp_path / "trace.json"
    r = subprocess.run([sys.executable, "main.py", "cartes/appartement_01.json", "cartes/scenario_01.json","donnees", str(sortie)], capture_output=True, text=True)
    assert r.returncode == 0
    assert sortie.exists()
    assert r.stdout == ""

def test_decision_arrive_a_cote():
    carte = [list("#####"), list("#R.A#"), list("#####")]
    assert prochaine_direction(carte, [1, 2], [1, 3]) == ARRIVE

def test_decision_un_pas_vers_la_cible():
    carte = [list("#####"), list("#R.A#"), list("#####")]
    assert prochaine_direction(carte, [1, 1], [1, 3]) == "E"

def test_decision_preuve_inaccessible():
    carte = [list("#####"), list("#R#P#"), list("#####")]
    assert prochaine_direction(carte, [1, 1], [1, 3]) is None

def test_preuve_resident_inaccessible():
    memoire = MemoireRobot(PETITE_CARTE, [1, 0])
    assert resident_inaccessible(memoire, "R1") is False
    for l, c in [(2, 5), (3, 4), (3, 6), (4, 5)]:
        memoire.carte[l][c] = "#"
    assert resident_inaccessible(memoire, "R1") is True
    assert resident_inaccessible(memoire, "R2") is False

def test_affichage_video(tmp_path, monkeypatch, capsys):
    from robot import affichage
    monkeypatch.setattr(affichage, "ACTIF", False)
    monkeypatch.setattr(affichage, "messages", [])
    monkeypatch.setattr(affichage.time, "sleep", lambda secondes: None)
    sans = tmp_path / "sans.json"
    avec = tmp_path / "avec.json"
    assert main(["main.py", "cartes/appartement_01.json", "cartes/scenario_01.json", "donnees", str(sans)]) == 0
    assert capsys.readouterr().out == ""
    assert main(["main.py", "cartes/appartement_01.json", "cartes/scenario_01.json", "donnees", str(avec), "--afficher"]) == 0
    ecran = capsys.readouterr().out
    assert sans.read_text(encoding="utf-8") == avec.read_text(encoding="utf-8")
    assert ecran.count("\033[H") > 100
    assert "[REPLANIFICATION] mur decouvert en [6, 7]" in ecran