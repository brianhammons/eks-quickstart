# Istio Guide 
The Istio project is a leading example of a new class of projects called Service Meshes. Service meshes manage traffic between microservices at Layer 7 of the OSI Model. Using this practice of traffic semantics – for example HTTP request hosts, methods, and paths – traffic handling can be much more sophisticated.

Setup Steps:

1. Download Istio Deployment Files
```
curl -L https://git.io/getLatestIstio | sh -
cd istio-1.0.2
export PATH=$PWD/bin:$PATH
```

2. Configure Helm and Tiller
```
kubectl create -f install/kubernetes/helm/helm-service-account.yaml
helm init --service-account tiller
```

3. Install Istio
```
helm install \
--wait \
--name istio \
--namespace istio-system \
install/kubernetes/helm/istio \
--set global.configValidation=false \
--set sidecarInjectorWebhook.enabled=false
```

4. Deploy Istio custom resources
```
kubectl apply -f install/kubernetes/helm/istio/templates/crds.yaml
```	

6. Install sample app (Bookinfo)
```
kubectl apply -f <(istioctl kube-inject -f samples/bookinfo/platform/kube/bookinfo.yaml)
```

7. Expose Bookinfo - deploy Gateway resource
```
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml
```

8. Expose Bookinfo - host and port mapping
```
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

9. Navigate to Bookinfo landing page
- Retrieve GATEWAY_URL
```
echo $GATEWAY_URL
```
- Browse to http://$GATEWAY_URL/productpage, the Bookinfo landing page. Replace $GATEWAY_URL with the value we just assigned to it or open http://$GATEWAY_URL/productpage.
