*This project has been created as part of the 42 curriculum by hasandri, fetraand.*

# A-Maze-ing

## Sommaire

- [Description](#description)
- [Instructions](#instructions)
- [Fichier de configuration](#fichier-de-configuration)
- [Format du fichier de sortie](#format-du-fichier-de-sortie)
- [Fonctionnalités et interactions](#fonctionnalités-et-interactions)
- [Algorithme de génération](#algorithme-de-génération)
- [Partie réutilisable du code](#partie-réutilisable-du-code)
- [Structure du projet](#structure-du-projet)
- [Équipe et gestion de projet](#équipe-et-gestion-de-projet)
- [Ressources](#ressources)

## Description

A-Maze-ing est un générateur de labyrinthes écrit en Python. À partir d'un
fichier de configuration, le programme génère un labyrinthe — parfait
(un seul chemin possible entre l'entrée et la sortie) ou imparfait
(avec des boucles) — l'affiche dans le terminal avec un rendu coloré, et
écrit le résultat dans un fichier au format hexadécimal.

Chaque labyrinthe contient un motif « 42 » dessiné par des cellules
entièrement fermées, et le programme calcule systématiquement le plus
court chemin entre l'entrée et la sortie.

Le cœur du projet (génération et résolution) est isolé dans un package
Python autonome, `mazegen`, installable via pip et réutilisable dans
n'importe quel projet futur.

**Objectifs pédagogiques couverts :** algorithmes de parcours de graphe,
arbres couvrants, manipulation de masques binaires, packaging Python,
typage statique et gestion rigoureuse des erreurs.

## Instructions

### Prérequis

- Python 3.10 ou supérieur
- `make`

### Installation

Il est recommandé de travailler dans un environnement virtuel :

```bash
python3 -m venv .env
source .env/bin/activate
```

Installer les dépendances de développement :

```bash
make install
```

Le package `mazegen` doit également être installé pour que le programme
principal fonctionne :

```bash
pip install ./mazegen-2.0.0-py3-none-any.whl
```

### Exécution

```bash
make run
```

ou directement, avec le fichier de configuration de votre choix :

```bash
python3 a_maze_ing.py config.txt
python3 a_maze_ing.py mon_autre_config.txt
```

Le nom du fichier de configuration est libre : il est lu depuis
l'argument de la ligne de commande.

### Autres règles disponibles

| Commande             | Effet                                                                 |
|----------------------|-------------------------------------------------------------------------|
| `make run`           | Lance le programme avec `config.txt`.                                 |
| `make debug`         | Lance le programme sous le débogueur `pdb`.                           |
| `make lint`          | Exécute `flake8` et `mypy` avec les options requises.                 |
| `make lint-strict`   | Exécute `flake8` et `mypy --strict`.                                  |
| `make clean`         | Supprime les fichiers générés et les caches.                          |
| `make build-mazegen` | Reconstruit le package `mazegen` (`.whl` et `.tar.gz`) depuis les sources. |

## Fichier de configuration

Le fichier de configuration est un fichier texte contenant une paire
`CLÉ=VALEUR` par ligne. Les lignes vides sont ignorées, et tout ce qui
suit un `#` est traité comme un commentaire (ligne entière ou fin de
ligne).

Toute ligne ne respectant pas le format `CLÉ=VALEUR`, ainsi que toute
clé dupliquée, rend la configuration invalide.

### Clés obligatoires

| Clé           | Description                                | Exemple                |
|---------------|--------------------------------------------|------------------------|
| `WIDTH`       | Largeur du labyrinthe (en cellules)        | `WIDTH=20`             |
| `HEIGHT`      | Hauteur du labyrinthe (en cellules)        | `HEIGHT=15`            |
| `ENTRY`       | Coordonnées de l'entrée `(x,y)`            | `ENTRY=0,0`            |
| `EXIT`        | Coordonnées de la sortie `(x,y)`           | `EXIT=19,14`           |
| `OUTPUT_FILE` | Nom du fichier de sortie                   | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | Labyrinthe parfait ou non                  | `PERFECT=True`         |

### Clé optionnelle

| Clé    | Description                                              | Exemple   |
|--------|----------------------------------------------------------|-----------|
| `SEED` | Graine de reproductibilité. Absente ou `None` = aléatoire | `SEED=42` |

Lorsqu'une graine est définie, le labyrinthe reste **strictement
identique** à chaque régénération et à chaque relancement du programme.
Les valeurs négatives sont refusées : Python ignore le signe d'une graine entière,
une graine négative produirait donc exactement le même labyrinthe que sa valeur absolue, ce qui serait trompeur.

### Exemple complet

```ini
# Configuration par défaut
WIDTH=11
HEIGHT=9
ENTRY=0,0
EXIT=10,8
OUTPUT_FILE=maze.txt
PERFECT=True
```

### Contraintes validées

- Dimensions comprises entre `11x9` et `50x45`. Le minimum de `11x9` correspond à la place nécessaire pour accueillir le motif « 42 » ; 
  en dessous, le programme s'arrête avec un message d'erreur explicite.
- `ENTRY` et `EXIT` doivent être dans les limites du labyrinthe et
  différentes l'une de l'autre.
- `PERFECT` accepte `True`/`1`/`yes` ou `False`/`0`/`no`
  (insensible à la casse).
- Le labyrinthe doit mesurer au minimum `11x9` pour accueillir le motif
  « 42 » ; en dessous, le programme s'arrête avec un message d'erreur
  explicite.

Toute erreur de configuration (fichier introuvable, clé manquante,
valeur hors limites, syntaxe invalide…) est signalée par un message
clair, sans jamais provoquer de plantage.

## Format du fichier de sortie

Le labyrinthe est écrit avec un chiffre hexadécimal par cellule, où
chaque bit indique si le mur correspondant est **fermé** (`1`) ou
**ouvert** (`0`) :

| Bit       | Direction |
|-----------|-----------|
| 0 (LSB)   | Nord      |
| 1         | Est       |
| 2         | Sud       |
| 3         | Ouest     |

Les cellules sont écrites ligne par ligne. Après une ligne vide,
trois lignes supplémentaires sont ajoutées : les coordonnées de
l'entrée, celles de la sortie, puis le plus court chemin exprimé avec
les lettres `N`, `E`, `S`, `W`.

```
D546C7C4556

0,0
10,8
EEEEEESEENEESSSWSSSSWWSEEE
```

## Fonctionnalités et interactions

Le labyrinthe est affiché dans le terminal en ASCII coloré : murs,
entrée (🐥), sortie (🐛), motif « 42 » et chemin solution.

| Touche | Action                                                   |
|--------|----------------------------------------------------------|
| `r`    | Régénérer un nouveau labyrinthe                          |
| `t`    | Changer la taille du labyrinthe                          |
| `h`    | Afficher/masquer le chemin (avec animation pas à pas)    |
| `g`    | Activer le mode joueur                                   |
| `e`    | Changer les coordonnées de l'entrée                      |
| `o`    | Changer les coordonnées de la sortie                     |
| `2`    | Changer la couleur des murs                              |
| `4`    | Changer la couleur du motif « 42 »                       |
| `6`    | Changer la couleur de fond                               |
| `q`    | Quitter le programme                                     |

### Fonctionnalités avancées

- **Mode joueur (`g`)** : déplacement manuel du personnage au clavier
  (flèches directionnelles) via une interface `curses`, avec détection
  de victoire à l'arrivée sur la sortie.
- **Animation du chemin (`h`)** : résolution affichée pas à pas.
- **Animations de démarrage et de fermeture** du programme.
- **Validation à chaud** : tout changement d'entrée, de sortie ou de
  taille est vérifié avant d'être appliqué. Si le labyrinthe devenait
  insoluble (par exemple si la nouvelle coordonnée tombe dans le motif
  « 42 »), le changement est annulé et l'état précédent est restauré.

## Algorithme de génération

### L'algorithme choisi : parcours en profondeur avec retour arrière

La génération repose sur un **DFS itératif avec backtracking**
(*recursive backtracker*), implémenté avec une pile explicite plutôt
qu'avec de la récursion.

Le principe : partir de la cellule d'entrée, choisir aléatoirement une
cellule voisine non visitée, casser le mur qui les sépare, puis
recommencer depuis cette nouvelle cellule. Quand une impasse est
atteinte (aucun voisin non visité), on remonte la pile jusqu'à trouver
une cellule ayant encore des voisins inexplorés.

### Pourquoi ce choix

- **Il produit naturellement un labyrinthe parfait.** Le résultat est un
  arbre couvrant : par définition, un arbre ne contient aucun cycle,
  donc il existe exactement un chemin entre deux cellules quelconques.
  L'exigence `PERFECT=True` est ainsi satisfaite par construction, sans
  vérification supplémentaire.
- **Il garantit l'absence de cellule isolée**, puisque chaque cellule
  atteignable est visitée exactement une fois.
- **Il exclut d'office les grandes zones ouvertes.** Une zone `3x3`
  entièrement ouverte nécessiterait des cycles, impossibles dans un
  arbre. La contrainte « pas de couloir plus large que 2 cellules » est
  donc respectée automatiquement.
- **Il génère des labyrinthes visuellement intéressants**, avec de longs
  couloirs sinueux, contrairement à d'autres approches qui produisent des
  motifs plus reconnaissables.
- **Sa version itérative évite tout risque de dépassement de pile** sur
  les grands labyrinthes, contrairement à l'implémentation récursive.

### Le mode imparfait

Lorsque `PERFECT=False`, des murs supplémentaires sont cassés
aléatoirement après la génération pour créer des boucles et donc
plusieurs chemins possibles. Chaque mur cassé est vérifié
individuellement : s'il créait une zone `3x3` entièrement ouverte, il
est immédiatement refermé et une autre position est tirée. Un contrôle
final parcourt l'ensemble de la grille pour garantir qu'aucune zone
interdite n'a pu se former.

### Le motif « 42 »

Le motif est inscrit **avant** la génération, sous forme de cellules
totalement fermées marquées comme déjà visitées. Le parcours les
contourne donc naturellement, sans jamais casser leurs murs. Une
vérification empêche de placer l'entrée ou la sortie à l'intérieur du
motif.

### La résolution

Le plus court chemin est calculé par un **parcours en largeur (BFS)**.
Ce choix est motivé par une propriété du BFS : dans un graphe non
pondéré — ce qui est le cas ici, chaque déplacement entre cellules
voisines ayant le même coût — le premier chemin trouvé vers la sortie
est nécessairement le plus court. Un DFS, lui, trouverait *un* chemin,
mais pas forcément le plus court.

## Partie réutilisable du code

Le package `mazegen` regroupe toute la logique de génération et de
résolution, indépendamment de l'interface en ligne de commande. Il est
distribué sous forme de wheel installable :

```bash
pip install ./mazegen-2.0.0-py3-none-any.whl
```

```python
import mazegen

maze = mazegen.Maze(width=15, height=12, seed=42, perfect=True)
maze.entry = (0, 0)
maze.exit = (14, 11)
maze.gen_dfs(start_x=0, start_y=0)

print(maze.to_hex_string())

path = mazegen.solve(maze)
print(f"Chemin trouvé en {len(path)} étapes")
```

Le package expose :

- `mazegen.Maze` — la classe de génération, avec ses paramètres
  (`width`, `height`, `seed`, `perfect`), sa structure accessible
  (`grid`, `entry`, `exit`, `width`, `height`) et ses méthodes
  (`gen_dfs`, `to_hex_string`, `display_ascii`, `break_wall`) ;
- `mazegen.solve` — le calcul du plus court chemin.

Le générateur n'écrit rien sur le disque et n'affiche rien de lui-même :
il expose une structure de données en mémoire, que le programme
appelant est libre d'utiliser comme il l'entend. Cette structure interne
(une grille d'entiers) est volontairement distincte du format
hexadécimal du fichier de sortie.

Le reste du code (lecture de la configuration, couleurs, animations,
écriture du fichier de sortie) est spécifique au programme
`a_maze_ing.py` et reste donc en dehors du package.

**La documentation détaillée du package se trouve dans
[`mazegen/MAZEGEN.md`](mazegen/MAZEGEN.md).**

### Reconstruire le package

```bash
make build-mazegen
```

## Structure du projet

```
.
├── mazegen/                         # Package réutilisable
│   ├── __init__.py                  # Expose Maze et solve
│   ├── maze_gen.py                  # Classe Maze (génération)
│   ├── MAZEGEN.md                   # Documentation du package
│   └── solver.py                    # Résolution (BFS)
├── .gitignore
├── a_maze_ing.py                    # Programme principal
├── animation.py                     # Animations et mode joueur
├── color.py                         # Couleurs ANSI et affichage
├── config.txt                       # Configuration par défaut
├── Makefile
├── mazegen-2.0.0-py3-none-any.whl   # Package construit
├── parsing.py                       # Lecture et validation de la config
├── pyproject.toml
├── README.md
├── requirements.txt
└── to_maze_txt.py                   # Écriture du fichier de sortie
```

## Équipe et gestion de projet

### Rôles

| Membre     | Périmètre                                                                                                |
|------------|----------------------------------------------------------------------------------------------------------|
| `hasandri` | Package `mazegen` (génération, résolution, packaging), `pyproject.toml`, `Makefile`.                     |
| `fetraand` | Programme principal `a_maze_ing.py`, parsing de la configuration, affichage coloré, animations et mode joueur, écriture du fichier de sortie. |

Cette répartition a permis de travailler en parallèle : l'interface
d'un côté, le moteur de l'autre, avec l'API du package `Maze` comme
point de contact entre les deux.

### Planning

> *À compléter : planning initial prévu et son évolution réelle.*

### Bilan

> *À compléter : ce qui a bien fonctionné et ce qui pourrait être
> amélioré.*

### Outils utilisés

- **Python 3.10+** et environnements virtuels (`venv`)
- **flake8** (avec le plugin `flake8-docstrings`) pour le style de code
  et la conformité des docstrings
- **mypy** pour le typage statique, y compris en mode `--strict`
- **build** et **setuptools/poetry-core** pour la construction du package
- **Git / GitHub** pour le versionnement
- **VS Code** comme éditeur, avec l'extension autoDocstring
- **Make** pour l'automatisation des tâches courantes

## Ressources

### Documentation et articles

- [Maze generation algorithm — Wikipédia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Spanning tree — Wikipédia](https://en.wikipedia.org/wiki/Spanning_tree)
- [Breadth-first search — Wikipédia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Buckblog — Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Documentation du module `typing`](https://docs.python.org/3/library/typing.html)
- [Documentation du module `curses`](https://docs.python.org/3/howto/curses.html)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [Documentation mypy](https://mypy.readthedocs.io/)

### Utilisation de l'IA

L'IA a été utilisée comme outil d'aide à la conception et au débogage,
et non comme générateur de code livré tel quel. Concrètement :

- **Aide à la conception** : discussion des algorithmes envisageables
  pour la génération (DFS avec backtracking, Prim, Kruskal) et pour la
  résolution (BFS vs DFS), afin de comprendre leurs propriétés
  respectives et de justifier nos choix ; réflexion sur l'organisation
  du code entre le package réutilisable et le programme principal.
- **Débogage** : identification de cas limites et de comportements
  inattendus — gestion des labyrinthes trop petits pour le motif « 42 »,
  cohérence de l'état interne après un changement de taille ou de
  coordonnées, robustesse face aux fichiers de configuration invalides
  et aux fichiers de sortie inaccessibles.
- **Relecture de conformité** : vérification du respect des consignes du
  sujet, des règles `flake8`/`mypy` et de la validité du format du
  fichier de sortie.

Chaque suggestion a été relue, testée et adaptée à notre code. Nous
sommes en mesure d'expliquer et de justifier l'intégralité du code
présent dans ce dépôt.