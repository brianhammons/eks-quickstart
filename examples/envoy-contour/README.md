## Service Mesh and Ingress
By using Contour as an Ingress Controller, the Envoy configuration is exposed as Kubernetes Ingress Resources. Using Envoy as a service mesh and Contour as an ingress controller, we are able to control the flow of traffic and proxy to downstream services.

# Setup Steps:
1. Add Contour to your cluster with the relevant RBACs.
```
$ kubectl apply -f https://j.hept.io/contour-deployment-rbac
```

This command creates:
```
A new namespace heptio-contour with two instances of Contour in the namespace
A Service of type: LoadBalancer that points to the Contour instances
Depending on your configuration, new cloud resources -- for example, ELBs in AWS
```

2. Run sample kuard workload.
```
$ kubectl apply -f https://j.hept.io/contour-kuard-example
```

3. Retrieve external address to Contour load balancer.
```
$ kubectl get -n heptio-contour service contour -o wide
```

4. You may now access the sample website by navigating to load balancer address. If you'd like to configure DNS, create a CNAME that maps to this ELB address.