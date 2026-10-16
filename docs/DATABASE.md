# DATABASE — Conception détaillée (T3.1) — À VALIDER

Version : brouillon 1 — Aucun code n'est écrit tant que ce document n'est pas validé.

## 1. Conventions générales
- Clé primaire : `id BIGINT GENERATED ALWAYS AS IDENTITY` (sauf tables profil : PK = `user_id`).
- Dates : `TIMESTAMPTZ` (UTC) ; `created_at DEFAULT now()` partout, `updated_at` sur les tables modifiables.
- Montants : `NUMERIC(10,2)` avec `CHECK (>= 0)`. Devise de la plateforme : TND (paramètre `currency`).
- Coordonnées GPS : `latitude NUMERIC(9,6)`, `longitude NUMERIC(9,6)`.
- "Enums" : `VARCHAR` + contrainte `CHECK` (plus simple à migrer avec Alembic que les enums natifs PostgreSQL).
- Noms en anglais, snake_case, tables au pluriel.
- Suppression : pas de suppression physique des produits/utilisateurs (`is_archived`, `is_active`). Les commandes gardent des **copies figées** (snapshots) des noms et prix.
- Clés étrangères : `RESTRICT` par défaut ; `CASCADE` pour les lignes enfants purement dépendantes ; `SET NULL` pour les liens optionnels.
- Sécurité : seul `password_hash` est stocké (jamais le mot de passe). Les refresh tokens sont stockés hachés.

## 2. Correspondance avec le cahier des charges
| Cahier | Table(s) |
|---|---|
| admins | users (rôle admin/support) + admins |
| audit_logs | audit_logs |
| parametres | settings |
| zones_livraison | delivery_zones (+ merchant_delivery_zones) |
| commercants / commercant_comptes | merchants / merchant_accounts |
| formules_abonnement / abonnements / paiements_abonnement | subscription_plans / subscriptions / subscription_payments |
| categories / produits / options_produits / horaires | categories / products / product_options / opening_hours |
| livreurs / demandes_livreur / livreur_documents / livreur_positions / gains_livreur | drivers / driver_applications / driver_documents / driver_locations / driver_earnings |
| clients / adresses_client / avis / reclamations | customers / customer_addresses / reviews / complaints |
| commandes / lignes_commande / livraisons / statuts_commande | orders / order_items / deliveries / order_status_history |
| paiements / codes_promo / notifications | payments / promo_codes / notifications |

**Tables ajoutées** (nécessaires aux exigences, absentes de la liste du cahier) :
users et refresh_tokens (authentification et rôles), carts / cart_items / cart_item_options (panier), order_item_options (options figées), promo_code_usages (limite d'usage par client), refunds (remboursements), complaint_messages (échanges support), device_tokens (notifications push), merchant_delivery_zones (zones desservies).

## 3. Authentification et comptes

**users** : id; email VARCHAR(255) NULL UNIQUE (stocké en minuscules); phone VARCHAR(20) NULL UNIQUE (format international E.164); password_hash VARCHAR(255) NOT NULL; role VARCHAR(20) NOT NULL CHECK IN ('customer','merchant','driver','admin','support'); is_active BOOL DEFAULT true; last_login_at; created_at; updated_at.
Contrainte : `CHECK (email IS NOT NULL OR phone IS NOT NULL)`. Index : role.

**refresh_tokens** : id; user_id FK users CASCADE; token_hash VARCHAR(255) UNIQUE; expires_at; revoked_at NULL; created_at. Index : user_id.

**admins** : user_id PK/FK users CASCADE; first_name; last_name; created_at. (Couvre admin et support ; le rôle est dans users.role.)

**customers** : user_id PK/FK users CASCADE; first_name; last_name; created_at.

**customer_addresses** : id; customer_id FK customers CASCADE; label VARCHAR(50) ('Maison'...); address_line VARCHAR(255); city; postal_code NULL; latitude; longitude; instructions TEXT NULL; delivery_zone_id FK delivery_zones SET NULL; is_default BOOL; created_at; updated_at. Index : customer_id. Règle : une seule adresse par défaut par client (index unique partiel sur customer_id WHERE is_default).

## 4. Administration

**settings** : key VARCHAR(100) PK; value TEXT NOT NULL; value_type VARCHAR(20) CHECK IN ('string','int','decimal','bool'); description TEXT; updated_by FK users SET NULL; updated_at.
Valeurs initiales : currency=TND, platform_commission_percent=10, driver_share_percent=80 (hypothèse, voir DECISIONS), order_accept_timeout_minutes=10.

**delivery_zones** : id; name UNIQUE; center_latitude; center_longitude; radius_km NUMERIC(6,2) CHECK > 0; delivery_fee NUMERIC(10,2); is_active; created_at; updated_at. (Zone circulaire pour commencer ; polygones possibles plus tard.)

**audit_logs** : id; user_id FK users SET NULL; action VARCHAR(100); entity_type VARCHAR(50); entity_id BIGINT NULL; details JSONB NULL; ip_address VARCHAR(45) NULL; created_at. Index : (entity_type, entity_id), created_at.

## 5. Commerçants

**merchants** : id; name; business_type VARCHAR(20) CHECK IN ('restaurant','supermarket','pharmacy','shop'); description; phone; address_line; city; latitude; longitude; logo_url NULL; status VARCHAR(20) DEFAULT 'pending' CHECK IN ('pending','approved','rejected','suspended'); is_accepting_orders BOOL DEFAULT true; default_prep_minutes INT DEFAULT 20; min_order_amount NUMERIC(10,2) DEFAULT 0; commission_percent NUMERIC(5,2) NULL (remplace la valeur globale si renseigné); rating_avg NUMERIC(3,2) DEFAULT 0; rating_count INT DEFAULT 0; created_at; updated_at. Index : (status, business_type), city.

**merchant_accounts** : id; merchant_id FK merchants CASCADE; user_id FK users CASCADE UNIQUE; account_role VARCHAR(20) CHECK IN ('owner','staff'); is_active; created_at. Règle : un utilisateur = un seul commerçant.

**merchant_delivery_zones** : merchant_id FK CASCADE; zone_id FK CASCADE; PK (merchant_id, zone_id).

**subscription_plans** : id; name UNIQUE; description; price NUMERIC(10,2); duration_days INT CHECK > 0; is_active; created_at.
**subscriptions** : id; merchant_id FK; plan_id FK; starts_at; ends_at; status CHECK IN ('active','expired','cancelled'); created_at. Index : (merchant_id, status).
**subscription_payments** : id; subscription_id FK; amount; method CHECK IN ('cash','bank_transfer','online'); status CHECK IN ('pending','paid','failed'); reference NULL; paid_at NULL; recorded_by FK users SET NULL; created_at.

## 6. Catalogue

**categories** : id; merchant_id FK CASCADE; name; position INT DEFAULT 0; is_active; created_at. UNIQUE (merchant_id, name).

**products** : id; merchant_id FK; category_id FK categories SET NULL; name; description; price NUMERIC(10,2); image_url NULL; is_available BOOL DEFAULT true; is_archived BOOL DEFAULT false (la "suppression" du cahier = archivage); position INT; created_at; updated_at. Index : (merchant_id, is_archived, is_available), category_id ; recherche par nom (index GIN/trigram plus tard).

**product_options** : id; product_id FK CASCADE; group_name VARCHAR(100) (ex. "Taille"); name; extra_price NUMERIC(10,2) DEFAULT 0; is_required_group BOOL; is_available BOOL; position. Index : product_id.

**opening_hours** : id; merchant_id FK CASCADE; day_of_week SMALLINT CHECK 0..6 (0 = lundi); opens_at TIME; closes_at TIME; UNIQUE (merchant_id, day_of_week, opens_at). Plusieurs plages par jour possibles ; un jour sans ligne = fermé.

## 7. Panier

**carts** : id; customer_id FK UNIQUE CASCADE (un panier par client); merchant_id FK NULL; promo_code_id FK SET NULL; updated_at. Règle : un panier = un seul commerçant ; si le client ajoute un produit d'un autre commerçant, l'API demande de vider le panier.
**cart_items** : id; cart_id FK CASCADE; product_id FK; quantity INT CHECK > 0; note TEXT NULL; UNIQUE (cart_id, product_id) hors options (voir règle service).
**cart_item_options** : cart_item_id FK CASCADE; option_id FK product_options; PK (cart_item_id, option_id).

## 8. Commandes

**orders** : id; order_number VARCHAR(20) UNIQUE (ex. ORD-20261016-0001); customer_id FK; merchant_id FK; delivery_address_id FK customer_addresses SET NULL; **adresse figée** : delivery_address_line, delivery_city, delivery_latitude, delivery_longitude, delivery_instructions; delivery_zone_id FK SET NULL; status VARCHAR(20) CHECK IN ('pending','accepted','rejected','preparing','ready_for_pickup','picked_up','delivered','cancelled'); payment_method CHECK IN ('cash','online'); subtotal; delivery_fee; discount_amount DEFAULT 0; total; promo_code_id FK SET NULL; commission_percent (copie); commission_amount; prep_minutes INT NULL; customer_note; rejection_reason; cancelled_by VARCHAR(20) NULL; cancel_reason; placed_at; accepted_at; ready_at; picked_up_at; delivered_at; created_at; updated_at.
Contrainte : `total = subtotal + delivery_fee - discount_amount` (vérifiée par CHECK). Index : (customer_id, created_at DESC), (merchant_id, status, created_at DESC), status.
Machine d'états : pending -> accepted | rejected | cancelled ; accepted -> preparing | cancelled ; preparing -> ready_for_pickup ; ready_for_pickup -> picked_up ; picked_up -> delivered. (Détaillée en T4.9.)

**order_items** : id; order_id FK CASCADE; product_id FK SET NULL; product_name (copie); unit_price (copie); quantity INT > 0; note NULL; line_total NUMERIC(10,2).
**order_item_options** : id; order_item_id FK CASCADE; option_name (copie); extra_price (copie).
**order_status_history** : id; order_id FK CASCADE; status; changed_by FK users SET NULL; note NULL; created_at. Index : (order_id, created_at).

## 9. Livraison et livreurs

**drivers** : user_id PK/FK users CASCADE; first_name; last_name; vehicle_type CHECK IN ('bike','scooter','car'); vehicle_plate NULL; status CHECK IN ('pending','approved','rejected','suspended') DEFAULT 'pending'; is_online BOOL DEFAULT false; created_at; updated_at.
**driver_applications** : id; driver_id FK drivers CASCADE; status CHECK IN ('pending','approved','rejected'); rejection_reason NULL; reviewed_by FK users SET NULL; reviewed_at NULL; created_at.
**driver_documents** : id; driver_id FK CASCADE; doc_type CHECK IN ('id_card','driving_license','vehicle_registration','insurance','photo'); file_url; status CHECK IN ('pending','approved','rejected'); expires_on DATE NULL; uploaded_at. (Fichiers stockés hors base ; ici seulement le chemin.)
**driver_locations** : id BIGINT; driver_id FK CASCADE; delivery_id FK deliveries SET NULL; latitude; longitude; accuracy_m NUMERIC(6,1) NULL; speed_kmh NUMERIC(5,1) NULL; recorded_at TIMESTAMPTZ. Index : (driver_id, recorded_at DESC), (delivery_id, recorded_at DESC). Table volumineuse : politique de purge à définir.
**deliveries** : id; order_id FK UNIQUE; driver_id FK drivers SET NULL NULL; status CHECK IN ('awaiting_driver','assigned','heading_to_merchant','picked_up','delivered','failed','cancelled') DEFAULT 'awaiting_driver'; assignment_mode CHECK IN ('driver_accepted','admin_assigned') NULL; assigned_at; picked_up_at; delivered_at; failure_reason NULL; created_at; updated_at. Index : (status), (driver_id, status).
**driver_earnings** : id; driver_id FK; delivery_id FK UNIQUE; amount NUMERIC(10,2); status CHECK IN ('pending','paid'); paid_at NULL; created_at.

## 10. Paiements et remboursements

**payments** : id; order_id FK; method CHECK IN ('cash','online'); provider VARCHAR(50) NULL; provider_reference VARCHAR(255) NULL UNIQUE; amount; currency CHAR(3) DEFAULT 'TND'; status CHECK IN ('pending','succeeded','failed','cancelled','refunded','partially_refunded'); collected_by_driver_id FK drivers SET NULL NULL (espèces); paid_at NULL; created_at; updated_at. Index : order_id, status.
**refunds** : id; payment_id FK; complaint_id FK complaints SET NULL NULL; amount NUMERIC(10,2) CHECK > 0; reason TEXT; status CHECK IN ('requested','approved','rejected','processed'); requested_by FK users SET NULL; processed_by FK users SET NULL; provider_reference NULL; created_at; processed_at NULL. Règle : somme des remboursements d'un paiement <= montant du paiement.

## 11. Promotions, avis, réclamations, notifications

**promo_codes** : id; code VARCHAR(50) UNIQUE (stocké en majuscules); discount_type CHECK IN ('percent','fixed'); discount_value NUMERIC(10,2) > 0; max_discount_amount NULL; min_order_amount DEFAULT 0; valid_from; valid_until; max_uses_total INT NULL; max_uses_per_customer INT DEFAULT 1; merchant_id FK NULL (NULL = valable partout); is_active; created_by FK users SET NULL; created_at. CHECK : valid_until > valid_from ; percent <= 100.
**promo_code_usages** : id; promo_code_id FK; customer_id FK; order_id FK UNIQUE; discount_amount; used_at. Index : (promo_code_id, customer_id).

**reviews** : id; order_id FK UNIQUE (un avis par commande, seulement si livrée — règle service); customer_id FK; merchant_id FK; driver_id FK NULL; merchant_rating SMALLINT CHECK 1..5; driver_rating SMALLINT NULL CHECK 1..5; comment TEXT NULL; created_at. Index : merchant_id.

**complaints** : id; order_id FK; customer_id FK; category CHECK IN ('late','missing_item','quality','payment','driver_behavior','other'); description TEXT; status CHECK IN ('open','in_progress','resolved','rejected','closed') DEFAULT 'open'; assigned_to FK users SET NULL NULL (agent support); resolution_note NULL; created_at; updated_at; resolved_at NULL. Index : (status, created_at).
**complaint_messages** : id; complaint_id FK CASCADE; author_id FK users; message TEXT; created_at.

**notifications** : id; user_id FK CASCADE; type VARCHAR(50) ('order_status','delivery_assigned','promo',...); title; body; data JSONB NULL; is_read BOOL DEFAULT false; read_at NULL; created_at. Index : (user_id, is_read, created_at DESC).
**device_tokens** : id; user_id FK CASCADE; token VARCHAR(500) UNIQUE; platform CHECK IN ('android','ios','web'); created_at; last_seen_at.

## 12. Ordre de création des migrations (Alembic)
1. users, refresh_tokens, admins, customers (T3.2)
2. delivery_zones, settings, audit_logs, customer_addresses (T4.1, T4.2, T3.7)
3. merchants, merchant_accounts, merchant_delivery_zones, subscriptions* (T4.3, T4.4)
4. categories, products, product_options, opening_hours (T4.5, T4.6)
5. carts* (T4.7), promo_codes* (T4.8)
6. orders, order_items*, order_status_history, payments, refunds (T4.9 à T4.11)
7. drivers*, deliveries, driver_locations, driver_earnings (T4.12 à T4.15)
8. notifications, device_tokens, reviews, complaints* (T4.16 à T4.18)

Les modèles ne sont créés que dans la tâche qui en a besoin (une migration par tâche).

## 13. Points ouverts liés à cette conception
- Q9 : pharmacies et ordonnances -> pas de colonne pour l'instant (à ajouter dans products si besoin).
- Q12 : vérification du téléphone par OTP -> table `otp_codes` ajoutée seulement si confirmé.
- Q16 : suppression de produit = archivage (hypothèse appliquée).
- Calcul de la part du livreur : `driver_share_percent` des frais de livraison (hypothèse à confirmer).
