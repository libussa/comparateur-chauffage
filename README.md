> ⚠️ Cette application a été conçue quasi intégralement par une IA

# Comparateur de chauffage

Application web en une page permettant d'estimer les coûts de chauffage entre plusieurs scénarios :

- chaudière neuve avec soutien du poêle à bois,
- chaudière neuve seule,
- radiateurs électriques + poêle,
- radiateurs électriques seuls,
- situation actuelle (chaudière existante + poêle) pour référence.

Les paramètres (consommations, rendements, prix, inflation, investissements, durée d'étude) sont entièrement modifiables pour estimer les budgets annuels, comparer les investissements et visualiser les temps de rentabilité croisée entre scénarios. Le surcoût d'abonnement électrique lié à l'augmentation de puissance peut également être simulé avec sa propre inflation, et chaque simulation peut être partagée via l'URL générée automatiquement.

## Prérequis

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installé (facultatif mais recommandé)

## Installation locale

```bash
uv venv
source .venv/bin/activate
uv pip install .
uvicorn app.main:app --reload
```

L'application est ensuite accessible sur http://127.0.0.1:8000.

## Via Docker Compose

```bash
docker compose up --build
```

Le service web est exposé sur http://127.0.0.1:8000.

## Tests

```bash
uv pip install .[dev]
pytest
```

Les tests vérifient notamment les calculs énergétiques, l'application du surcoût d'abonnement électrique et les statuts de rentabilité.

## Déploiement sur Render.com (sans Docker)

1. Poussez ce dépôt vers GitHub/GitLab/Bitbucket.
2. Sur Render, créez un nouveau service Web, choisissez le dépôt, et sélectionnez l'option **Python**.
3. Laissez Render utiliser la configuration fournie :
   - commande de build : `pip install -r requirements.txt`
   - commande de démarrage : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. (Facultatif) Si vous préférez l'infra-as-code, conservez le fichier `render.yaml` inclus : Render le détecte automatiquement et applique les paramètres ci-dessus.

> Render fournit automatiquement la variable d'environnement `PORT`. Aucun autre réglage n'est requis pour cette application.
