# IaC_Visitor_Counter-App_Project-Python_EKS_ALB_CICD


**TASKS:**

1.	[Application]
Create an application featuring a webpage displaying the message "This is the <x> visitor," where <x> is a counter fetched from Redis. The counter should increment with each visit to the index page. The application should be dockerize

2.	[CI/CD Pipeline] 
Devise a plan for the automated deployment of the above application to production using GitLab. 

3.	[Cloud infrastructure] 
Deploy an Amazon EKS cluster using Infrastructure as Code (IaC) with Terraform.

4.  [Infra Design]
Provide infrastructure design diagram


## Solution:

**Pre-requisite:**
```
Git 
Docker
Terraform
AWSCLI
eksctl
Download repo in your PC
``

### Option 1: Deploy visitor counter app to EKS using Docker Hub`

**Step 1) Build Image manually**

```
docker build -t visitorcountapp .
docker tag visitorcountapp ardher/visitorcountapp:latest
docker login
docker push ardher/visitorcountapp:latest
```

**Step 2) Create EKS Cluster**
```
Terraform init
Terraform plan
Terraform apply

aws eks update-kubeconfig --name myekstest-cluster-01
kubectl get svc
kubectl get nodes
kubectl get pods
kubectl apply -f visitor-app-deploy.yml
kubectl apply -f visitor-app-redis-deploy.yml
kubectl get deploy
kubectl get svc
>> Browse a75034d3d45714e7ba6213e60fa15bd9-624944191.us-east-2.elb.amazonaws.com
```

### Option 2: Deploy visitor counter app to EKS using AWS ECR
**Step 1) Build Image using GitLab CICD**
```
Login to GitLab
Create new Project
Copy yml file to the repo
Goto pipelines to check pipeline status
Goto Jobs
Run Job build-and-push
Verify container image updated to AWS ECR repo
```

**Step 2) Create EKS Cluster**
```
Terraform init
Terraform plan
Terraform apply

aws eks update-kubeconfig --name myekstest-cluster-01
kubectl get svc
kubectl get nodes
kubectl get pods

kubectl apply -f visitor-app-redis-deploy-v2.yml
kubectl apply -f visitor-app-deploy-v2.yml
kubectl get deploy
kubectl get pods
kubectl get svc
>> Browse a75034d3d45714e7ba6213e60fa15bd9-624944191.us-east-2.elb.amazonaws.com
```

**Step 3) Configure Ingress for EKS Cluster**
```
 1: Prerequisites- enabled OIDC for cluster
eksctl utils associate-iam-oidc-provider --cluster myekstest-cluster-01 --approve

2: Create IAM Policy for ALB Controller
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json

3: Create IAM SVC Acct for Controller
eksctl create iamserviceaccount --cluster myekstest-cluster-01 --namespace kube-system --name aws-load-balancer-controller --attach-policy-arn arn:aws:iam::00000000000:policy/AWSLoadBalancerControllerIAMPolicy --approve

4: Install ALB Controller via Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=myekstest-cluster-01 --set region=us-east-2 --set vpcId=vpc-079f124622ede5786 --set serviceAccount.create=false --set serviceAccount.name=aws-load-balancer-controller

5: Verify Installation
kubectl get deployment -n kube-system aws-load-balancer-controller
kubectl get ingress
aws eks describe-cluster --name myekstest-cluster-01 --query "cluster.resourcesVpcConfig.vpcId" --output text
kubectl get pods -l app=visitor-app -o wide
kubectl get ingress
>> Browse k8s-default-visitora-cfab75fbe6-1700530975.us-east-2.elb.amazonaws.com
```



