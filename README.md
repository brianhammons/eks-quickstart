# EKS Quickstart Guide 
### This is a WIP, feel free to contribute directly and enter a PR.
The EKS Quickstart will quickly spin up an EKS cluster and worker nodes through cloudformation. This requires AWS CLI version 1.15.32, kubectl version 1.10 and the Heptio authenticator. Please find details in the EKS Getting Started section of the [User Guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html).

Click [here](https://us-west-2.console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=eks-quickstart&templateURL=https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/v2/eks-quickstart.template) to deploy the cloudformation template in the AWS Console.

QuickStart Setup Steps:

1. Create an S3 Bucket to store cluster configuration files. May auto-generate with command below or enter your own unique bucket name.
```
$ export S3_BUCKET=eks-state-store-$(cat /dev/urandom | LC_ALL=C tr -dc "[:alpha:]" | tr '[:upper:]' '[:lower:]' | head -c 32)
$ export EKS_STATE_STORE=s3://${S3_BUCKET}
```

2. Set configuration variables for the EKS cluster name and ssh key for worker node access.
```
$ export CLUSTER_NAME=eks-demo
$ export SSH_KEY=eks-demo-key
```

3. You may run the cloudformation template from the link above or using the command line.
```
$ aws cloudformation create-stack --stack-name $CLUSTER_NAME-stack \
--template-url https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/v2/eks-quickstart.yaml \
--parameters ParameterKey=ClusterName,ParameterValue=$CLUSTER_NAME ParameterKey=NodeGroupName,ParameterValue=$CLUSTER_NAME-nodegroup ParameterKey=KeyName,ParameterValue=$SSH_KEY ParameterKey=S3Bucket,ParameterValue=$S3_BUCKET \
--capabilities "CAPABILITY_IAM"
```	

4. Create local Kubernetes configuration directory and download EKS config file after cluster is ready. (Should be complete in ~9-10 minutes)
```
$ mkdir ~/.kube && aws s3 cp s3://$S3_BUCKET/$CLUSTER_NAME/config ~/.kube/config
```

5. Apply generated auth model.
```
$ kubectl apply -f https://s3.amazonaws.com/$S3_BUCKET/$CLUSTER_NAME/aws-auth-cm.json
```

6. Test that cluster is active.
```
$ kubectl get nodes
```
