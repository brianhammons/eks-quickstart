# Quickstart Script
#title           quickstart-configure.sh
#description     This script will make a header for a bash script.
#author          salvot@amazon.com
#date            2018-01-19
#version         0.1
#usage           curl -sSL https://s3.amazonaws.com/lab-ide-theomazonian/lab-ide-build.sh | bash -s stable
#notes           Install Vim and Emacs to use this script.
#==============================================================================

# # Alias kube config to preview config
export OPERATING_SYSTEM=$(echo $(uname) | tr "[:upper:]" "[:lower:]")

if [[ $OPERATING_SYSTEM == 'darwin' ]]; then

elif [[ $OPERATING_SYSTEM == 'darwin' ]]; then
	python -mplatform | grep -qi Ubuntu && apt-get update || grep -qi Darwin && bower update
	sudo yum -y install jq
	sudo yum install bash-completion -y
fi

# Configure AWS CLI
availability_zone=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone)
export AWS_DEFAULT_REGION=${availability_zone%?}

# Lab-specific configuration
export AWS_AVAILABILITY_ZONES="$(aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text | awk -v OFS="," '$1=$1')"
export AWS_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 describe-instances --instance-ids $AWS_INSTANCE_ID > /tmp/instance.json
export AWS_STACK_NAME=$(jq -r '.Reservations[0].Instances[0]|(.Tags[]|select(.Key=="aws:cloudformation:stack-name")|.Value)' /tmp/instance.json)
export AWS_ENVIRONMENT=$(jq -r '.Reservations[0].Instances[0]|(.Tags[]|select(.Key=="aws:cloud9:environment")|.Value)' /tmp/instance.json)
export AWS_MASTER_STACK=${AWS_STACK_NAME%$AWS_ENVIRONMENT}
export AWS_MASTER_STACK=${AWS_MASTER_STACK%?}
export AWS_MASTER_STACK=${AWS_MASTER_STACK#aws-cloud9-}
export KOPS_STATE_STORE=s3://$(aws cloudformation describe-stack-resource --stack-name $AWS_MASTER_STACK --logical-resource-id "KopsStateStore" | jq -r '.StackResourceDetail.PhysicalResourceId')

# Persist lab variables
echo "AWS_AVAILABILITY_ZONES=$AWS_AVAILABILITY_ZONES" >> ~/.bash_profile
echo "KOPS_STATE_STORE=$KOPS_STATE_STORE" >> ~/.bash_profile
echo "export AWS_AVAILABILITY_ZONES KOPS_STATE_STORE" >> ~/.bash_profile

# Create SSH key
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

if [ ! -d "aws-workshop-for-kubernetes/" ]; then
  # Download lab Repository
  git clone https://github.com/aws-samples/aws-workshop-for-kubernetes
fi

