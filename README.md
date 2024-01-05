# PyKMIP w/ MongoDB CSFLE in Orchestrated Containers

### FOR DEMONSTRATION PURPOSES ONLY

This project deploys a PyKMIP server, MongoDB enterprise replica set with KMIP encryption at rest, and contains python examples of using Client-Side Field Level Encryption (CSFLE) that uses KMIP for KMS.

### Prerequisites

1. Kubernetes cluster

Consider using docker desktop, k3s, or k3d to deploy a k8s cluster on your workstation.

2. cert-manager

Install cert-manager in your k8s clusters and configure it to watch all namespaces.

3. MongoDB Kubernetes Operator (Community)

We will use the Community Operator to avoid the overhead of running Ops Manager on your workstation.  For this demonstration, I am using the pymongo namespace in my test cluster.

Note that we are overriding the container registry and repository to use the MongoDB enterprise binaries (necessary for KMIP support), base ubi8 is the default here.

```
helm repo add mongodb https://mongodb.github.io/helm-charts
helm install community-operator mongodb/community-operator --namespace pymongo --create-namespace --set mongodb.name=mongodb-enterprise-server --set mongodb.repo=docker.io/mongodb
```

4. Deploy the resource manifests in the ./deploy directory

```
kubectl apply -f deploy/00_certificates.yaml -n pymongo
kubectl apply -f deploy/10_pykmip_server.yaml -n pymongo
kubectl apply -f deploy/20_mongodb.yaml -n pymongo
```

### CSFLE

1. Apply test app deployments, tools are available in the container images.

### FAQ

Slack me.
