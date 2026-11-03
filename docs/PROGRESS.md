# PROGRESS

## Terminé (vérifié sur le dépôt réel le 2026-10-17)
### Phase 1 : analyse et architecture
- T1.1 à T1.5 : exigences, rôles, architecture, plan, documents
### Phase 2 : mise en place
- T2.1 à T2.9 : Git, prérequis, FastAPI, configuration, PostgreSQL, Alembic, Angular, Flutter, pytest
### Phase 3 : fondations backend
- T3.0 Décisions métier (52a99e3) ; T3.1 Conception de la base (3e6ab69)
- T3.2 Modèles users, refresh_tokens, admins, customers + migration 792c3e1c2311
- T3.3 Hachage Argon2, JWT, refresh tokens
- T3.4a Inscription client ; T3.4b Connexion, refresh avec rotation, déconnexion
- T3.5 Utilisateur courant, RBAC, GET /users/me
- T3.6 Erreurs centralisées (dc7fba2) : 56 tests passent
- Étiquette Git : backup-avant-mvp

## Abandonnées pour le MVP
- T3.7 Journal d'audit, T3.8 Documentation OpenAPI détaillée

## En cours
- MVP-0 : fusion de T3.6, étiquette de sauvegarde, plan MVP (branche dev)

## À venir
- Jour 1 : M1 Commerçants et livreurs (voir docs/PROJECT_PLAN.md)

## Notes
- Anciennes versions des documents : docs/archive/
- Le mot de passe de la base et la SECRET_KEY sont uniquement dans backend/.env (ignoré par Git).
- Base de développement : 1 utilisateur de test (yassmine@example.com, rôle customer).
- Avertissement à traiter plus tard : starlette.testclient signale que httpx est déprécié.
