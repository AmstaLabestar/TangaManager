# TANGA Manage Support

Application de gestion des fiches d'installation TANGA GROUP.

Le projet vise a numeriser le parcours terrain d'un technicien apres le deploiement d'une solution chez un client : collecte des informations client, choix de la solution installee, checklist de mise en service, note de formation, signatures client/technicien, puis generation d'un recapitulatif exploitable par le bureau TANGA GROUP.

## Objectif produit

Remplacer la fiche papier de reception par une application mobile-first, simple a utiliser sur le terrain, capable de :

- guider le technicien en 4 etapes ;
- enregistrer une fiche signee avec un statut clair ;
- adapter la checklist selon la solution installee ;
- produire un PDF de reception ;
- envoyer un recapitulatif WhatsApp au client ;
- creer des jalons de suivi J+2, J+7 et J+30 ;
- permettre a l'equipe interne de consulter et exporter les installations.

## Documents de reference

- `TANGA_Fiche_Installation.html` : prototype HTML/CSS/JS existant du formulaire mobile.
- `contexte_entreprise.md` : contexte metier, donnees attendues, roles, checklists et actions apres validation.
- `SPECIFICATION_FONCTIONNELLE.md` : specification consolidee de l'application cible.
- `PLAN_DEVELOPPEMENT.md` : phases de realisation proposees.
- `SUIVI_PROJET.md` : tableau de suivi des taches.
- `MODELE_DONNEES.md` : modele de donnees initial a implementer.

## Parcours utilisateur v1

La v1 priorise le role Technicien.

1. Le technicien ouvre une nouvelle fiche.
2. Il renseigne les informations client et la date d'installation.
3. Il selectionne la solution installee.
4. Il renseigne le materiel : numero de serie, quantite, firmware, WiFi, IP, acces distant.
5. Il complete la checklist de mise en service.
6. Il note la maitrise du client apres formation.
7. Le client et le technicien signent.
8. La fiche passe au statut `signee`.
9. Le systeme declenche les actions de suivi : jalons, PDF, recap WhatsApp.

## Solutions gerees

| Code | Label | Checklist |
|---|---|---|
| `presencerh_rfid` | PresenseRH RFID | `default` |
| `presencerh_bio` | PresenseRH Biometrique | `default` |
| `presencerh_qr` | PresenseRH QR Code | `default` |
| `feelback` | FeelBack Terminal | `feelback` |
| `smartcard` | SmartCard / Carte fidelite | `smartcard` |
| `kuilinga` | KUILINGA Ecole | `default` |

## Stack technique

- Backend : Django + Django REST Framework
- Authentification : sessions Django ou JWT selon client web/mobile
- Taches asynchrones : Celery + Redis
- PDF : WeasyPrint
- WhatsApp : Twilio
- Base de donnees : PostgreSQL en production, SQLite possible en local
- Frontend v1 : templates Django ou SPA legere, en conservant le design mobile du prototype HTML
- Conteneurs : Docker + Docker Compose
- CI/CD : GitHub Actions

## Structure technique

```text
.
+-- apps/
|   +-- installations/      # App metier des fiches d'installation
+-- config/                 # Configuration Django, URLs, WSGI/ASGI, Celery
+-- docker/                 # Scripts d'entree conteneur
+-- .github/workflows/      # CI et publication Docker
+-- Dockerfile
+-- docker-compose.yml
+-- manage.py
+-- requirements.txt
```

## Installation locale

Prerequis :

- Python 3.11+
- Git
- Redis si les taches Celery sont testees localement
- PostgreSQL recommande pour se rapprocher de la production

Creer un environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Installer les dependances :

```powershell
pip install -r requirements.txt
```

Verifier le projet Django :

```powershell
python manage.py check
python manage.py test
```

Lancer en local sans Docker :

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Lancer Celery quand les taches asynchrones seront implementees :

```powershell
celery -A config worker -l info
```

## Lancement avec Docker

Creer le fichier `.env` depuis l'exemple :

```powershell
Copy-Item .env.example .env
```

Construire et lancer les services :

```powershell
docker compose up --build
```

Services disponibles :

- Application Django : `http://localhost:8000`
- Healthcheck : `http://localhost:8000/health/`
- Admin Django : `http://localhost:8000/admin/`
- PostgreSQL : `localhost:5432`
- Redis : `localhost:6379`

Commandes utiles :

```powershell
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose exec web python manage.py check
docker compose down
```

## CI/CD GitHub Actions

Deux workflows sont prepares :

- `.github/workflows/ci.yml`
  - installe les dependances Python ;
  - lance `python manage.py check` ;
  - lance les tests Django ;
  - construit l'image Docker.

- `.github/workflows/cd.yml`
  - se declenche sur `main` ou manuellement ;
  - construit l'image Docker ;
  - publie l'image dans GitHub Container Registry : `ghcr.io/<owner>/<repo>`.

Le deploiement serveur final reste a brancher selon l'hebergeur choisi.

## Git

Le remote attendu est :

```powershell
git remote add origin https://github.com/AmstaLabestar/TangaManager.git
```

La politique du depot est de ne pas versionner les fichiers Markdown de cadrage, sauf `README.md`. Cette regle est appliquee dans `.gitignore` :

```gitignore
*.md
!README.md
```

## Variables d'environnement prevues

```env
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DATABASE_URL=
REDIS_URL=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=
DEFAULT_FROM_EMAIL=
```

## Statuts d'une fiche

- `brouillon` : fiche commencee mais non signee.
- `validee` : fiche complete avant signature finale, si cette etape est conservee.
- `signee` : fiche signee par le client et le technicien.

## Regles importantes

- Le numero de serie est obligatoire.
- La solution installee est obligatoire.
- Les signatures client et technicien sont obligatoires pour finaliser.
- La note de formation doit etre comprise entre 1 et 5.
- La checklist depend de la solution.
- Les donnees de signature doivent etre conservees comme images PNG ou fichiers media.
- Apres signature, les actions automatiques ne doivent pas bloquer l'utilisateur : elles doivent partir en tache de fond.

## Etat actuel

Le depot contient aujourd'hui :

- le prototype statique existant ;
- une premiere application Django fonctionnelle pour creer une fiche signee ;
- une interface mobile-first avec checklist dynamique et signatures canvas ;
- les modeles `InstallationFiche`, `ChecklistItem` et `Jalon` ;
- l'administration Django des fiches, checklists et jalons ;
- une configuration Docker Compose avec Django, PostgreSQL, Redis et Celery ;
- une CI GitHub Actions ;
- une CD de publication d'image Docker vers GHCR.

Les prochaines etapes sont d'ajouter la generation PDF, l'envoi WhatsApp Twilio, le dashboard commercial/admin et les exports.
