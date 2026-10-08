# INTC Product Barcode Print

Module **Odoo 19** pour générer et imprimer des étiquettes code-barres produits sur une **imprimante thermique ESC/POS** (58 mm), directement depuis le navigateur, via le pont d'impression INTC installé sur le poste (PC Windows ou téléphone Android).

- **Version** : 19.0.1.3.0
- **Licence** : LGPL-3
- **Dépendances** : `product`, `web`
- **Éditeur** : INTC

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Comment ça marche](#comment-ça-marche)
3. [Installation](#installation)
4. [Utilisation](#utilisation)
5. [Configuration](#configuration)
6. [Le jeton du pont](#le-jeton-du-pont)
7. [Dépannage](#dépannage)
8. [Structure du module](#structure-du-module)
9. [Déploiement automatique](#déploiement-automatique)
10. [Projets liés](#projets-liés)

---

## Fonctionnalités

### Impression des étiquettes
- Action **Imprimer code-barre** sur les produits (vue liste et formulaire).
- Assistant avec choix du contenu de l'étiquette :
  - nom du produit ;
  - référence interne ;
  - chiffres du code-barres ;
  - prix.
- Nombre d'étiquettes par produit.
- **Imprimer** : envoi direct à l'imprimante via le pont local.
- **Télécharger (.bin)** : récupère les octets ESC/POS bruts dans un fichier (utile pour tester ou imprimer autrement).

### Génération automatique des codes-barres
- Action **Générer les codes-barres** dans le menu *Actions* (vue liste et formulaire).
- Ne remplit **que les produits sans code-barres** : les codes existants ne sont jamais modifiés.
- **Ignore les produits de type service** (Acompte, Dépôt, Régler la facture…).
- Codes **EAN-13 à préfixe `20`** (plage réservée à l'usage interne : aucun risque de collision avec un vrai code fabricant).
- Continue la numérotation à partir du plus grand code `20…` déjà en base, produits archivés et autres sociétés compris.
- Calcule automatiquement la clé de contrôle EAN-13.
- Fonctionne par variante : un produit à plusieurs variantes reçoit un code par variante.
- Le champ reste éditable : le client peut toujours saisir un code à la main.

---

## Comment ça marche

```
┌──────────────── Navigateur (PC ou téléphone) ────────────────┐
│  Odoo  ──(1) génère les octets ESC/POS côté serveur          │
│        ──(2) JavaScript : POST http://localhost:8080/rawprint│
│              en-tête X-Bridge-Token                          │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
                 Pont d'impression INTC (sur le même poste)
                 PC : service Windows  ·  Android : app INTC Bridge
                               │ Bluetooth / Port COM / Réseau / USB
                               ▼
                       Imprimante thermique
```

Le serveur Odoo ne parle **jamais** directement à l'imprimante : c'est le navigateur du poste qui transmet l'impression au pont local. Odoo peut donc être hébergé n'importe où (VPS, cloud).

---

## Installation

1. Copier le dossier `product_barcode_print_intc` dans un répertoire déclaré dans `addons_path`.
2. Redémarrer Odoo.
3. *Applications* → **Mettre à jour la liste des applications**.
4. Rechercher **INTC Product Barcode Print** → **Installer**.

Pour une mise à jour du code : *Applications* → le module → ⋮ → **Mettre à jour**, puis recharger la page du navigateur avec **Ctrl+Maj+R** (pour charger le nouveau JavaScript).

### Côté poste client

Installer le pont d'impression sur chaque poste qui imprime :

| Poste | Pont | Dépôt |
|---|---|---|
| PC Windows | `INTC-Bridge-Setup-x.y.z.exe` | [`Gitjaphet/intc_print_bridge`](https://github.com/Gitjaphet/intc_print_bridge) |
| Téléphone Android | `INTC-Bridge-x.y.z.apk` | [`Gitjaphet/intc_bridge_android`](https://github.com/Gitjaphet/intc_bridge_android) |

---

## Utilisation

### Imprimer des étiquettes
1. *Point de Vente* (ou *Inventaire*) → **Produits**.
2. Cocher un ou plusieurs produits (ou ouvrir une fiche produit).
3. **Actions** → **Imprimer code-barre**.
4. Choisir le contenu et le nombre d'étiquettes → **Imprimer**.

### Générer les codes-barres manquants
1. **Produits** en vue liste → cocher les produits concernés.
2. **Actions** → **Générer les codes-barres**.
3. Une notification indique le nombre de codes créés et la liste se rafraîchit.

Exemple : si les codes `2000000000015` à `2000000000046` existent déjà, les trois prochains produits recevront `2000000000053`, `2000000000060`, `2000000000077`.

---

## Configuration

| Paramètre système | Défaut | Rôle |
|---|---|---|
| `product_barcode_print_intc.bridge_url` | `http://localhost:8080` | Adresse du pont d'impression local |

À modifier dans *Paramètres* → *Technique* → *Paramètres système* (mode développeur) uniquement si le pont écoute sur un autre port.

---

## Le jeton du pont

Chaque pont (chaque PC, chaque téléphone) génère **son propre jeton** à l'installation. Il empêche un autre site web ouvert dans le navigateur d'imprimer à la place d'Odoo.

- À la **première impression** depuis un poste, le pont répond `401` et Odoo demande le jeton.
- Copier le jeton dans l'application du pont (bouton **Copier**), le coller dans la fenêtre d'Odoo → **OK**.
- Le jeton est mémorisé **dans le navigateur de ce poste** (`localStorage`, clé `intc_bridge_token`) : il n'est plus redemandé.
- Si le pont est réinstallé avec un nouveau jeton, la demande réapparaît automatiquement.

---

## Dépannage

| Message dans Odoo | Cause | Solution |
|---|---|---|
| *pont injoignable. Vérifiez qu'INTC Print Bridge est installé et « En marche »* | Le pont n'est pas installé, arrêté, ou n'écoute pas sur le port configuré | Ouvrir l'application du pont et vérifier l'état du service |
| *Jeton invalide* | Mauvais jeton collé, ou pont réinstallé | Relancer l'impression et coller le jeton affiché par le pont |
| *Imprimante éteinte ou hors de portée* | L'imprimante ne répond pas | Allumer l'imprimante, la rapprocher |
| *Imprimante occupée ou connexion interrompue* | Un autre appareil (téléphone, autre PC) est connecté à l'imprimante | Une imprimante Bluetooth n'accepte qu'**une connexion à la fois** : déconnecter l'autre appareil |
| *Aucun produit à traiter* (génération) | Les produits sélectionnés ont déjà un code ou sont des services | Normal |

Si Chrome demande l'autorisation d'**accéder aux appareils du réseau local**, cliquer sur **Autoriser** (le pont tourne sur `localhost`).

---

## Structure du module

```
product_barcode_print_intc/
├── __manifest__.py
├── models/
│   ├── barcode_print_wizard.py     # assistant d'impression (ESC/POS, envoi au pont)
│   └── product_template.py         # génération des codes EAN-13 « 20… »
├── tools/
│   └── escpos.py                   # construction des commandes ESC/POS
├── views/
│   ├── barcode_print_wizard_views.xml
│   └── product_template_actions.xml  # action serveur « Générer les codes-barres »
├── static/src/js/
│   └── barcode_print_action.js     # action client : envoi au pont + gestion du jeton
└── security/ir.model.access.csv
```

---

## Déploiement automatique

Chaque `git push` sur `main` déclenche un workflow GitHub Actions :

1. **Lint & validation** du code.
2. **Déploiement VPS** : clone du module dans `/odoo19/mes-modules-pro/product_barcode_print_intc` sur le serveur, puis redémarrage du service Odoo.

Après le déploiement, **mettre à jour le module** dans *Applications* si des vues, des données ou le manifeste ont changé.

---

## Projets liés

- [`Gitjaphet/intc_print_bridge`](https://github.com/Gitjaphet/intc_print_bridge) — pont d'impression pour **PC Windows** (service + interface).
- [`Gitjaphet/intc_bridge_android`](https://github.com/Gitjaphet/intc_bridge_android) — pont d'impression pour **Android**.

Les deux ponts respectent le même contrat (`POST /rawprint` + `X-Bridge-Token` sur le port 8080) : le module fonctionne sans aucune différence avec un PC ou un téléphone.
