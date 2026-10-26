import unittest
import reconfort_io as rio
from robot.emotions import trouver_emotion

dictionnaire = rio.charger_dictionnaire("donnees/dictionnaire.json")


# lire l'emotion d'un message
def lire(message):
    return trouver_emotion(rio.normaliser(message), dictionnaire)


class TestEmotion(unittest.TestCase):

    def test_seule_donne_tristesse(self):
        self.assertEqual(lire("Je me sens tellement seule ce soir."), ("tristesse", "moyenne"))

    # un message pour chaque emotion
    def test_joie(self):
        self.assertEqual(lire("Je suis contente aujourd'hui."), ("joie", "faible"))

    def test_confiance(self):
        self.assertEqual(lire("Je suis d'accord avec vous."), ("confiance", "faible"))

    def test_peur(self):
        self.assertEqual(lire("Je suis anxieuse ce soir."), ("peur", "faible"))

    def test_surprise(self):
        self.assertEqual(lire("C'est bizarre, la porte est ouverte."), ("surprise", "faible"))

    def test_tristesse(self):
        self.assertEqual(lire("J'ai le cafard."), ("tristesse", "faible"))

    def test_degout(self):
        self.assertEqual(lire("Je suis blasee de tout."), ("degout", "faible"))

    def test_colere(self):
        self.assertEqual(lire("Je suis agacee par le bruit."), ("colere", "faible"))

    def test_anticipation(self):
        self.assertEqual(lire("Je suis curieuse de voir la suite."), ("anticipation", "faible"))

    def test_premier_mot_gagne(self):
        # anxieuse arrive en premier : c'est peur
        self.assertEqual(lire("Je suis anxieuse mais contente."), ("peur", "faible"))
        # contente arrive en premier : c'est joie
        self.assertEqual(lire("Je suis contente mais anxieuse."), ("joie", "faible"))

    def test_rien_reconnu(self):
        # aucun mot connu
        self.assertEqual(lire("blablabla azerty qwerty"), (None, None))


if __name__ == "__main__":
    unittest.main()
