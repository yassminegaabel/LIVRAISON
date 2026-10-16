# PROGRESS

## Terminé
### Phase 1 : analyse et architecture
- T1.1 Exigences, T1.2 Rôles (brouillon), T1.3 Architecture, T1.5 Feuille de route et documents
### Phase 2 : mise en place (terminée)
- T2.1 Git et documents
- T2.2 Prérequis et versions figées
- T2.3 Backend FastAPI + /health
- T2.4 Configuration par variables d'environnement
- T2.5 PostgreSQL (delivery_db / delivery_user) et SQLAlchemy
- T2.6 Alembic, migration initiale 9cc8576c03f7
- T2.7 Workspace Angular, 3 apps compilées
- T2.8 Apps Flutter customer_app et driver_app
- T2.9 Test pytest /health (2 passed, commit 5beabb8)

## En cours
- T3.0 Confirmer les décisions métier (Q1, Q3 à Q6) avant la conception de la base
- T3.1 Conception détaillée de la base de données (docs/DATABASE.md)

## Bloqué
- Rien

## Notes
- Avertissement à traiter plus tard : starlette.testclient signale que httpx est déprécié (les tests passent).
- Le mot de passe de la base est uniquement dans backend/.env (ignoré par Git).

## À venir
- T3.2 modèles utilisateurs/rôles, T3.3 hash + JWT, T3.4 inscription/connexion, T3.5 RBAC
