# eks-sandbox
The EKS Quickstart will quickly spin up an EKS cluster and worker nodes through cloudformation. This requires AWS CLI version 1.15.32, kubectl version 1.10 and the Heptio authenticator.

Click [here](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=eks-quickstart&templateURL=https://s3-us-west-2.amazonaws.com/eks-quickstart-demo/v2/eks-master.yaml) to deploy the cloudformation template in the AWS Console.

QuickStart Proposed Steps:

1. Install CLI Requirements

	Install or update awscli
	Install or update kubectl
	Install or update heptio authenticator

2. Configure Cluster State Storage

	Using S3, we will store the config files that will represent the state of your cluster. This bucket will become the source of truth for our cluster configuration. The following steps create a randomly generated name for this bucket but if you need to send these files to a pre-generated bucket or use a custom naming convention, you can modify the S3_BUCKET variable.

3. Create Service Account and VPC through CF

	This can be done as one step through cloudformation w/in console or aws cli.

4. Create EKS Cluster

	This can be done through eks api or new aws cli.

5. Create Nodes

	This can be done through cloudformation w/in console or aws cli.

6. Install Sample App (Prometheus/KubeUI) through kubectl.
