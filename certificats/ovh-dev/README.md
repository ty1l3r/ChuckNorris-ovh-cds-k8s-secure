# OVH-DEV — Création d'un utilisateur restreint Kubernetes (développement)

> Chuck Norris ne demande jamais d'accès.
> Le kube-apiserver l'ajoute automatiquement dans le groupe system:masters.

---

## Objectif

Ce dossier contient la définition d'un utilisateur Kubernetes restreint (« ovh-dev ») pour le namespace dev, avec RBAC limité.

Ce README explique comment :
* générer une paire clé/certificat client,
* créer un kubeconfig dédié,
* restreindre l'accès via un Role et RoleBinding.

---

## Prérequis
* Un cluster K3s fonctionnel
* Un accès root (ou sudo) pour extraire les certificats du cluster

### 1. Génération de la clé et du certificat client

```bash
# Générer une clé privée pour l'utilisateur
openssl genrsa -out ovh-dev.key 2048

# Créer une requête de signature (CSR)
openssl req -new -key ovh-dev.key -out ovh-dev.csr -subj "/CN=ovh-dev"

# Signer le certificat avec l'autorité client de K3s (valable 365 jours)
sudo openssl x509 -req -in ovh-dev.csr \
  -CA /var/lib/rancher/k3s/server/tls/client-ca.crt \
  -CAkey /var/lib/rancher/k3s/server/tls/client-ca.key \
  -CAcreateserial \
  -out ovh-dev.crt -days 365
```

---

### 2. Extraction du certificat d'autorité (CA)

```bash
# Copier le certificat d'autorité (pour kubeconfig)
sudo cp /var/lib/rancher/k3s/server/tls/server-ca.crt ./ca/

# Changer les permissions pour éviter les sudo
sudo chown $USER:$USER ./ca/server-ca.crt
chmod 400 ./ca/server-ca.crt
```

---

### 3. Génération du fichier kubeconfig

```bash
# Définir le chemin de sortie
export KUBECONFIG_OVH=./ovh-dev.kubeconfig

# Ajouter le cluster (avec certificat CA embarqué)
kubectl config --kubeconfig=$KUBECONFIG_OVH set-cluster k3s-cluster \
  --server=https://127.0.0.1:6443 \
  --certificate-authority=./ca/server-ca.crt \
  --embed-certs=true

# Ajouter les credentials utilisateur (certificat + clé)
kubectl config --kubeconfig=$KUBECONFIG_OVH set-credentials ovh-dev \
  --client-certificate=ovh-dev.crt \
  --client-key=ovh-dev.key \
  --embed-certs=true

# Créer le contexte
kubectl config --kubeconfig=$KUBECONFIG_OVH set-context ovh-dev-context \
  --cluster=k3s-cluster \
  --user=ovh-dev \
  --namespace=dev

# Activer le contexte par défaut
kubectl config --kubeconfig=$KUBECONFIG_OVH use-context ovh-dev-context
```

---

### 4. Attribution des permissions (RBAC)

Les fichiers suivants définissent les permissions exactes de ovh-dev :
	•	role-ovh-dev.yaml : accès aux pods, services, configmaps, etc.
	•	rolebinding-ovh-dev.yaml : attache le rôle à l’utilisateur dans le namespace dev

Appliquer les rôles :

```bash
kubectl apply -f role-ovh-dev.yaml
kubectl apply -f rolebinding-ovh-dev.yaml
```


---

## Notes
	•	Ne jamais versionner les fichiers .key, .crt, .kubeconfig
	•	Ce dossier est volontairement partiel pour montrer la mécanique, pas les secrets
	•	Compatible avec PodSecurity Standards niveau restricted

---

→ Pour un deuxième utilisateur (ex: ovh-prod), suivre la même logique avec un namespace différent et un rôle ajusté.