# EKS Quickstart Guide 
The EKS Quickstart will quickly spin up an EKS cluster and worker nodes through cloudformation. This will require AWS CLI version 1.15.32+, kubectl version 1.10+ and the aws-iam-authenticator. Please find details in the EKS Getting Started section of the [User Guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html).

Click [here](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=eks-quickstart&templateURL=https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/v3/eks-quickstart.yaml) to deploy the cloudformation template in the AWS Console.

QuickStart Setup Steps:

1. Generate EKS cluster name.
```
export CLUSTER_NAME=eks-demo-$(cat /dev/urandom | LC_ALL=C tr -dc "[:alpha:]" | tr '[:upper:]' '[:lower:]' | head -c 8)
```

2. Create an S3 Bucket to store cluster configuration files.
```
export S3_BUCKET=state-store-$CLUSTER_NAME
```

3. Generate ssh key for worker node access.
```
export SSH_KEY=$CLUSTER_NAME-keypair
mkdir ~/.ssh | aws ec2 create-key-pair --key-name $SSH_KEY >> ~/.ssh/$SSH_KEY.pem
```

4. You may run the cloudformation template from the link above or using the command line.
```
aws cloudformation create-stack --stack-name $CLUSTER_NAME \
--template-url https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/eks-quickstart.yaml \
--parameters ParameterKey=ClusterName,ParameterValue=$CLUSTER_NAME ParameterKey=NodeGroupName,ParameterValue=$CLUSTER_NAME-nodegroup ParameterKey=KeyName,ParameterValue=$SSH_KEY ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET \
--capabilities "CAPABILITY_IAM"
```	

5. Create local Kubernetes configuration directory and download EKS config file after cluster is ready. (Should be complete in ~9-10 minutes)
```
aws s3 cp s3://$S3_BUCKET/$CLUSTER_NAME/config ~/.kube/config-$CLUSTER_NAME
export KUBECONFIG=$KUBECONFIG:~/.kube/config-$CLUSTER_NAME
```

6. Apply generated auth model.
```
aws s3 cp s3://$S3_BUCKET/$CLUSTER_NAME/aws-auth-cm.json ~/.kube/$CLUSTER_NAME/aws-auth-cm.json
kubectl apply -f ~/.kube/$CLUSTER_NAME/aws-auth-cm.json
```

7. Test that cluster is active.
```
kubectl get nodes
```
