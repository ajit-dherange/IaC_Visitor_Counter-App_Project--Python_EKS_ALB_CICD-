# IaC_Visitor_Counter-App_Project-Python_EKS_ALB_CICD


**TASKS:**

1.	[Application]
Create an application featuring a webpage displaying the message "This is the <x> visitor," where <x> is a counter fetched from Redis. The counter should increment with each visit to the index page. The application should be dockerize

2.	[CI/CD Pipeline] 
Pipeline for the automated deployment of the above application to production using GitLab. 

3.	[Cloud infrastructure] 
Deploy an Amazon EKS cluster using Infrastructure as Code (IaC) with Terraform.

4.  [Infra Design]
Draw infrastructure design diagram


## Solution:

**Pre-requisite:**
```
Download this repo in your PC and make sure below app installed in your PC
Git 
Docker
Terraform
AWSCLI
eksctl
Kubectl
```
***Please Note: replace your dockerhub id with ardher***

### Option 1: Deploy visitor counter app to EKS with Load Balancer using Docker Hub`

**Step 1) Build Image and Push to Docker Hub**

```
I) Build Container image
# Goto the folder visitor-app and run below commands:
$  docker build -t visitorcountapp .

I) Push Container image
$  docker tag visitorcountapp ardher/visitorcountapp:latest 
$  docker login
$  docker push ardher/visitorcountapp:latest 
```

**Step 2) Create EKS Cluster**
```
I) Deploy EKS Cluster
# Pre=requisite:- Login to aws concole, Goto to VPC, Copy the default VPC ID and update in the file _vars.tf_ from the folder EKS-AD (line no. 7)
# Goto the folder IaC-EKS-AD and run below commands:
$  aws configure 
$  terraform init
$  terraform plan
$  terraform apply

II) Connect to EKS cluster
# Goto the folder EKS-Deployments and run below commands to connect to EKS cluster and check resources
aws eks update-kubeconfig --name myekstest-cluster-01
$  kubectl get svc
$  kubectl get nodes
$  kubectl get pods

III) Deploy visitor-app Application 
$  kubectl apply -f visitor-app-deploy.yml
$  kubectl apply -f visitor-app-redis-deploy.yml
$  kubectl get deploy
$  kubectl get pods

IV)  Verify visitor-app Application is working
$  kubectl get svc
>> Browse a75034d3d45714e7ba6213e60fa15bd9-624944191.us-east-2.elb.amazonaws.com
```

### Option 2: Deploy visitor counter app to EKS with Ingress using AWS ECR (Automate deployment using GitLab CICD)

**Step 1) Build AND Deploy Image to ECR using GitLab CICD**
```
I) Create GitLab Repo
Login to GitLab
Create new Project "cds-visitor-app"

II) Configure GitLab CICD Pipeline
Copy yml file to the repo

III) Build and Push Image to ECR
Goto pipelines to check pipeline status
Goto Jobs
Run Job build-and-push
Check Pipeline logs and verify job run successfully

IV) Verify Container Image Deployed
Logon to AWS
Goto ECR and then select repo "visitorcountapp"
Verify container image updated to the AWS ECR repo
```
***GitLab Pipeline Features:***
1) Static File Scanning:
   
Performs comprehensive scans of static files to detect potential vulnerabilities, misconfigurations, or policy violations early in the development process.

2) Dependency Scanning:
   
Analyzes project dependencies to identify known security vulnerabilities and outdated libraries, ensuring a secure and up-to-date codebase.

3) Secret Scanning:
   
Detects accidental exposure of sensitive information such as API keys, tokens, and credentials within the code repository, helping to prevent security breaches.

4) Container Image Build & Deployment:
   
Builds container images from the application code and securely pushes them to Amazon Elastic Container Registry (AWS ECR), enabling streamlined and automated deployment workflows.


**Step 2) Create EKS Cluster**
```
I) Deploy EKS Cluster
# Pre=requisite:- Login to aws concole, Goto to VPC, Copy the default VPC ID and update in the file _vars.tf_ from the folder EKS-AD (line no. 7)
# Goto the folder IaC-EKS-AD and run below commands:
$  aws configure 
$  terraform init
$  terraform plan
$  terraform apply

II) Connect to EKS cluster
# Goto the folder EKS-Deployments and run below commands to connect to EKS cluster and check resources
aws eks update-kubeconfig --name myekstest-cluster-01
$  kubectl get svc
$  kubectl get nodes
$  kubectl get pods

III) Deploy visitor-app Application 
$  kubectl apply -f visitor-app-redis-deploy-v2.yml
$  kubectl apply -f visitor-app-deploy-v2.yml
$  kubectl get deploy
$  kubectl get pods
```

**Step 3) Configure Ingress for EKS Cluster**
```
I) Configure Ingress to EKS
Prerequisites:
1: enable OIDC for cluster
$  eksctl utils associate-iam-oidc-provider --cluster myekstest-cluster-01 --approve
2: Create IAM Policy for ALB Controller
$  curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
$  aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json
3: Create IAM SVC Acct for Controller
$  eksctl create iamserviceaccount --cluster myekstest-cluster-01 --namespace kube-system --name aws-load-balancer-controller --attach-policy-arn arn:aws:iam::00000000000:policy/AWSLoadBalancerControllerIAMPolicy --approve
4: Install ALB Controller via Helm
$  helm repo add eks https://aws.github.io/eks-charts
$  helm repo update
$  helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=myekstest-cluster-01 --set region=us-east-2 --set vpcId=vpc-079f124622ede5786 --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller

II) Deploy Ingress service
$  kubectl apply -f visitor-app-ingress-v2.yml
$  kubectl get deployment -n kube-system aws-load-balancer-controller
$  kubectl get ingress
$  aws eks describe-cluster --name myekstest-cluster-01 --query "cluster.resourcesVpcConfig.vpcId" --output text
$  kubectl get pods -l app=visitor-app -o wide

IV) Verify visitor-app Application is working
$  kubectl get ingress
>> Browse k8s-default-visitora-cfab75fbe6-1700530975.us-east-2.elb.amazonaws.com
```

***Don't forget to destory resources after test completed***

