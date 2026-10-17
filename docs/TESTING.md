# TESTING

## Backend (depuis le dossier backend)
- Lancer les tests : .venv\Scripts\python.exe -m pytest -v
- Lancer l'API : .venv\Scripts\python.exe -m uvicorn app.main:app --reload
- Swagger : http://127.0.0.1:8000/docs
- Migrations : .venv\Scripts\alembic.exe upgrade head ; .venv\Scripts\alembic.exe current
- Prérequis : fichier backend/.env présent (modèle : backend/.env.example) et PostgreSQL démarré.

## Angular (depuis le dossier web)
- Compiler : ng build customer-site ; ng build merchant-portal ; ng build admin-dashboard
- Lancer : ng serve customer-site (http://localhost:4200)

## Flutter (depuis mobile\customer_app puis mobile\driver_app)
- flutter analyze
- flutter test
- flutter run (avec un émulateur ou un téléphone connecté)

## Règle
Une tâche n'est cochée dans PROGRESS.md qu'après exécution réelle des commandes qui la concernent.

## Tests avec base de données (depuis T3.4a)
- PostgreSQL doit tourner et backend/.env doit exister : les tests d'API utilisent la base de développement dans une transaction annulée (aucune donnée conservée).
- Commande : .venv\Scripts\python.exe -m pytest -v (24 tests attendus après T3.4a)
- Après T3.4b : 36 tests attendus (users en base : 1 = l'utilisateur de test créé à la main en T3.4a).
