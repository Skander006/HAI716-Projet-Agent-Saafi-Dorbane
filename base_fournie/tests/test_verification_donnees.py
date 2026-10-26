import copy
import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr

import reconfort_io as rio
from validation import armoire_dictionnaire as v

ARMOIRE = rio.charger_armoire("donnees/armoire_standard.json")
DICO = rio.charger_dictionnaire("donnees/dictionnaire.json")


# creer un petit fichier pour le test
def fichier_temporaire(contenu_octets):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    f.write(contenu_octets)
    f.close()
    return f.name


# a chaque fois : on prend la vraie armoire, on la casse un peu,
# et on verifie qu'elle est refusee
class TestVerificationArmoire(unittest.TestCase):

    # l'armoire doit etre refusee, avec un message d'erreur
    def refuse(self, armoire):
        sortie = io.StringIO()
        with redirect_stderr(sortie):
            resultat = v.valider_donnees_armoire(armoire)
        self.assertFalse(resultat)
        self.assertIn("Erreur", sortie.getvalue())

    def test_armoire_standard_acceptee(self):
        # la vraie armoire, elle, est acceptee
        self.assertTrue(v.valider_donnees_armoire(copy.deepcopy(ARMOIRE)))

    def test_champ_absent(self):
        a = copy.deepcopy(ARMOIRE)
        del a["casiers"]
        self.refuse(a)

    def test_mauvais_type(self):
        # "1" est un texte, pas un nombre
        a = copy.deepcopy(ARMOIRE)
        a["casiers"][0]["ligne"] = "1"
        self.refuse(a)

    def test_casier_hors_armoire(self):
        # il n'y a pas de colonne 8
        a = copy.deepcopy(ARMOIRE)
        a["casiers"][0]["colonne"] = 8
        self.refuse(a)

    def test_casier_en_double(self):
        a = copy.deepcopy(ARMOIRE)
        a["casiers"].append(copy.deepcopy(a["casiers"][0]))
        self.refuse(a)

    def test_etiquette_incoherente(self):
        # on change le nom de l'emotion sans changer la place du casier
        a = copy.deepcopy(ARMOIRE)
        casier = a["casiers"][0]
        casier["emotion"] = v.EMOTIONS[(casier["colonne"] + 1) % 8]
        self.refuse(a)

    def test_casier_depart_hors_armoire(self):
        # il n'y a pas de ligne 3
        a = copy.deepcopy(ARMOIRE)
        a["casier_depart"] = [3, 0]
        self.refuse(a)

    def test_emotion_inconnue(self):
        a = copy.deepcopy(ARMOIRE)
        a["casiers"][0]["emotion"] = "nostalgie"
        self.refuse(a)

    def test_ordre_de_la_roue_change(self):
        # on echange joie et confiance
        a = copy.deepcopy(ARMOIRE)
        a["emotions"][0], a["emotions"][1] = a["emotions"][1], a["emotions"][0]
        self.refuse(a)


# pareil pour le dictionnaire
class TestVerificationDictionnaire(unittest.TestCase):

    def refuse(self, dico):
        sortie = io.StringIO()
        with redirect_stderr(sortie):
            resultat = v.valider_donnees_dictionnaire(dico)
        self.assertFalse(resultat)
        self.assertIn("Erreur", sortie.getvalue())

    def test_dictionnaire_fourni_accepte(self):
        # le vrai dictionnaire, lui, est accepte
        self.assertTrue(v.valider_donnees_dictionnaire(copy.deepcopy(DICO)))

    def test_champ_absent(self):
        d = copy.deepcopy(DICO)
        del d["entrees"]
        self.refuse(d)

    def test_mauvais_type(self):
        # formes doit etre une liste, pas un seul mot
        d = copy.deepcopy(DICO)
        d["entrees"][0]["formes"] = "triste"
        self.refuse(d)

    def test_emotion_inconnue(self):
        d = copy.deepcopy(DICO)
        d["entrees"][0]["emotion"] = "nostalgie"
        self.refuse(d)

    def test_intensite_inconnue(self):
        d = copy.deepcopy(DICO)
        d["entrees"][0]["intensite"] = "enorme"
        self.refuse(d)

    def test_meme_mot_dans_deux_entrees(self):
        # on met un mot de la 1re entree aussi dans la 2e
        d = copy.deepcopy(DICO)
        d["entrees"][1]["formes"].append(d["entrees"][0]["formes"][0])
        self.refuse(d)


# les fichiers abimes : absent, mauvais encodage, JSON casse,
# mauvais format, mauvaise version
class TestVerificationFichiers(unittest.TestCase):

    def refuse_fichier(self, chemin):
        sortie = io.StringIO()
        with redirect_stderr(sortie):
            resultat = v.valider_armoire(chemin)
        self.assertFalse(resultat)
        self.assertIn("Erreur", sortie.getvalue())

    def test_fichier_absent(self):
        self.refuse_fichier("donnees/cette_armoire_n_existe_pas.json")

    def test_fichier_pas_utf8(self):
        chemin = fichier_temporaire('{"nom": "caf\xe9"}'.encode("latin-1"))
        self.refuse_fichier(chemin)
        os.remove(chemin)

    def test_json_invalide(self):
        # le JSON n'est pas fini
        chemin = fichier_temporaire(b'{"format": "robot-reconfort/armoire", ')
        self.refuse_fichier(chemin)
        os.remove(chemin)

    def test_format_inattendu(self):
        # c'est un fichier carte, pas un fichier armoire
        chemin = fichier_temporaire(b'{"format": "robot-reconfort/carte", "version": 1}')
        self.refuse_fichier(chemin)
        os.remove(chemin)

    def test_version_inattendue(self):
        chemin = fichier_temporaire(b'{"format": "robot-reconfort/armoire", "version": 2}')
        self.refuse_fichier(chemin)
        os.remove(chemin)

    def test_dictionnaire_fichier_absent(self):
        sortie = io.StringIO()
        with redirect_stderr(sortie):
            self.assertFalse(v.valider_dictionnaire("donnees/introuvable.json"))
        self.assertIn("Erreur", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
