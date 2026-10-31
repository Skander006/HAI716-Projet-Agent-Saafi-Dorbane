# Robot de réconfort — SAAFI & DORBANE

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : *Python* — Version : *Python 3.12*

## Lancer

Depuis base_fournie
```
python main.py <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json>
```

Exemple :

```
python main.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json
```
ou aussi si on veut voir l'affichage :

```
python main.py cartes/appartement_01.json cartes/scenario_01.json donnees sortie.json --afficher
```
Dépendances : aucune bibliothèque externe nécessaire pour exécuter le programme. Python 3.12 est recommandé.

## Tester

Installer `pytest` si necessaire
```
python -m pip install pytest
```
Lancer les tests depuis `base_fournie` :

```
python -m pytest -v
```

*Les tests couvrent la validation des fichiers JSON, la perception locale, la carte mémoire, le calcul des chemins BFS, la replanification, les déplacements, l'identification des émotions, la recherche dans l'armoire et plusieurs comportements du robot.*

## Organisation du code

| Fichier | Rôle |
|---|---|
| `base_fournie/main.py` | Point d'entrée, initialisation et exécution des scénarios |
| `base_fournie/robot/agent.py` | Boucle de décision et coordination des actions |
| `base_fournie/robot/perception.py` | Perception locale de l'environnement |
| `base_fournie/robot/memoire.py` | Gestion de la carte mémoire et de l'état du robot |
| `base_fournie/robot/decision.py` | Planification et choix des actions |
| `base_fournie/robot/action.py` | Exécution des actions du robot |
| `base_fournie/robot/emotions.py` | Reconnaissance des émotions et des intensités |
| `base_fournie/robot/armoire.py` | Recherche et sélection des objets de réconfort |
| `base_fournie/robot/affichage.py` | Gère l'affichage de la grille, les actions du robot et tout ce qui est visuel à chaque tour|
| `base_fournie/deplacements/deplacements.py` | Calcul des chemins BFS et déplacements |
| `base_fournie/monde/monde_armoire.py` | Simulation de l'armoire et de ses casiers |
| `base_fournie/monde/monde_appartement.py` | Simulation de l'appartement |
| `base_fournie/validation/armoire_dictionnaire.py` | Validation du dictionnaire et des armoires |
| `base_fournie/validation/carte.py` | Validation des cartes d'appartement |
| `base_fournie/validation/fichiers.py` | Validation de tous les fichiers d'entrées en appelant les resultats des autres fichiers de validation |
| `base_fournie/reconfort_io.py` | Chargement des fichiers et génération des traces JSON |
| `base_fournie/tests` | Tests unitaires et tests d'intégration |
| `base_fournie/cartes` | Fichiers de cartes fournis |
| `base_fournie/donnees` | Fichiers de données de dictionnaire et d'armoire fournis |
| `base_fournie/rendu.json` | Configuration de lancement pour le correcteur |

## État

**Ce qui marche.**
Les 5 cartes fournies : toutes les demandes sont livrées, et la trace rejouée contre la réalité ne contient aucune erreur. Le robot replanifie à chaque pas quand il découvre un mur. Le résident muré est détecté (le BFS échoue sur la carte mentale, où les cases inconnues sont supposées libres : c'est une preuve, annexe B.6), et la demande suivante continue normalement. Une armoire vide donne « armoire vide » après avoir regardé les 15 casiers. Les fichiers cassés de la section 5.6 sont refusés avec un message clair, un code de retour 1 et sans trace.
Le robot suit l'ordre de la section 4 : dictionnaire, armoire, résident. Les échecs n'utilisent que les trois motifs de l'énoncé.
**Ce qui ne marche pas.** 
Résident muré découvert après PRENDRE : le robot garde l'objet dans les mains, car aucune action ne permet de le poser. Pour la suite :
s'il a déjà la preuve qu'un résident est muré, il ne prend rien pour lui ;
à la demande suivante, si l'objet choisi est celui qu'il porte déjà, il le donne sans PRENDRE ;
sinon il ne peut rien prendre (un seul objet à la fois) et la demande échoue avec le motif « armoire vide ». L'énoncé ne prévoit pas ce cas : c'est le choix le plus proche qu'on a trouvé.
Dictionnaire ou armoire murés : l'énoncé ne prévoit pas de motif. On note « emotion indeterminee » (le robot n'a pas pu lire l'émotion) ou « armoire vide » (il n'a pas pu prendre d'objet).
Le robot recalcule tout le BFS à chaque pas (et meilleure_destination fait un BFS pour chacune des 4 cases autour de la cible). C'est simple et rapide sur nos cartes, mais ça recalcule beaucoup.
Dans l'armoire, le sélecteur bouge toujours d'abord verticalement, puis horizontalement. Il repasse parfois devant des casiers déjà vus vides (comme dans l'annexe C.5).
## Vidéo

`video/demo.mp4` , également déclarée dans `base_fournie/rendu.json`.
