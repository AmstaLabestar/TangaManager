# Déploiement (Docker + Nginx) — Guide rapide

1) Préparer l'environnement

- Copier le fichier d'exemple et le mettre à jour:

```bash
cp .env.prod.example .env.prod
# Éditez .env.prod: DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, DATABASE_URL, REDIS_URL
```

2) Construire et lancer les services en production

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3) Appliquer les migrations, collectstatic et créer un admin

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

4) Déploiement sur Render

- Render est bien adapté à ce projet grâce au Dockerfile existant.
- Le fichier `render.yaml` définit un service Web et un worker Docker.
- Un workflow GitHub Actions a été ajouté pour déployer automatiquement sur Render après un push vers `master`.

Commandes Render:

```bash
render login
render deploy --confirm
```

Dans le dashboard Render, ajoutez les variables:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=["your.domain.com"]`
- `DJANGO_CSRF_TRUSTED_ORIGINS=["https://your.domain.com"]`
- `DATABASE_URL`
- `REDIS_URL`
- `DEFAULT_FROM_EMAIL`

Ajoutez également ce secret à GitHub pour le workflow Render :
- `RENDER_API_KEY`

Render recommande de créer un service PostgreSQL géré et un service Redis géré. Vous pouvez utiliser ces URLs dans `DATABASE_URL` et `REDIS_URL`.

5) Déploiement sur Vercel (optionnel)

- Vercel peut déployer le projet via Docker avec `vercel.json` et `Dockerfile`.
- Ce route est possible, mais pas idéale pour une application Django complète : vous aurez besoin d'une base de données Postgres externe et d'un Redis externe.

Dans Vercel, configurez les variables d'environnement:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=["your.domain.com"]`
- `DJANGO_CSRF_TRUSTED_ORIGINS=["https://your.domain.com"]`
- `DATABASE_URL`
- `REDIS_URL`
- `DEFAULT_FROM_EMAIL`

6) Activer HTTPS (optionnel mais recommandé)

- Utiliser `certbot` ou un reverse-proxy géré pour obtenir des certificats. Exemple rapide avec `certbot` sur l'hôte:

  - Arrêter nginx container ou ouvrir port 80 vers certbot.
  - Suivre la doc Certbot pour docker/nginx.

7) Opérations courantes

- Pour redéployer après changement de code:

```bash
docker compose -f docker-compose.prod.yml up -d --build web
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

Notes:
- Le fichier `docker/nginx.conf` sert de point de départ; adaptez `server_name` et règles caching.
- Assurez-vous que `.env.prod` est stocké de façon sécurisée (vault, secret manager, ou variables CI/CD).
