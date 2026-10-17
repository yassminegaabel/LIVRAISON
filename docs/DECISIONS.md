# DECISIONS

## Décisions
- D1 Mobile : Flutter (le cahier dit "Flutter / React Native" ; le prompt impose Flutter).
- D2 Une seule API FastAPI ; JWT access + refresh ; RBAC avec rôles : customer, merchant, driver, admin, support.
- D3 Nom des tables en anglais ; correspondance : admins->admins, audit_logs->audit_logs, parametres->settings, zones_livraison->delivery_zones, commercants->merchants, commercant_comptes->merchant_accounts, formules_abonnement->subscription_plans, abonnements->subscriptions, paiements_abonnement->subscription_payments, produits->products, options_produits->product_options, horaires->opening_hours, livreurs->drivers, demandes_livreur->driver_applications, livreur_documents->driver_documents, livreur_positions->driver_locations, gains_livreur->driver_earnings, clients->customers, adresses_client->customer_addresses, avis->reviews, reclamations->complaints, commandes->orders, lignes_commande->order_items, livraisons->deliveries, statuts_commande->order_status_history, paiements->payments, codes_promo->promo_codes.
- D4 Application web "support" = section du dashboard admin avec rôle support (hypothèse, modifiable).
- D5 Temps réel : WebSocket FastAPI (ou polling en repli), documenté en T4.14.
- D6 Paiement en ligne : fournisseur à choisir après réponse à la question Q2 ; mode sandbox en dev, jamais de faux succès en prod.

## Matrice de permissions (brouillon)
- customer : son profil, ses adresses, panier, ses commandes, avis, réclamations.
- merchant : son profil, catalogue, horaires, commandes reçues (accepter/refuser/statut/temps de préparation).
- driver : son profil, courses assignées, positions, confirmation de livraison, gains.
- support : réclamations, remboursements, lecture des commandes concernées.
- admin : tout, validation commerçants/livreurs, paramètres, zones, audit.

## Ambiguïtés
- Q1 Quel pays/devise/langues (FR/AR/EN) ? TVA ?
- Q2 Fournisseur de paiement en ligne souhaité ? (nécessite clés API)
- Q3 Abonnements commerçants : la BDD en parle (formules, paiements d'abonnement) mais pas les besoins fonctionnels. Les implémente-t-on ?
- Q4 Attribution des livreurs : automatique (plus proche), manuelle admin, ou le livreur choisit parmi des courses ?
- Q5 Commission de la plateforme et frais de livraison : calcul (fixe, par distance, par zone) ?
- Q6 Un client peut-il commander chez plusieurs commerçants en une commande ? (hypothèse : un panier = un commerçant)
- Q7 Remboursement : total/partiel ? via fournisseur ou manuel ?
- Q8 Livreur : documents requis, validation admin obligatoire ? Statut en ligne/hors ligne ?
- Q9 Pharmacies : ordonnances/produits réglementés ?
- Q10 Cartes/GPS : Google Maps ou OpenStreetMap (gratuit) ?
- Q11 Notifications : push (Firebase), email, SMS ?
- Q12 Inscription par téléphone : vérification OTP par SMS ? (service payant)
- Q13 "Tablette commerçant optionnelle" : hors périmètre initial ? (hypothèse : portail web responsive suffit)
- Q14 Hébergement final, 99,5 % de disponibilité : local seulement ou cloud ?
- Q15 Annulation de commande : qui, quand ?
- Q16 Suppression de produit : suppression réelle ou archivage (hypothèse : archivage logique)
- Q17 Support client : application web séparée ou section de l'admin ?
- Q18 RGPD/protection des données personnelles, conservation des positions GPS ?

## Versions de l'environnement (figées en T2.2, le 2026-10-16)
- Python 3.12.10, pip 26.2.1
- Node.js 24.19.0, npm 11.17.0, Angular CLI 22.1.7
- Flutter 3.47.5 (stable), Dart 3.13.4
- PostgreSQL client 17.11 (serveur à vérifier en T2.5)
- Les versions des paquets Python seront figées dans backend/requirements.txt en T2.3.

- Angular (@angular/core) : ^22.1.0 ; workspace web/ avec 3 apps standalone (customer-site, merchant-portal, admin-dashboard), SCSS, sans SSR (T2.7).

## Décisions métier validées (T3.0, 2026-10-16)
- D7 Devise : TND (paramètre "currency" de la plateforme). Montants en NUMERIC(10,2).
- D8 Abonnements commerçants : tables prévues, fonctionnalité en T4.4 ; paiements d'abonnement saisis à la main par l'admin au début.
- D9 Attribution des livreurs : le premier livreur en ligne qui accepte la course la prend ; l'admin peut assigner manuellement. Attribution automatique plus tard si souhaitée.
- D10 Frais de livraison : fixes par zone de livraison. Commission : pourcentage configurable (paramètre global, surchargeable par commerçant).
- D11 Un panier et une commande = un seul commerçant.
- D12 Clés primaires BIGINT identity ; "enums" en VARCHAR + CHECK ; produits archivés au lieu d'être supprimés.
- D13 (hypothèse à confirmer) Gain du livreur = driver_share_percent (80 %) des frais de livraison.
- D14 Zones de livraison : cercle (centre + rayon) au départ.
- Conception détaillée de la base : voir docs/DATABASE.md.

## Sécurité (T3.3)
- D15 Mots de passe : Argon2id via pwdlib ; seul le hash est stocké.
- D16 Access token : JWT HS256 (PyJWT), 30 min, claims sub/role/type/iat/exp/jti. Le champ "sub" est une chaîne (id utilisateur).
- D17 Refresh token : chaîne aléatoire opaque (non JWT), stockée hachée en SHA-256 dans refresh_tokens, durée 30 jours, révocable.
- D18 SECRET_KEY : minimum 32 caractères, uniquement dans .env. Changer la clé invalide tous les access tokens.
