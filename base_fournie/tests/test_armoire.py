import unittest
import reconfort_io as rio
from robot import armoire
from monde.monde_armoire import MondeArmoire

armoire_data = rio.charger_armoire("donnees/armoire_standard.json")


def nouvelle_fouille(emotion, intensite, donnees=armoire_data):
    memoire = armoire.MemoireArmoire(donnees["casier_depart"])
    return armoire.fouiller_armoire(emotion, intensite, memoire, MondeArmoire(donnees))


def armoire_test(objets, casier_depart=(1, 0)):
    """Fabrique une armoire de 24 casiers, tous vides sauf ceux donnes dans
    objets : {(ligne, colonne): "nom de l'objet"}. Sert pour les cas qu'on ne
    peut pas obtenir avec l'armoire standard."""
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

    # --- deplacement du selecteur (enonce section 8, point 4) ---

    def test_chemin_directions_exemples_annexe(self):
        # les trois exemples du tableau de l'annexe C.3
        self.assertEqual(armoire.chemin_vers((1, 0), (1, 4)), ["E", "E", "E", "E"])
        self.assertEqual(armoire.chemin_vers((2, 7), (0, 1)), ["N", "N", "E", "E"])
        self.assertEqual(armoire.chemin_vers((1, 0), (2, 6)), ["S", "O", "O"])

    def test_bouclage_colonne_7_vers_0(self):
        self.assertEqual(armoire.chemin_vers((1, 7), (1, 0)), ["E"])
        self.assertEqual(armoire.deplacer_selecteur((1, 7), "E"), (1, 0))

    def test_bouclage_colonne_0_vers_7(self):
        self.assertEqual(armoire.chemin_vers((1, 0), (1, 7)), ["O"])
        self.assertEqual(armoire.deplacer_selecteur((1, 0), "O"), (1, 7))

    def test_lignes_ne_bouclent_pas(self):
        with self.assertRaises(ValueError):
            armoire.deplacer_selecteur((0, 3), "N")
        with self.assertRaises(ValueError):
            armoire.deplacer_selecteur((2, 3), "S")

    # --- regle de repli (enonce section 8, point 5) ---

    def test_fouille_trouve_objet_exact(self):
        # casier exact garni
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne")
        self.assertEqual(objet, "couverture")
        self.assertEqual(armoire.determiner_repli(casier), "aucun")

    def test_repli_intensite(self):
        # armoire standard : anticipation/forte est vide, anticipation/moyenne est garni
        objet, casier, pas = nouvelle_fouille("anticipation", "forte")
        self.assertEqual(objet, "calendrier")
        self.assertEqual(armoire.determiner_repli(casier), "intensite")
        self.assertEqual([casier["ligne"], casier["colonne"]], [1, 7])

    def test_fouille_repli(self):
        # colonne surprise entierement vide : repli sur une voisine
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        self.assertEqual(objet, "telephone")
        self.assertEqual(armoire.determiner_repli(casier), "voisine_1")

    def test_armoire_vide(self):
        vide = {"casier_depart": [1, 0], "casiers": []}
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne", vide)
        self.assertIsNone(objet)

    def test_aucun_casier_garni_a_distance_2(self):
        # impossible avec l'armoire standard : seuls joie (distance 4) et
        # confiance (distance 3) sont garnis, ils ne doivent jamais etre utilises
        donnees = armoire_test({(1, 0): "ballon", (1, 1): "livre"})
        memoire = armoire.MemoireArmoire(donnees["casier_depart"])
        objet, casier, pas = armoire.fouiller_armoire("tristesse", "moyenne", memoire, MondeArmoire(donnees))
        self.assertIsNone(objet)
        self.assertIsNone(casier)
        # avant d'abandonner, le robot a bien regarde les 15 candidats
        for c in armoire.casiers_candidats("tristesse", "moyenne"):
            self.assertTrue(memoire.deja_vu(armoire.position_casier(c["emotion"], c["intensite"])))

    # --- ordre des candidats (enonce section 6.2) ---

    def test_ordre_candidats_annexe(self):
        # annexe C.5 : surprise/forte donne d'abord ces 5 casiers, dans cet ordre
        tries = armoire.trier_candidats(armoire.casiers_candidats("surprise", "forte"))
        premiers = [armoire.position_casier(c["emotion"], c["intensite"]) for c in tries[:5]]
        self.assertEqual(premiers, [(2, 3), (1, 3), (0, 3), (2, 4), (2, 2)])

    def test_intensite_faible_avant_forte(self):
        # critere 3 : a ecart egal, l'intensite la plus faible d'abord.
        # impossible avec l'armoire standard (il faut faible ET forte garnis)
        donnees = armoire_test({(0, 4): "plaid", (2, 4): "telephone"})
        objet, casier, pas = nouvelle_fouille("tristesse", "moyenne", donnees)
        self.assertEqual(objet, "plaid")

    def test_ordre_prime_sur_ce_qu_on_croise(self):
        # section 6.2 / annexe C.5 : on passe devant peur/forte (garni),
        # mais on doit prendre tristesse/forte, plus prioritaire
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        self.assertIn([2, 2], [p["casier"] for p in pas])
        self.assertEqual([casier["ligne"], casier["colonne"]], [2, 4])

    # --- perception et memoire de l'armoire (sections 4, 5.5 et 7) ---

    def test_contenu_casier_correspond_a_la_realite(self):
        # section 5.5 : contenu_casier est verifie, une perception fausse est une erreur
        monde = MondeArmoire(armoire_data)
        objet, casier, pas = nouvelle_fouille("surprise", "forte")
        for p in pas:
            self.assertEqual(p["contenu_casier"], monde.regarder(p["casier"]))

    def test_selecteur_garde_sa_position(self):
        # section 4 : la position du selecteur persiste d'une demande a l'autre
        monde = MondeArmoire(armoire_data)
        memoire = armoire.MemoireArmoire(armoire_data["casier_depart"])
        armoire.fouiller_armoire("tristesse", "moyenne", memoire, monde)
        objet, casier, pas = armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        self.assertEqual(pas[0]["casier"], [1, 4])

    def test_casier_vu_vide_pas_revisite(self):
        # section 7 : la memoire garde ce que le robot a deja vu dans l'armoire
        monde = MondeArmoire(armoire_data)
        memoire = armoire.MemoireArmoire(armoire_data["casier_depart"])
        armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        objet, casier, pas = armoire.fouiller_armoire("surprise", "forte", memoire, monde)
        self.assertEqual([p["action"] for p in pas], ["PRENDRE"])


if __name__ == "__main__":
    unittest.main()
