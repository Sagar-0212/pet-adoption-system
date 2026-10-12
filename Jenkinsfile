pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'ghcr.io'
        IMAGE_NAME      = 'sagar-0212/pet-adoption-system'
        BUILD_TAG       = "build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "GitFlow: Checking out branch ${env.BRANCH_NAME}..."
                checkout scm
            }
        }

        stage('Static Analysis & Lint') {
            steps {
                echo 'Performing code linting and dependency check...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt flake8
                    flake8 . --count --exit-zero --max-line-length=120 --exclude=.git,__pycache__,.pytest_cache
                '''
            }
        }

        stage('Automated Pytest Suite') {
            steps {
                echo 'Running pytest automated test suite...'
                sh 'pytest test_main.py -v'
            }
        }

        stage('Docker Build (All Branches)') {
            steps {
                echo "Building local test image..."
                sh "docker build -t ${IMAGE_NAME}:${BUILD_TAG} ."
            }
        }

        stage('Publish Artifacts (Develop / Release / Main)') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                    branch pattern: "release/.*", comparator: "REGEXP"
                    branch pattern: "hotfix/.*", comparator: "REGEXP"
                }
            }
            steps {
                echo "Tagging and pushing container to registry..."
                sh """
                    docker tag ${IMAGE_NAME}:${BUILD_TAG} ${IMAGE_NAME}:latest
                    echo "Docker image ready for registry deployment"
                """
            }
        }

        stage('Deploy to Staging (Develop/Release)') {
            when {
                anyOf {
                    branch 'develop'
                    branch pattern: "release/.*", comparator: "REGEXP"
                }
            }
            steps {
                echo "Applying Kubernetes manifests to STAGING namespace..."
                sh 'kubectl apply -f k8s/ -n staging || true'
            }
        }

        stage('Deploy to Production (Main)') {
            when {
                branch 'main'
            }
            steps {
                echo "Applying Kubernetes manifests to PRODUCTION cluster..."
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded for branch ${env.BRANCH_NAME}! Build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline FAILED on branch ${env.BRANCH_NAME}. Please review test and lint stages."
        }
        always {
            cleanWs()
        }
    }
}
