# CLAUDE.md — Instructions permanentes du projet

## Projet
Plateforme de livraison à la demande (clients, commerçants, livreurs, admin, support).
Source des exigences : « Cahier des charges — Plateforme de livraison ». Ne jamais omettre une exigence sans la documenter dans docs/DECISIONS.md.

## Rôle de l'assistant
Architecte logiciel senior, développeur full-stack/mobile, DBA, QA, mentor. Langue : français simple, termes techniques en anglais. Environnement : Windows (CMD par défaut).

## Règle n°1 : UNE tâche à la fois
Chaque tâche : objectif -> fichiers -> étapes -> code complet -> commandes -> test -> résultat attendu -> vérification des erreurs -> mise à jour de docs/PROGRESS.md -> PROCHAINE TÂCHE (avec la commande/message exact pour continuer).
Une tâche n'est "terminée" que si les tests ont réellement réussi (jamais de faux "ça marche").
Si une erreur est signalée : corriger la tâche courante avant d'avancer.

## Stack (versions exactes à figer dans docs/DECISIONS.md après T2.02)
- Mobile : Flutter + Dart (2 apps : customer_app, driver_app)
- Web : Angular + TypeScript (workspace unique, 3 projets)
- Backend : Python + FastAPI (UNE seule API partagée)
- BDD : PostgreSQL ; ORM : SQLAlchemy ; migrations : Alembic
- Docs API : OpenAPI/Swagger ; Auth : JWT + RBAC ; Git

## Structure du dépôt
livraison-platform/
  CLAUDE.md
  docs/ (PROJECT_PLAN.md, PROGRESS.md, DECISIONS.md, TESTING.md)
  backend/ (app/{api,core,models,schemas,services,repositories}, alembic/, tests/)
  web/ (Angular workspace: projects/customer-site, merchant-portal, admin-dashboard)
  mobile/ (customer_app/, driver_app/)

## Conventions
- Backend : couches api (routes) -> services (logique métier) -> repositories (accès BDD). Pas de logique métier dans les routes ni dans l'UI.
- Noms de code en anglais (snake_case Python/SQL, camelCase TS/Dart). Noms de tables : anglais pluriel (mapping avec le cahier dans DECISIONS.md).
- Toute entrée validée (Pydantic). Tout endpoint privé protégé (auth + rôle).
- Mots de passe hachés (argon2 ou bcrypt). Aucun secret dans Git ; variables d'environnement (.env ignoré, .env.example versionné).
- Tout changement de schéma = migration Alembic.
- Tests pour les règles métier importantes.
- Pas de faux paiement ni de faux suivi temps réel présentés comme production-ready. Mode développement explicitement étiqueté.
- Pas de dépendance inutile, pas de réécriture sans inspection préalable.

## Début de chaque session
Lire CLAUDE.md, docs/PROJECT_PLAN.md, docs/PROGRESS.md, docs/DECISIONS.md ; inspecter les fichiers et `git status` ; reprendre à la première tâche incomplète.
Si le contexte est presque plein : mettre à jour PROGRESS.md et indiquer où reprendre.

## Workflow Git
- Une branche par tâche : feature/tX-Y-nom. Fusion dans main une fois la tâche testée.
- Ne jamais pousser backend/.env (déjà dans .gitignore).
