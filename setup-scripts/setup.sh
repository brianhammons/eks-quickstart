# #!/bin/bash

# # Install custom model for Amazon EKS
aws s3 cp --recursive s3://amazon-eks/$1/ ./packages
echo ""
echo "Install custom service model"
export CURRENT_LOCATION=$(pwd)
aws configure add-model --service-model file://$CURRENT_LOCATION/packages/eks-2017-11-01.normal.json --service-name eks

# # Install kubectl binary
echo "Install kubectl binary"
if [ ! -d $HOME/bin ]; then 
	mkdir $HOME/bin
fi

# # Create .kube folder if not exists
if [ ! -d $HOME/.kube ]; then 
	mkdir $HOME/.kube
fi

# # Alias kube config to preview config
export OPERATING_SYSTEM=$(echo $(uname) | tr "[:upper:]" "[:lower:]")
export KUBECTL_PACKAGE="./packages/bin/$OPERATING_SYSTEM/amd64/kubectl"
chmod +x $KUBECTL_PACKAGE
cp $KUBECTL_PACKAGE	$HOME/bin/kubectl

# # Alias kube config to preview config
export HEPTIO_AUTH="./packages/bin/$OPERATING_SYSTEM/amd64/heptio-authenticator-aws"
chmod +x $HEPTIO_AUTH
cp $HEPTIO_AUTH	$HOME/bin/heptio-authenticator-aws

export PATH=$HOME/bin:$PATH
export KUBECONFIG=$KUBECONFIG:~/.kube/config-preview