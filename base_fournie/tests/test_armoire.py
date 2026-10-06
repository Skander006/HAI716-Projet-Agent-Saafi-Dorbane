import unittest
import reconfort_io as rio
import armoire

armoire_data = rio.charger_armoire("donnees/armoire_standard.json")


class TestArmoire(unittest.TestCase):

    def test_distance_meme_emotion(self):
        self.assertEqual(armoire.distance_emotion("tristesse", "tristesse"), 0)

    def test_distance_opposees(self):
        self.assertEqual(armoire.distance_emotion("tristesse", "joie"), 4)

    def test_distance_bouclage(self):
        # anticipation et joie sont voisines a cause du bouclage
        self.assertEqual(armoire.distance_emotion("anticipation", "joie"), 1)

    def test_position_casier(self):
        self.assertEqual(armoire.position_casier("tristesse", "moyenne"), (1, 4))

    def test_chemin_vers_bouclage(self):
        # exemple du sujet, [1,0] -> [2,6], plus court par l'ouest
        chemin = armoire.chemin_vers((1, 0), (2, 6))
        self.assertEqual(len(chemin), 3)

    def test_15_candidats(self):
        candidats = armoire.casiers_candidats("tristesse", "moyenne")
        self.assertEqual(len(candidats), 15)

    def test_tri_met_casier_exact_premier(self):
        candidats = armoire.casiers_candidats("tristesse", "moyenne")
        tries = armoire.trier_candidats(candidats)
        self.assertEqual(tries[0]["emotion"], "tristesse")
        self.assertEqual(tries[0]["intensite"], "moyenne")

    def test_fouille_trouve_objet_exact(self):
        objet, casier, actions = armoire.fouiller_armoire("tristesse", "moyenne", armoire_data)
        self.assertEqual(objet, "couverture")

    def test_fouille_repli(self):
        objet, casier, actions = armoire.fouiller_armoire("surprise", "forte", armoire_data)
        self.assertEqual(objet, "telephone")
        self.assertEqual(armoire.determiner_repli(casier), "voisine_1")

    def test_armoire_vide(self):
        vide = {"casier_depart": [1, 0], "casiers": []}
        objet, casier, actions = armoire.fouiller_armoire("tristesse", "moyenne", vide)
        self.assertIsNone(objet)


if __name__ == "__main__":
    unittest.main()