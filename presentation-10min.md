# Présentation 10 min – Architecture Moodle (portail.uqar.ca)

**Objectif** : Expliquer les composants et abréviations des vues **Vue globale** et **Vue déploiement (zones et instances)** du diagramme d’architecture.

**Durée cible** : 10 minutes (environ 1 min par slide + intro/conclusion).

---

## Slide 1 – Titre (30 s)

**Titre** : Architecture du portail Moodle UQAR – Vue globale et déploiement

**À dire** : Nous présentons l’architecture du portail.uqar.ca (Moodle) en deux vues : la vue globale des services (SOA) et la vue déploiement avec les zones et instances. Chaque composant et abréviation sera expliqué.

---

## Slide 2 – Vue globale : les acteurs (≈1 min)

**Titre** : Vue globale – Acteurs (côté gauche du schéma)

| Abréviation | Signification | Rôle |
|-------------|---------------|------|
| **E** | Étudiants | Consulter cours, rendre devoirs, passer quiz, forums |
| **P** | Enseignants | Créer/gérer cours, noter, gérer ressources et forums |
| **A** | Administrateurs | Gestion utilisateurs, cours, plugins, maintenance |

**À dire** : En haut du schéma, les trois types d’utilisateurs : E pour Étudiants, P pour Enseignants, A pour Administrateurs. Ils passent tous par la même couche d’accès.

---

## Slide 3 – Vue globale : couche d’accès (≈1 min)

**Titre** : Vue globale – Couche d’accès

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **LB** | **L**oad **B**alancer | Répartit les requêtes entre plusieurs serveurs Moodle pour répartir la charge et assurer la disponibilité. |

**À dire** : Le Load Balancer, noté LB, est la seule entrée pour les utilisateurs. Il répartit les connexions entre les serveurs applicatifs et évite de surcharger une seule machine.

---

## Slide 4 – Vue globale : services applicatifs (≈2 min)

**Titre** : Vue globale – Services applicatifs (SOA)

| Abréviation | Signification | Rôle |
|-------------|---------------|------|
| **AUTH** | **Auth**entification / **SSO** | Connexion unique (SSO = **S**ingle **S**ign-**O**n), sessions, intégration CAS UQAR |
| **CAT** | **Cat**alogue cours | Liste des cours, inscriptions, rôles, cohortes |
| **CONT** | **Cont**enu / Fichiers | Pages, ressources, dépôt de fichiers (devoirs, projets) |
| **DEVOIR** | Devoirs / Quiz | Soumissions, dates, quiz, notes, feedback |
| **FORUM** | Forums | Messages, threads, abonnements, modération |
| **NOTIF** | **Notif**ications | Alertes, emails (rappels, annonces) |

**À dire** : Au centre, les services métier en SOA. AUTH gère l’authentification et le SSO. CAT le catalogue de cours. CONT le contenu et les fichiers. DEVOIR couvre devoirs et quiz. FORUM les discussions. NOTIF les notifications et emails. En pratique, tout tourne dans le même monolithe Moodle, mais on les sépare pour réfléchir en services.

---

## Slide 5 – Vue globale : couche données (≈1 min)

**Titre** : Vue globale – Couche données

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **DB** | **D**ata**b**ase | Base de données (MySQL/MariaDB) : cours, utilisateurs, notes, tentatives. Réplication lecture pour alléger les requêtes. |
| **CACHE** | Cache (Redis) | Stockage des **sessions** utilisateur et du **cache** Moodle (listes de cours, pages) pour réduire la charge sur la DB. |
| **FILES** | Stockage **fichiers** | Fichiers déposés (devoirs, ressources). Souvent **S3** (Amazon) ou **NFS** (**N**etwork **F**ile **S**ystem) partagé. |

**À dire** : En bas du schéma, trois types de stockage : DB pour tout ce qui est structuré, CACHE pour les sessions et le cache (souvent Redis), FILES pour les fichiers (S3 ou NFS). S3 désigne un stockage objet type Amazon ; NFS un partage de fichiers sur le réseau.

---

## Slide 6 – Vue déploiement : zones et entrée (≈1 min)

**Titre** : Vue déploiement – Zones et entrée

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **U** | **U**tilisateurs | Tous les types d’utilisateurs (étudiants, enseignants, admin). |
| **Zone DMZ** | **D**emilitarized **Z**one | Zone tampon entre Internet et le réseau interne. On n’expose que le reverse proxy et le CDN, pas les serveurs applicatifs. |
| **LB** | **L**oad **B**alancer | En pratique : **Nginx** ou **HAProxy**, avec terminaison **SSL** (HTTPS) et répartition de charge. |
| **CDN** | **C**ontent **D**elivery **N**etwork | Réseau de serveurs qui sert les assets statiques (CSS, JS, images) au plus près des utilisateurs pour réduire la charge et la latence. |

**À dire** : En déploiement, les utilisateurs U arrivent dans la zone DMZ. Le LB fait SSL et répartition de charge ; le CDN sert les ressources statiques. Les applications ne sont pas exposées directement sur Internet.

---

## Slide 7 – Vue déploiement : zone applicative (≈1 min)

**Titre** : Vue déploiement – Zone applicative

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **M1, M2, M3** (ou **M…N**) | **M**oodle instance 1, 2, … N | Plusieurs instances Moodle (**PHP-FPM** = **P**HP **F**ast**P**rocess **M**anager). Chaque instance exécute les services AUTH, CAT, CONT, etc. |
| **PHP-FPM** | **P**HP **F**ast**P**rocess **M**anager | Moteur qui exécute le code PHP de Moodle ; plusieurs processus en parallèle pour traiter les requêtes. |

**À dire** : Derrière le LB, on a plusieurs serveurs Moodle : M1, M2, jusqu’à N. Chacun tourne avec PHP-FPM. On peut en ajouter pour monter en charge : c’est le scaling horizontal.

---

## Slide 8 – Vue déploiement : zone données (≈1 min)

**Titre** : Vue déploiement – Zone données

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **REDIS** | Redis (nom du produit) | Base clé-valeur en mémoire : **sessions** utilisateur et **cache** Moodle. Très rapide. |
| **DB_M** | **D**ata**b**ase **M**aster | Instance MySQL en **écriture**. Toutes les modifications (soumissions, notes, etc.) vont ici. |
| **DB_R** | **D**ata**b**ase **R**eplica | Instance MySQL en **lecture seule**. Copie du Master ; on y envoie les requêtes de lecture (listes, rapports) pour ne pas surcharger le Master. |
| **FILES** | Stockage fichiers | Comme en vue globale : S3 ou NFS pour les fichiers déposés. |

**À dire** : REDIS stocke les sessions et le cache. DB_M est la base en écriture, DB_R la réplica en lecture pour répartir la charge. FILES reste le stockage des fichiers.

---

## Slide 9 – Vue déploiement : zone back-office (≈1 min)

**Titre** : Vue déploiement – Zone back-office

| Composant | Signification | Rôle |
|-----------|---------------|------|
| **Q** | **Q**ueue (file d’attente) | **RabbitMQ** ou **Redis** utilisé comme file : on y met les tâches asynchrones (envoi d’emails, génération de rapports). |
| **WORKER** | Workers | Processus qui consomment la file Q : ils envoient les emails et génèrent les rapports sans bloquer les requêtes des utilisateurs. |

**À dire** : Q désigne la file d’attente, souvent RabbitMQ ou Redis. Les workers lisent cette file et exécutent les tâches lourdes (emails, rapports) en arrière-plan. Ainsi, Moodle répond vite même lors d’envois massifs.

---

## Slide 10 – Récap des abréviations (30 s)

**Titre** : Récapitulatif des abréviations

| Abrév. | Signification |
|--------|----------------|
| LB | Load Balancer |
| SSO | Single Sign-On |
| AUTH, CAT, CONT, DEVOIR, FORUM, NOTIF | Services (Auth, Catalogue, Contenu, Devoirs, Forums, Notifications) |
| DB | Database |
| S3 | Stockage objet (ex. Amazon S3) |
| NFS | Network File System |
| DMZ | Demilitarized Zone |
| CDN | Content Delivery Network |
| PHP-FPM | PHP FastProcess Manager |
| DB_M / DB_R | Database Master / Replica |
| Q | Queue (file d’attente) |
| WORKER | Processus qui consomment la queue |

**À dire** : Voici le récap des abréviations. Vous pouvez vous y référer pendant les questions.

---

## Slide 11 – Conclusion (30 s)

**Titre** : Conclusion

- **Vue globale** : acteurs → LB → services (AUTH, CAT, CONT, DEVOIR, FORUM, NOTIF) → données (DB, CACHE, FILES).
- **Vue déploiement** : zones (DMZ → applicative → données → back-office), instances (M1..N), réplication (DB_M / DB_R), file et workers (Q, WORKER).

**À dire** : La vue globale décrit les services métier et les flux ; la vue déploiement décrit où et comment tout est déployé en zones et instances. Merci, nous sommes ouverts à vos questions.

---

## Conseils pour le PowerPoint

1. **Une slide = un tableau** : utiliser les tableaux de ce document pour chaque slide (titres de colonnes : Composant, Signification, Rôle).
2. **Copier les diagrammes** : exporter les blocs Mermaid du `diagramme.md` en PNG (via [mermaid.live](https://mermaid.live)) et les insérer sur les slides « Vue globale » et « Vue déploiement ».
3. **Notes orateur** : coller la partie « À dire » de chaque slide dans les notes du bas de la slide PowerPoint pour vous guider à l’oral.
4. **Chronomètre** : viser environ 1 minute par slide ; raccourcir les tableaux si nécessaire pour rester sous 10 min.
