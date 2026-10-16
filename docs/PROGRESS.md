# PROGRESS

## Terminé
- T1.1 Extraction des exigences
- T1.2 Rôles (brouillon)
- T1.3 Architecture
- T1.5 Feuille de route et documents
- T2.1 Dossier du projet, Git, .gitignore, documents
- T2.2 Vérification des prérequis et versions figées
- T2.3 Backend FastAPI minimal + /health
- T2.4 Configuration par variables d'environnement
- T2.5 PostgreSQL (delivery_db / delivery_user) et connexion SQLAlchemy
- T2.6 Alembic configuré, migration initiale appliquée (9cc8576c03f7)
- T2.7 Workspace Angular, 3 apps compilées (ac732b5)
- T2.8 Apps Flutter customer_app et driver_app (analyze + test OK ; customer_app lancée sur émulateur Android)

## En cours
- T2.9 Test pytest pour /health

## Bloqué
- Rien

## Notes
- Lancer l'API depuis backend/ : .venv\Scripts\python.exe -m uvicorn app.main:app --reload
- Le mot de passe de la base est uniquement dans backend/.env (ignoré par Git).
- Phase 2 presque terminée : il reste T2.9.

## À venir
- Phase 3 : T3.1 conception détaillée de la base, puis modèles, auth, RBAC
