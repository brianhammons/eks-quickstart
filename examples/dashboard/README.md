## Kubernetes Dashboard
Use the following steps to deploy the Kubernetes dashboard, heapster, and the influxdb backend for CPU and memory metrics to your cluster.

# Setup Steps:
1. Deploy Kubernetes Dashboard
```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
```

2. Deploy Heapster
```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/influxdb/heapster.yaml
```

3. Deploy InfluxDB
```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/influxdb/influxdb.yaml
```	

4. Bind heapster cluster role for Dashboard
```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/heapster/master/deploy/kube-config/rbac/heapster-rbac.yaml
```

5. Apply service account to cluster
```
$ kubectl apply -f https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/templates/eks-admin-service-account.yaml
```

6. Apply cluster role to cluster
```
$ kubectl apply -f https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/templates/eks-admin-cluster-role-binding.yaml
```
7. Copy authentication token from "token" field
```
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep eks-admin | awk '{print $1}')
```
8. Start kubectl proxy
```
kubectl proxy
```
9. Open the following link: http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/

10. Choose <b>Token</b> and paste copied authentication token into <b>Enter token</b> field. Press <b>Sign In</b> button.