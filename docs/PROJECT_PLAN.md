# PROJECT_PLAN — MVP de 14 jours

> Le plan complet d'origine (8 phases) est conservé dans docs/archive/PROJECT_PLAN_complet.md.
> Objectif : une application de livraison fonctionnelle, présentable et complète sur le parcours principal.

## Périmètre du MVP
- Client : inscription, connexion, consultation des commerçants et des produits, panier, commande avec paiement en espèces, suivi de la commande.
- Commerçant : inscription (validée par l'admin), gestion des produits, réception des commandes, acceptation ou refus, statuts de préparation.
- Livreur : inscription (validée par l'admin), courses disponibles, acceptation, ramassage, livraison.
- Administrateur : validation des commerçants et des livreurs, supervision des commandes.
- Données de démonstration et comptes de démo.

## Hors périmètre (reporté)
Paiement en ligne, notifications push, géolocalisation en temps réel, abonnements commerçants, codes promo, avis, réclamations et remboursements, journal d'audit, zones de livraison, options de produits, horaires d'ouverture, vérification du téléphone par SMS, limitation des tentatives de connexion.

## Simplifications par rapport à docs/DATABASE.md
- Pas de table categories (catégorie en texte sur le produit), product_options, opening_hours, delivery_zones (frais de livraison fixes par commerçant), settings.
- Panier côté navigateur ; prix recalculés par le serveur à la commande.
- Pas de table payments : orders.payment_status (pending puis paid à la livraison).
- Pas de table deliveries : orders.driver_id.
- Pas de driver_applications ni driver_documents, pas de audit_logs.

## Cycle de vie d'une commande
pending -> accepted | rejected ; accepted -> preparing -> ready_for_pickup -> picked_up -> delivered.
Le client peut annuler tant que la commande est pending (cancelled).
Un livreur peut accepter une course dès que la commande est accepted (sans livreur assigné) ; picked_up exige ready_for_pickup.

## Planning
| Jour | Tâche |
|---|---|
| 1 | M1 Commerçants et livreurs : inscription en attente, validation admin, script de création de l'admin |
| 2 | M2 Produits (commerçant) et liste publique ; M3 Adresses client |
| 3 | M4 Commandes : création (calcul serveur), suivi, annulation |
| 4 | M5 Commerçant : accepter/refuser, préparation ; M6 Livreur : courses, accepter, ramassée, livrée |
| 5 | M7 Supervision admin ; M8 Données de démo et test du parcours complet. API terminée |
| 6-7 | W1-W2 Socle Angular, connexion, inscription des 3 rôles, navigation par rôle |
| 8-9 | W3-W4 Espace client : catalogue, panier, commande, suivi |
| 10 | W5 Espace commerçant |
| 11 | W6 Espace livreur (web adapté au téléphone) |
| 12 | W7 Espace admin |
| 13 | Q1 Finitions : responsive, erreurs, états vides |
| 14 | Q2 Documentation, comptes de démo, scénario de présentation, étiquette v1.0-mvp |

## Ordre de coupe en cas de retard
1. Espace admin web (l'admin utilise Swagger) 2. Statistiques 3. Finitions. Application Flutter du livreur : bonus seulement.

## Critères d'acceptation du MVP
- Un client passe une commande en espèces, un commerçant l'accepte, un livreur la prend et la livre, le client voit chaque statut.
- Un commerçant ou un livreur non validé ne peut pas agir.
- Chaque route est protégée par rôle ; tous les tests automatiques passent.
- Le projet se lance avec la documentation, avec des comptes de démo.
