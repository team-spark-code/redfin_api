pipeline {
    agent any
    environment {
        IMAGE = 'docker.io/sungminwoo0612/redfin-api'
        GIT_SHA = sh(script: 'git rev-parse --short HEAD || echo local', returnStdout: true).trim()
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
            steps {
                sh ```
                    docker run --rm -v "$$PWD":/w -w /w python:3.11-slim bash -l -c "
                        set -euo pipefail
                        if [ -f "requirements.txt" ]; then
                            pip install -U pip && pip install -r requirements.txt
                        else
                            pip install -U pip && pip install fastapi uvicorn pytest httpx pydantic
                        fi
                        pytest -q
                    "
                ```
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build -t ${IMAGE}:latest -t ${IMAGE}:${GIT_SHA} .
                '''
            }
        }

        stage('Push to Docker Hub') {
            withCredentials([
                usernamePassword(credentialsId: 'dockerhub-sungminwoo0612', 
                usernameVariable: 'DH_USER', 
                passwordVariable: 'DH_PASS')
            ]) {
                sh '''
                    echo '$DH_PASS' | docker login -u $DH_USER --password-stdin
                    docker push ${IMAGE}:${GIT_SHA}
                    docker push ${IMAGE}:latest
                '''
            }
        }
        post {
            always { sh 'docker image prune -f || true' }
        }
    }
}
