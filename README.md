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

## Déploiement sur Render.com (avec Docker)

1. Poussez ce dépôt vers GitHub/GitLab/Bitbucket.
2. Sur Render, créez un nouveau service Web, connectez le dépôt et choisissez **Docker** comme environnement d'exécution.
3. Render utilisera automatiquement le `Dockerfile` présent à la racine. Aucune commande de build/start supplémentaire n'est nécessaire.
4. Conservez les valeurs par défaut pour les variables d'environnement ; la variable `PORT` fournie par Render est gérée dans l'image (`CMD` exploite `${PORT:-8000}`).
5. Déployez : Render construira l'image, lancera Uvicorn et exposera l'app sur votre URL publique.
