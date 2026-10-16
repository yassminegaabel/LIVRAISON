# PROJECT_PLAN — Feuille de route

Légende dépendances : Tx.y <- prérequis.

## Phase 1 — Analyse et architecture
- T1.1 Extraction des exigences (fonctionnelles/non fonctionnelles) — fait dans la 1re réponse
- T1.2 Rôles et matrice de permissions — brouillon dans DECISIONS.md
- T1.3 Architecture et structure du dépôt — voir CLAUDE.md
- T1.4 Liste des entités et relations (niveau haut) — voir ci-dessous ; colonnes détaillées en T3.1
- T1.5 Feuille de route + documents de mémoire

## Phase 2 — Mise en place
- T2.1 Dossier du projet, Git, .gitignore, documents (<- T1.5)
- T2.2 Vérifier les prérequis (Git, Python, Node, Angular CLI, Flutter, PostgreSQL) et figer les versions (<- T2.1)
- T2.3 Backend FastAPI minimal + endpoint /health + venv + requirements (<- T2.2)
- T2.4 Configuration par variables d'environnement (pydantic-settings, .env.example) (<- T2.3)
- T2.5 PostgreSQL : base + utilisateur de dev + connexion SQLAlchemy (<- T2.4)
- T2.6 Alembic initialisé + première migration vide (<- T2.5)
- T2.7 Workspace Angular (3 projets) qui compile (<- T2.2)
- T2.8 Apps Flutter (customer_app, driver_app) qui démarrent (<- T2.2)
- T2.9 Test backend automatisé (pytest) pour /health + CI locale (<- T2.3)

## Phase 3 — Fondations backend
- T3.1 Conception détaillée de la BDD (ERD, colonnes, contraintes, index) (<- T2.6)
- T3.2 Modèles + migrations : utilisateurs/rôles (<- T3.1)
- T3.3 Hash de mot de passe + JWT (access/refresh) (<- T3.2)
- T3.4 Inscription client (email OU téléphone) + connexion (<- T3.3)
- T3.5 RBAC (dépendances par rôle) + tests (<- T3.4)
- T3.6 Gestionnaire d'erreurs centralisé + format d'erreur standard (<- T2.3)
- T3.7 Audit logs (<- T3.5)
- T3.8 Documentation OpenAPI complète + tests d'auth (<- T3.5)

## Phase 4 — Métier (chacun = modèle + migration + service + routes + tests)
- T4.1 Clients et adresses (<- T3.5)
- T4.2 Admin : paramètres, zones de livraison (<- T3.5)
- T4.3 Commerçants + comptes commerçant + validation admin (<- T3.5)
- T4.4 Formules d'abonnement, abonnements, paiements d'abonnement (<- T4.3) [à confirmer, voir ambiguïtés]
- T4.5 Catégories (<- T4.3)
- T4.6 Produits, options, horaires, recherche commerçants/produits (<- T4.5)
- T4.7 Panier (<- T4.6, T4.1)
- T4.8 Codes promo (<- T4.7)
- T4.9 Création de commande + lignes + statuts (machine d'états) (<- T4.7, T4.8, T4.2)
- T4.10 Commerçant : accepter/refuser + temps de préparation (<- T4.9)
- T4.11 Paiements : espèces (COD) + enregistrement ; en ligne via fournisseur (mode sandbox) (<- T4.9)
- T4.12 Livreurs : demande d'inscription, documents, validation admin (<- T3.5)
- T4.13 Attribution des courses + workflow livreur (accepter, récupérer, livrer) (<- T4.10, T4.12)
- T4.14 Positions livreur + suivi (REST puis WebSocket) (<- T4.13)
- T4.15 Gains livreur (<- T4.13)
- T4.16 Notifications (en base + push FCM en dev) (<- T4.9)
- T4.17 Avis (<- T4.13)
- T4.18 Réclamations + remboursements (support) (<- T4.11, T4.13)

## Phase 5 — Web
- T5.1 Socle Angular : auth, interceptors, guards, layout (<- T3.5, T2.7)
- T5.2 Site client : recherche, produits, panier, commande, suivi (<- T4.9, T5.1)
- T5.3 Portail commerçant : profil, produits, commandes (<- T4.10, T5.1)
- T5.4 Dashboard admin : utilisateurs, commerçants, livreurs, commandes, paramètres, zones (<- T4.x, T5.1)
- T5.5 Interface support : réclamations, remboursements (<- T4.18, T5.1)

## Phase 6 — Mobile
- T6.1 Socle Flutter commun : auth + client API (<- T3.5, T2.8)
- T6.2 App client : parcours complet commande/paiement/suivi (<- T4.9, T6.1)
- T6.3 App livreur : connexion, courses, itinéraire, confirmation (<- T4.13, T6.1)
- T6.4 Permissions localisation + envoi de positions (<- T4.14)
- T6.5 Notifications push (<- T4.16)

## Phase 7 — Intégration et qualité
- T7.1 Scénario de bout en bout (client -> commerçant -> livreur -> livraison)
- T7.2 Tests unitaires/intégration, couverture des règles métier
- T7.3 Revue sécurité/autorisations, validation des entrées
- T7.4 Responsive, performance (API < 500 ms), cas limites

## Phase 8 — Finalisation
- T8.1 Documentation complète  - T8.2 Config d'environnement  - T8.3 Installation BDD  - T8.4 Déploiement local (Docker Compose optionnel)  - T8.5 Checklist d'acceptation finale

## Critères d'acceptation par phase
- P1 : tous documents créés, exigences tracées, aucune ambiguïté bloquante non listée.
- P2 : /health répond 200 ; Alembic exécute `upgrade head` ; Angular et Flutter compilent et démarrent ; pytest passe.
- P3 : inscription/connexion fonctionnent ; un rôle non autorisé reçoit 403 ; erreurs au format standard ; Swagger à jour.
- P4 : chaque fonctionnalité a des routes documentées, testées (cas nominal + refus d'accès + validation) ; le cycle d'une commande est testé bout en bout par l'API.
- P5 : chaque portail permet les actions listées au cahier ; pages protégées par rôle.
- P6 : les 2 apps tournent sur émulateur Android (iOS si Mac) et font le parcours complet.
- P7 : scénario E2E vert ; pas de faille d'autorisation connue ; temps de réponse mesurés.
- P8 : un tiers peut installer et lancer le projet avec la seule documentation.

## Entités (niveau haut)
users(roles) 1-1 clients/commercants_comptes/livreurs/admins ; clients 1-N adresses ; commercants 1-N comptes, categories, produits, horaires ; produits 1-N options ; commandes N-1 client, commerçant, adresse ; commandes 1-N lignes, statuts ; commandes 1-1 livraison (N-1 livreur) ; commandes 1-N paiements ; commandes 1-N avis/réclamations ; codes_promo N-N commandes ; zones_livraison liées aux commerçants/commandes ; livreurs 1-N positions, documents, gains ; notifications N-1 utilisateur.
