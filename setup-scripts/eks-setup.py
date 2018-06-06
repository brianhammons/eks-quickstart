import boto3
import time
import os
import yaml

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from os.path import expanduser

# Set Global Variables
global SERVICE_STACK
global VPC_STACK
global CLUSTER_NAME
global NODE_STACK
global NODE_GROUP
global ASG_MIN
global ASG_MAX
global NODE_INSTANCE_TYPE
global SSH_KEY

# Set User Inputs
SERVICE_STACK = raw_input("Input cloudformation stack name for IAM Service Role: ")
VPC_STACK = raw_input("Input cloudformation stack name for VPC: ")
CLUSTER_NAME = raw_input("Input cluster name: ")
NODE_STACK = raw_input("Input cloudformation stack name for worker nodes: ")
NODE_GROUP = raw_input("Enter a name for your node group that is included in your Auto Scaling node group name: ")
ASG_MIN = raw_input("Enter the minimum number of nodes that your worker node Auto Scaling group can scale in to: ")
ASG_MAX = raw_input("Enter the maximum number of nodes that your worker node Auto Scaling group can scale out to: ")
NODE_INSTANCE_TYPE = raw_input("Choose an instance type for your worker nodes: ")
SSH_KEY = raw_input("Enter the name of an Amazon EC2 SSH key pair that you can use to connect using SSH into your worker nodes: ")

# Configuration Variables
HOME = expanduser("~")
PACKAGE_DATE = "1.10.0/2018-05-09"
EKS_WORKER_AMI = "ami-993141e1"
SERVICE_TEMPLATE_LOCATION = "https://amazon-eks.s3-us-west-2.amazonaws.com/" + PACKAGE_DATE + "/amazon-eks-service-role.yaml"
VPC_TEMPLATE_LOCATION = "https://amazon-eks.s3-us-west-2.amazonaws.com/" + PACKAGE_DATE + "/amazon-eks-vpc-sample.yaml"
NODE_TEMPLATE_LOCATION = "https://amazon-eks.s3-us-west-2.amazonaws.com/" + PACKAGE_DATE + "/amazon-eks-nodegroup.yaml"

# Initialize Cloudformation Client
client = boto3.client('cloudformation')

def run_setup_script(eks_version):
	call(["chmod", "+x", "./setup.sh"])
	call(["sh", "./setup.sh", eks_version])
	return

def create_eks_role(service_template):
	global ROLE_ARN
	SERVICE_ROLE_RESPONSE = client.create_stack(
	    StackName = SERVICE_STACK,
	    TemplateURL = service_template,
	    Capabilities = [
	        'CAPABILITY_IAM',
	    ]
	)
	flag = True
	for i in range(0,100):
	    while flag == True:
	        try:
		    	time.sleep(15)
		    	ROLE_STACK_ARN = client.describe_stacks(StackName = SERVICE_ROLE_RESPONSE['StackId'])
		    	ROLE_ARN = ROLE_STACK_ARN['Stacks'][0]['Outputs'][0]['OutputValue']
		    	flag = False   	
		    	break
	        except KeyError:
	        	pass
	return
	
def create_vpc(vpc_template):
	global VPC_ID
	global VPC_SUBNET
	global VPC_SECURITY_GROUP
	VPC_RESPONSE = client.create_stack(
	    StackName = VPC_STACK,
	    TemplateURL = vpc_template,
	    Parameters = [
	        {
	            'ParameterKey': 'ClusterName',
	            'ParameterValue': CLUSTER_NAME
	        },
	    ],
	    Capabilities = [
	        'CAPABILITY_IAM',
	    ]
	)
	flag = True
	for i in range(0,100):
	    while flag == True:
	        try:
		    	time.sleep(15)
		    	# Describe VPC
		    	VPC_INFO = client.describe_stacks(StackName = VPC_RESPONSE['StackId'])
		    	VPC_SECURITY_GROUP = VPC_INFO['Stacks'][0]['Outputs'][0]['OutputValue']
		    	VPC_SUBNET = VPC_INFO['Stacks'][0]['Outputs'][2]['OutputValue']
		    	# Get VPC_ID
		    	VPC_RESOURCE_INFO = client.describe_stack_resource(StackName = VPC_RESPONSE['StackId'], LogicalResourceId = 'VPC')
		    	VPC_ID = VPC_RESOURCE_INFO['StackResourceDetail']['PhysicalResourceId']
		    	flag = False   	
		    	break
	        except KeyError:
	        	pass
	return

def create_nodes(node_template):
	global NODE_INSTANCE_ROLE
	SUBNET_BLOCK = VPC_SUBNET.split(" ")[0] + ',' + VPC_SUBNET.split(" ")[1]
	NODE_RESPONSE = client.create_stack(
	    StackName = NODE_STACK,
	    TemplateURL = node_template,
	    Parameters = [
	        {
	            'ParameterKey': 'ClusterName',
	            'ParameterValue': CLUSTER_NAME
	        },
	        {
	            'ParameterKey': 'ClusterControlPlaneSecurityGroup',
	            'ParameterValue': VPC_SECURITY_GROUP
	        },
	        {
	            'ParameterKey': 'NodeGroupName',
	            'ParameterValue': NODE_GROUP
	        },
	        {
	            'ParameterKey': 'NodeAutoScalingGroupMinSize',
	            'ParameterValue': ASG_MIN
	        },
	        {
	            'ParameterKey': 'NodeAutoScalingGroupMaxSize',
	            'ParameterValue': ASG_MAX
	        },
	        {
	            'ParameterKey': 'NodeInstanceType',
	            'ParameterValue': NODE_INSTANCE_TYPE
	        },
	        {
	            'ParameterKey': 'NodeImageId',
	            'ParameterValue': EKS_WORKER_AMI
	        },
	        {
	            'ParameterKey': 'KeyName',
	            'ParameterValue': SSH_KEY
	        },
	        {
	            'ParameterKey': 'VpcId',
	            'ParameterValue': VPC_ID
	        },
	        {
	            'ParameterKey': 'Subnets',
	            'ParameterValue': SUBNET_BLOCK
	        }
	    ],
	    Capabilities = [
	        'CAPABILITY_IAM',
	    ]
	)
	flag = True
	for i in range(0,100):
	    while flag == True:
	        try:
		    	time.sleep(15)
		    	NODE_STACK_INFO = client.describe_stacks(StackName = NODE_RESPONSE['StackId'])
		    	NODE_INSTANCE_ROLE = NODE_STACK_INFO['Stacks'][0]['Outputs'][0]['OutputValue']
		    	flag = False   	
		    	break
	        except KeyError:
	        	pass
	return

def enable_nodes(node_instance_role):
	config_map = dict({
	   "apiVersion": "v1",
	   "kind": "ConfigMap",
	   "metadata": {
	      "name": "aws-auth",
	      "namespace": "default"
	   },
	   "data": {
	      "mapRoles": "- rolearn: " + node_instance_role + "\n  username: system:node:{{EC2PrivateDNSName}}\n  groups:\n    - system:bootstrappers\n    - system:nodes\n    - system:node-proxier\n"
	   }
	})
	MAP_LOCATION = './packages/aws-auth-cm.yaml'
	with open(MAP_LOCATION, 'w') as outfile:
	    yaml.dump(config_map, outfile, default_flow_style=False, allow_unicode=True)
	call(["kubectl", "apply", "-f", MAP_LOCATION])
	return

def describe_cluster(cluster):
	global STATUS
	global MASTER_ENDPOINT
	global CA
	STATUS = ""
	for i in range(0,100):
	    while STATUS != "ACTIVE":
	    	time.sleep(15)
	    	STATUS = Popen(["aws", "eks", "describe-cluster", "--region", "us-west-2", "--cluster-name", cluster, "--query", "cluster.status"], stdout=PIPE).communicate()[0].strip().replace('"','')
	MASTER_ENDPOINT = Popen(["aws", "eks", "describe-cluster", "--region", "us-west-2", "--cluster-name", cluster, "--query", "cluster.masterEndpoint"], stdout=PIPE).communicate()[0].strip().replace('"','')
	CA = Popen(["aws", "eks", "describe-cluster", "--region", "us-west-2", "--cluster-name", cluster, "--query", "cluster.certificateAuthority.data"], stdout=PIPE).communicate()[0].strip().replace('"','')
	return

def config_generator(endpoint, certificate, cluster):
	kube_config = dict({
	  "apiVersion": "v1",
	  "clusters": [
	    {
	      "cluster": {
	        "server": endpoint,
	        "certificate-authority-data": certificate
	      },
	      "name": "kubernetes"
	    }
	  ],
	  "contexts": [
	    {
	      "context": {
	        "cluster": "kubernetes",
	        "user": "aws"
	      },
	      "name": "aws"
	    }
	  ],
	  "current-context": "aws",
	  "kind": "Config",
	  "preferences": {
	  },
	  "users": [
	    {
	      "name": "aws",
	      "user": {
	        "exec": {
	          "apiVersion": "client.authentication.k8s.io/v1alpha1",
	          "command": "heptio-authenticator-aws",
	          "args": [
	            "token",
	            "-i",
	            cluster
	          ]
	        }
	      }
	    }
	  ]
	})
	
	# # Add under cluster if you'd like to assign a role to authenticator
	# "-r",
	# "<role-arn>"

	CONFIG_LOCATION = HOME + '/.kube/config-preview'
	with open(CONFIG_LOCATION, 'w') as outfile:
	    yaml.dump(kube_config, outfile, default_flow_style=False, allow_unicode=True)
	call(["kubectl", "config", "use-context", "aws"])
	return

def cleanup():
	call(["rm", "-r", "packages/"])
	return

if __name__ == '__main__':
	start = time.time()
	print("")
	print("Download EKS package.")
	run_setup_script(PACKAGE_DATE)
	print("")

	print("Creating EKS service role.")
	create_eks_role(SERVICE_TEMPLATE_LOCATION)
	print("")

	print("Creating EKS VPC.")
	create_vpc(VPC_TEMPLATE_LOCATION)
	print("")

	print("Creating EKS cluster. This may take a few minutes...")
	call(["aws", "eks", "create-cluster", "--cluster-name", CLUSTER_NAME, "--role-arn", ROLE_ARN, "--subnets", VPC_SUBNET.split(" ")[0], VPC_SUBNET.split(" ")[1], "--security-groups", VPC_SECURITY_GROUP])
	describe_cluster(CLUSTER_NAME)
	print("")

	print("Configuring kubectl for Amazon EKS.")
	config_generator(MASTER_ENDPOINT, CA, CLUSTER_NAME)
	print("")

	print("Create worker nodes.")
	create_nodes(NODE_TEMPLATE_LOCATION)
	print("")

	print("Configure worker nodes.")
	enable_nodes(NODE_INSTANCE_ROLE)
	print("Setup Complete!")

	end = time.time()
	elapsed = (end - start) / 60
	print("Time elapsed: " + str(elapsed))