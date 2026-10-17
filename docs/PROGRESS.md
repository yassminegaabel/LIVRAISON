# PROGRESS

## Terminé
### Phase 1 : analyse et architecture
- T1.1 Exigences, T1.2 Rôles (brouillon), T1.3 Architecture, T1.5 Feuille de route
### Phase 2 : mise en place (terminée)
- T2.1 à T2.9 : Git, prérequis, FastAPI, config, PostgreSQL, Alembic, Angular, Flutter, pytest
### Phase 3 : fondations backend
- T3.0 Décisions métier validées (D7 à D14)
- T3.1 Conception de la base (docs/DATABASE.md)
- T3.2 Modèles users, refresh_tokens, admins, customers + migration 792c3e1c2311
- T3.3 Hachage Argon2, JWT, refresh tokens
- T3.4a Inscription client POST /api/v1/auth/register (24 tests, commit 77b3e09)

## En cours
- T3.4b Connexion, refresh, déconnexion (branche feature/t3-4b-login)

## Bloqué
- Rien

## Notes
- Avertissement à traiter plus tard : starlette.testclient signale que httpx est déprécié.
- Le mot de passe de la base et la SECRET_KEY sont uniquement dans backend/.env (ignoré par Git).
- Sécurité à compléter : limitation des tentatives de connexion (T7.3).
- Base de développement : 1 utilisateur de test (yassmine@example.com).

## À venir
- T3.5 RBAC (utilisateur courant, rôles, /auth/me), T3.6 erreurs centralisées, T3.7 audit logs
