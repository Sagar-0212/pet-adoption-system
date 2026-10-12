pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        AWS_ACCOUNT_ID     = credentials('AWS_ACCOUNT_ID')
        AWS_CREDENTIALS_ID = 'aws-credentials'
        ECR_REPOSITORY     = 'pet-adoption-system'
        EKS_CLUSTER_NAME   = 'pet-adoption-eks'
        IMAGE_NAME         = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPOSITORY}"
        // Immutable image tag strategy: git commit short SHA + build number
        IMAGE_TAG          = "${env.GIT_COMMIT ? env.GIT_COMMIT.take(8) : 'sha'}-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "GitFlow: Checking out branch ${env.BRANCH_NAME}..."
                checkout scm
            }
        }

        stage('Static Analysis & Quality Gate') {
            steps {
                echo 'Running flake8 static code analysis and PEP8 validation...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt flake8
                    flake8 . --count --max-line-length=120 --exclude=.git,__pycache__,.pytest_cache
                '''
            }
        }

        stage('Automated Pytest Suite') {
            steps {
                echo 'Executing pytest automated test suite...'
                sh 'pytest test_main.py -v'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building container image with immutable tag: ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Container Security Scan (Trivy)') {
            steps {
                echo "Scanning Docker image for vulnerabilities..."
                sh """
                    if command -v trivy >/dev/null 2>&1; then
                        trivy image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
                    else
                        echo "Trivy not installed on Jenkins agent; skipping local CVE scan"
                    fi
                """
            }
        }

        stage('Push to Amazon ECR') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                    branch pattern: "release/.*", comparator: "REGEXP"
                    branch pattern: "hotfix/.*", comparator: "REGEXP"
                }
            }
            steps {
                echo 'Authenticating with Amazon ECR and pushing image...'
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: "${AWS_CREDENTIALS_ID}"
                ]]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                        aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_DEFAULT_REGION} || aws ecr create-repository --repository-name ${ECR_REPOSITORY} --image-tag-mutability IMMUTABLE --region ${AWS_DEFAULT_REGION}
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Deploy to Staging (EKS)') {
            when {
                anyOf {
                    branch 'develop'
                    branch pattern: "release/.*", comparator: "REGEXP"
                }
            }
            steps {
                echo "GitFlow: Automated deployment to Staging namespace in AWS EKS..."
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: "${AWS_CREDENTIALS_ID}"
                ]]) {
                    sh """
                        aws eks update-kubeconfig --region ${AWS_DEFAULT_REGION} --name ${EKS_CLUSTER_NAME}
                        kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
                        sed -i 's|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/deployment.yaml
                        kubectl apply -f k8s/ -n staging
                        kubectl rollout status deployment/pet-api -n staging --timeout=180s
                    """
                }
            }
        }

        stage('Manual Approval for Production') {
            when {
                branch 'main'
            }
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input message: "Approve deployment to AWS EKS Production with image tag ${IMAGE_TAG}?",
                          ok: "Deploy to Production",
                          submitterParameter: 'APPROVER'
                }
            }
        }

        stage('Deploy to Production (EKS)') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying verified image ${IMAGE_TAG} to Production..."
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: "${AWS_CREDENTIALS_ID}"
                ]]) {
                    sh """
                        aws eks update-kubeconfig --region ${AWS_DEFAULT_REGION} --name ${EKS_CLUSTER_NAME}
                        sed -i 's|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/deployment.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl rollout status deployment/pet-api --timeout=180s
                        echo "Production rollout successfully completed!"
                        kubectl get service pet-service
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded for branch ${env.BRANCH_NAME}! Build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline FAILED on branch ${env.BRANCH_NAME}. Please review test and deployment stages."
        }
        always {
            cleanWs()
        }
    }
}
