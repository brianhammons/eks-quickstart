## Helm and Tiller
Helm is a Kubernetes package manager used to find, share, and use software built for Kubernetes. There are two parts to Helm: The Helm client and Tiller, the Helm server. The following steps will take you through this setup on EKS.

# Setup Steps:
1. If you are using a Mac, use Homebrew to install helm binary:
```
$ brew install kubernetes-helm
```

2. To deploy Tiller into your existing EKS cluster, enter the following:
```
$ helm init
```
and run an update to get latest repo information:
```
$ helm repo update
```

3. Helm runs with default service account so perform the following steps to configure access:
```
$ kubectl create serviceaccount --namespace kube-system tiller
$ kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
$ kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'      
$ helm init --service-account tiller --upgrade
```