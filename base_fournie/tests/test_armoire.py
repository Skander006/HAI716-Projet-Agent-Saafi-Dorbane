import unittest
import reconfort_io as rio
from robot import armoire
from monde.monde_armoire import MondeArmoire

armoire_data = rio.charger_armoire("donnees/armoire_standard.json")


# lancer une fouille avec une memoire toute neuve
def nouvelle_fouille(emotion, intensite, donnees=armoire_data):
    memoire = armoire.MemoireArmoire(donnees["casier_depart"])
    return armoire.fouiller_armoire(emotion, intensite, memoire, MondeArmoire(donnees))


# fabriquer une armoire de test : tous les casiers sont vides,
# sauf ceux qu'on donne dans objets
def armoire_test(objets, casier_depart=(1, 0)):
    casiers = []
    for ligne in range(3):
        for colonne in range(8):
            casiers.append({"ligne": ligne, "colonne": colonne,
                            "emotion": armoire.ORDRE_EMOTIONS[colonne],
                            "intensite": armoire.ORDRE_INTENSITES[ligne],
                            "objet": objets.get((ligne, colonne))})
    return {"casier_depart": list(casier_depart), "casiers": casiers}


class TestArmoire(unittest.TestCase):

    def test_distance_meme_emotion(self):
        self.assertEqual(armoire.distance_emotion("tristesse", "tristesse"), 0)

    def test_distance_opposees(self):
        self.assertEqual(armoire.distance_emotion("tristesse", "joie"), 4)

    def test_distance_bouclage(self):
        # anticipation et joie sont cote a cote car la roue tourne
        self.assertEqual(armoire.distance_emotion("anticipation", "joie"), 1)

    def test_position_casier(self):
        self.assertEqual(armoire.position_casier("tristesse", "moyenne"), (1, 4))

    def test_chemin_vers_bouclage(self):
        # de [1,0] a [2,6] : plus court en passant par la gauche
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

    # --- bouger le selecteur ---

    def test_chemin_directions_exemples_annexe(self):
        # les trois exemples du sujet
        self.assertEqual(armoire.chemin_vers((1, 0), (1, 4)), ["E", "E", "E", "E"])
        self.assertEqual(armoire.chemin_vers((2, 7), (0, 1)), ["N", "N", "E", "E"])
        self.assertEqual(armoire.chemin_vers((1, 0), (2, 6)), ["S", "O", "O"])

    def test_bouclage_colonne_7_vers_0(self):
        # apres la colonne 7 on revient a la colonne 0
        self.assertEqual(armoire.chemin_vers((1, 7), (1, 0)), ["E"])
        self.assertEqual(armoire.deplacer_selecteur((1, 7), "E"), (1, 0))

    def test_bouclage_colonne_0_vers_7(self):
        # avant la colonne 0 il y a la colonne 7
        self.assertEqual(armoire.chemin_vers((1, 0), (1, 7)), ["O"])
        self.assertEqual(armoire.deplacer_selecteur((1, 0), "O"), (1, 7))

    def test_lignes_ne_bouclent_pas(self):
        # on ne peut pas sortir par le haut ni par le bas
        with self.assertRaises(ValueError):
            armoire.deplacer_selecteur((0, 3), "N")
        with self.assertRaises(ValueError):
            armoire.deplacer_selecteur((2, 3), "S")

    # --- quel casier on prend ---

    def test_fouille_trouve_objet_exact(self):
        # le bon casier a un objet : on le prend
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne")
        self.assertEqual(objet, "couverture")
        self.assertEqual(armoire.determiner_repli(casier), "aucun")

    def test_repli_intensite(self):
        # anticipation/forte est vide, alors on prend anticipation/moyenne
        objet, casier, pas = nouvelle_fouille("anticipation", "forte")
        self.assertEqual(objet, "calendrier")
        self.assertEqual(armoire.determiner_repli(casier), "intensite")
        self.assertEqual([casier["ligne"], casier["colonne"]], [1, 7])

    def test_fouille_repli(self):
        # toute la colonne surprise est vide, alors on prend chez la voisine
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        self.assertEqual(objet, "telephone")
        self.assertEqual(armoire.determiner_repli(casier), "voisine_1")

    def test_armoire_vide(self):
        vide = {"casier_depart": [1, 0], "casiers": []}
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne", vide)
        self.assertIsNone(objet)

    def test_aucun_casier_garni_a_distance_2(self):
        # il y a des objets mais trop loin sur la roue : on ne doit pas les prendre
        donnees = armoire_test({(1, 0): "ballon", (1, 1): "livre"})
        memoire = armoire.MemoireArmoire(donnees["casier_depart"])
        objet, casier, pas = armoire.fouiller_armoire("tristesse", "moyenne", memoire, MondeArmoire(donnees))
        self.assertIsNone(objet)
        self.assertIsNone(casier)
        # avant d'abandonner, le robot a regarde les 15 casiers
        for c in armoire.casiers_candidats("tristesse", "moyenne"):
            self.assertTrue(memoire.deja_vu(armoire.position_casier(c["emotion"], c["intensite"])))

    # --- l'ordre des casiers ---

    def test_ordre_candidats_annexe(self):
        # les 5 premiers casiers pour surprise/forte, comme dans le sujet
        tries = armoire.trier_candidats(armoire.casiers_candidats("surprise", "forte"))
        premiers = [armoire.position_casier(c["emotion"], c["intensite"]) for c in tries[:5]]
        self.assertEqual(premiers, [(2, 3), (1, 3), (0, 3), (2, 4), (2, 2)])

    def test_intensite_faible_avant_forte(self):
        # faible et forte ont un objet : on doit prendre faible d'abord
        donnees = armoire_test({(0, 4): "plaid", (2, 4): "telephone"})
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne", donnees)
        self.assertEqual(objet, "plaid")

    def test_ordre_prime_sur_ce_qu_on_croise(self):
        # on passe devant un objet en chemin, mais on ne le prend pas
        # car un autre casier passe avant dans la liste
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        self.assertIn([2, 2], [p["casier"] for p in pas])
        self.assertEqual([casier["ligne"], casier["colonne"]], [2, 4])

    # --- ce que le robot voit et retient ---

    def test_contenu_casier_correspond_a_la_realite(self):
        # ce que le robot dit avoir vu est bien ce qu'il y a dans le casier
        monde = MondeArmoire(armoire_data)
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        for p in pas:
            self.assertEqual(p["contenu_casier"], monde.regarder(p["casier"]))

    def test_selecteur_garde_sa_position(self):
        # la 2e fouille repart la ou la 1re s'est arretee
        monde = MondeArmoire(armoire_data)
        memoire = armoire.MemoireArmoire(armoire_data["casier_depart"])
        armoire.fouiller_armoire("tristesse", "moyenne", memoire, monde)
        objet, casier, pas = armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        self.assertEqual(pas[0]["casier"], [1, 4])

    def test_casier_vu_vide_pas_revisite(self):
        # le robot se souvient des casiers vides, il ne retourne pas les voir
        monde = MondeArmoire(armoire_data)
        memoire = armoire.MemoireArmoire(armoire_data["casier_depart"])
        armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        objet, casier, pas = armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        self.assertEqual([p["action"] for p in pas], ["PRENDRE"])


if __name__ == "__main__":
    unittest.main()
