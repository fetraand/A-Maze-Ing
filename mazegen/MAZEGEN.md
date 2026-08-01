# MAZEGEN.md

> Ce fichier documente uniquement le **package réutilisable `mazegen`**
> (génération et résolution de labyrinthe), conformément à la section
> *"Code reusability requirements"* du sujet. Il est distinct du
> `README.md` principal du projet A-Maze-ing, qui documente le
> programme complet (`a_maze_ing.py`, configuration, algorithme,
> interface, gestion de projet, etc.).

## Sommaire

- [Description](#description)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Paramètres personnalisés](#paramètres-personnalisés)
- [Accéder à la structure générée](#accéder-à-la-structure-générée)
- [Accéder à une solution](#accéder-à-une-solution)
- [Exemple complet](#exemple-complet)
- [Référence de l'API](#référence-de-lapi)
- [Reconstruire le package depuis les sources](#reconstruire-le-package-depuis-les-sources)

## Description

`mazegen` est un package Python autonome qui fournit :

- une classe **`Maze`** capable de générer un labyrinthe (parfait ou
  avec boucles), reproductible via une graine (`seed`) ;
- une fonction **`solve`** qui calcule le plus court chemin entre
  l'entrée et la sortie d'un `Maze` généré (parcours en largeur).

Il est pensé pour être importé tel quel dans n'importe quel projet
Python futur, indépendamment du programme `a_maze_ing.py`.

> **Note** : la structure interne exposée par `Maze` (une grille
> d'entiers représentant les murs de chaque cellule) n'est pas
> nécessairement le même format que le fichier de sortie hexadécimal
> produit par `a_maze_ing.py`. C'est une structure de données pensée
> pour être manipulée directement en mémoire par du code Python.

## Installation

Le package est distribué sous forme de wheel à la racine du dépôt :

```bash
pip install ./mazegen-2.0.0-py3-none-any.whl
```

## Démarrage rapide

```python
pip list

Python3

import mazegen

# 1. Instancier un générateur (labyrinthe 15x12, parfait)
maze = mazegen.Maze(width=15, height=12)

# 2. Générer le labyrinthe à partir d'un point de départ
maze.gen_dfs(start_x=0, start_y=0)

# 3. Afficher la représentation hexadécimale (une ligne par rangée)
print(maze.to_hex_string())
```

## Paramètres personnalisés

Le constructeur `Maze(width, height, seed=None, perfect=True)` accepte :

| Paramètre | Type            | Description                                                          |
|-----------|-----------------|------------------------------------------------------------------------|
| `width`   | `int`           | Largeur du labyrinthe (nombre de cellules).                          |
| `height`  | `int`           | Hauteur du labyrinthe (nombre de cellules).                          |
| `seed`    | `Optional[int]` | Graine de reproductibilité. `None` (défaut) = tirage aléatoire.      |
| `perfect` | `bool`          | `True` (défaut) = un seul chemin possible. `False` = boucles ajoutées.|

```python
# Labyrinthe reproductible (toujours identique avec seed=42)
maze = mazegen.Maze(width=20, height=15, seed=42, perfect=False)
maze.entry = (0, 0)
maze.exit = (19, 14)
maze.gen_dfs(start_x=0, start_y=0)
```

Par défaut, `entry` vaut `(0, 0)` et `exit` vaut
`(width - 1, height - 1)` ; ils peuvent être réassignés avant l'appel
à `gen_dfs` (toute coordonnée doit rester dans les bornes du
labyrinthe et différente l'une de l'autre).

## Accéder à la structure générée

Après génération, l'objet `Maze` expose :

| Attribut         | Type                | Description                                                        |
|------------------|---------------------|----------------------------------------------------------------------|
| `maze.grid`      | `List[List[int]]`  | Grille `[y][x]` : chaque cellule est un entier 0-15 codant ses murs. |
| `maze.width`     | `int`               | Largeur du labyrinthe.                                                |
| `maze.height`    | `int`               | Hauteur du labyrinthe.                                                |
| `maze.entry`     | `Tuple[int, int]`  | Coordonnées `(x, y)` de l'entrée.                                     |
| `maze.exit`      | `Tuple[int, int]`  | Coordonnées `(x, y)` de la sortie.                                    |
| `maze.perfect`   | `bool`              | Indique si le labyrinthe est parfait.                                 |
| `maze.is_generated` | `bool`           | `True` une fois `gen_dfs` exécuté avec succès.                        |

Chaque valeur de `maze.grid[y][x]` est un masque binaire : le bit vaut
`1` si le mur correspondant est fermé, `0` s'il est ouvert.

```python
Maze.LINE_N  # 1 (bit 0) — mur nord
Maze.LINE_E  # 2 (bit 1) — mur est
Maze.LINE_S  # 4 (bit 2) — mur sud
Maze.LINE_W  # 8 (bit 3) — mur ouest
```

```python
cell = maze.grid[0][0]
if cell & mazegen.Maze.LINE_E:
    print("Mur fermé à l'est de la cellule (0, 0)")
```

## Accéder à une solution

La fonction `mazegen.solve(maze)` retourne le plus court chemin entre
`maze.entry` et `maze.exit`, sous forme de liste de coordonnées
`(x, y)` :

```python
path = mazegen.solve(maze)
print(path)
# [(0, 0), (0, 1), (1, 1), ..., (19, 14)]
```

Elle lève une `RuntimeError` si le labyrinthe n'a pas encore été
généré (`maze.is_generated is False`), ou s'il n'existe aucun chemin
entre l'entrée et la sortie.

## Exemple complet

```python
import mazegen

maze = mazegen.Maze(width=15, height=12, seed=42, perfect=True)
maze.entry = (0, 0)
maze.exit = (14, 11)
maze.gen_dfs(start_x=0, start_y=0)

print(maze.to_hex_string())

path = mazegen.solve(maze)
print(f"Chemin trouvé en {len(path)} étapes : {path}")
```

## Référence de l'API

### `class mazegen.Maze(width, height, seed=None, perfect=True)`

| Méthode                              | Description                                                                 |
|---------------------------------------|------------------------------------------------------------------------------|
| `gen_dfs(start_x=0, start_y=0)`      | Génère le labyrinthe (parcours en profondeur itératif) depuis ce point.     |
| `break_wall(x1, y1, x2, y2)`          | Casse le mur entre deux cellules adjacentes (utilisé en interne).          |
| `to_hex_string()`                     | Retourne la grille sous forme de chaîne hexadécimale (une ligne par rangée).|
| `display_ascii(path=None)`            | Affiche le labyrinthe en ASCII sur la sortie standard.                     |

### `mazegen.solve(maze: Maze) -> List[Tuple[int, int]]`

Calcule le plus court chemin entre `maze.entry` et `maze.exit` par
parcours en largeur (BFS).

## Reconstruire le package depuis les sources

Le package est reconstructible à tout moment depuis `pyproject.toml`
et le dossier `mazegen/` à la racine du dépôt :

```bash
python3 -m venv env
source env/bin/activate
pip install build
python -m build
# -> dist/mazegen-2.0.0-py3-none-any.whl
# -> dist/mazegen-2.0.0.tar.gz
```
