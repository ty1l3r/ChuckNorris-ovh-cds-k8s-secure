# OVH-PROD — Création d'un utilisateur restreint Kubernetes (production)

> Chuck Norris ne génère pas de clés.
> Les autorités de certification le supplient de signer leurs clusters.

---

## Objectif

Ce dossier contient les fichiers relatifs à l'utilisateur restreint ovh-prod, utilisé pour les déploiements production dans le namespace prod. L'objectif est de fournir un accès sécurisé, non-administrateur, limité à ce namespace, avec un rôle RBAC spécifique.

---

## Prérequis
* Cluster K3s avec namespace prod précréé
* Accès root (ou sudo) à la VM

### 1. Génération des fichiers certs (en local)

```bash
# Générer la clé privée
openssl genrsa -out ovh-prod.key 2048

# CSR avec nom CN=ovh-prod
openssl req -new -key ovh-prod.key -out ovh-prod.csr -subj "/CN=ovh-prod"

# Signature avec le client-ca de K3s
sudo openssl x509 -req -in ovh-prod.csr \
  -CA /var/lib/rancher/k3s/server/tls/client-ca.crt \
  -CAkey /var/lib/rancher/k3s/server/tls/client-ca.key \
  -CAcreateserial \
  -out ovh-prod.crt -days 365
```

---

### 2. Récupération du certificat d'autorité du cluster (si pas déjà fait)

```bash
# Extraire la CA publique du cluster
sudo cp /var/lib/rancher/k3s/server/tls/server-ca.crt ./ca/
sudo chown $USER:$USER ./ca/server-ca.crt
chmod 400 ./ca/server-ca.crt
```

---

### 3. Création du kubeconfig pour ovh-prod

```bash
export KUBECONFIG_OVH=./ovh-prod.kubeconfig

# Déclarer le cluster
kubectl config --kubeconfig=$KUBECONFIG_OVH set-cluster k3s-cluster \
  --server=https://127.0.0.1:6443 \
  --certificate-authority=./ca/server-ca.crt \
  --embed-certs=true

# Ajouter les credentials utilisateur
kubectl config --kubeconfig=$KUBECONFIG_OVH set-credentials ovh-prod \
  --client-certificate=ovh-prod.crt \
  --client-key=ovh-prod.key \
  --embed-certs=true

# Contexte isolé dans le namespace `prod`
kubectl config --kubeconfig=$KUBECONFIG_OVH set-context ovh-prod-context \
  --cluster=k3s-cluster \
  --user=ovh-prod \
  --namespace=prod

kubectl config --kubeconfig=$KUBECONFIG_OVH use-context ovh-prod-context
```

---

### 4. Attribution RBAC pour ovh-prod

```bash
# Appliquer le rôle
kubectl apply -f role-ovh-prod.yaml

# Appliquer le binding
kubectl apply -f rolebinding-ovh-prod.yaml
```

Le rôle de ovh-prod est orienté CI/CD :
	•	Plein accès sur le namespace prod
	•	Read-only sur certains objets dans dev (ex: secrets, logs)

---

## Notes finales
* Aucun de ces fichiers .key, .crt, .kubeconfig ne doit être push sur un Git
* Ce fichier README est là pour documenter le processus, pas stocker des secrets
* Si un credential est visible dans le repo, Chuck Norris te retrouvera