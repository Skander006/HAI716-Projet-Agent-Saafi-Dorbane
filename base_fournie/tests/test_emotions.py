import unittest
import reconfort_io as rio
from emotions import trouver_emotion

dictionnaire = rio.charger_dictionnaire("donnees/dictionnaire.json")


class TestEmotion(unittest.TestCase):

    def test_seule_donne_tristesse(self):
        mots = rio.normaliser("Je me sens tellement seule ce soir.")
        emotion, intensite = trouver_emotion(mots, dictionnaire)
        self.assertEqual(emotion, "tristesse")
        self.assertEqual(intensite, "moyenne")

    def test_rien_reconnu(self):
        mots = rio.normaliser("blablabla azerty qwerty")
        emotion, intensite = trouver_emotion(mots, dictionnaire)
        self.assertIsNone(emotion)


if __name__ == "__main__":
    unittest.main()