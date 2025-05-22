# build/Dockerfile

# ──────────────────────────────────────────────────────────────
# 🐳 Image multi-étapes sécurisée pour Flask (Chuck Norris Facts)
# - Utilisateur non-root
# - Dependencies isolées
# - Compatible Kubernetes (SecurityContext, readonly root, etc.)
# ──────────────────────────────────────────────────────────────

# Étape 1 : build
FROM python:3.11-slim AS builder

# Créer un utilisateur non-root
ARG UID=1000
ARG GID=1000
RUN addgroup --gid ${GID} app && \
    adduser --uid ${UID} --gid ${GID} --disabled-password --gecos "" app

# Dépendances
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Étape 2 : image finale propre
FROM python:3.11-slim

# Même utilisateur non-root
ARG UID=1000
ARG GID=1000
RUN addgroup --gid ${GID} app && \
    adduser --uid ${UID} --gid ${GID} --disabled-password --gecos "" app

# Copier uniquement ce qui est nécessaire
COPY --from=builder /install /usr/local
COPY app.py /app/app.py

# Dossier de travail sécurisé
WORKDIR /app

# Utiliser un utilisateur non-root
USER app

# Port exposé pour K8s Service
EXPOSE 5000

# Démarrage de l'application
CMD ["python", "app.py"]