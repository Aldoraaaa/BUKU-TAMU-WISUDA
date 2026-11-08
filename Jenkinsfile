pipeline {
    agent any

    environment {
        APP_NAME         = "guestbook-backend"
        DOCKER_IMAGE     = "guestbook-backend"
        GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo "===> Mengambil kode dari GitHub branch main..."
                checkout scm
            }
        }

        stage('2. Syntax Check') {
            steps {
                echo "===> Memverifikasi sintaks kode Python..."
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('3. Build Docker Image') {
            steps {
                echo "===> Membangun Docker Image dengan Dual Tag..."
                sh """
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('4. Automated Deployment') {
            steps {
                echo "===> Menjalankan stack via Docker Compose..."
                sh """
                    docker compose down || true
                    docker compose up -d --build
                """
            }
        }

        stage('5. Health Check') {
            steps {
                echo "===> Memvalidasi kesehatan backend & frontend..."
                sleep 5
                sh """
                    docker exec guestbook-backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/health').read().decode())"
                    curl -fsS http://localhost:8081/health > /dev/null
                    curl -fsS http://localhost:8081/api/messages > /dev/null
                """
                echo "===> Sistem LIVE dan Sehat pada Port 8081!"
            }
        }
    }

    post {
        success {
            echo "Pipeline CI/CD Berhasil! Aplikasi aktif dengan tag :${BUILD_NUMBER} dan :${GIT_COMMIT_SHORT}"
        }
        failure {
            echo "Pipeline Gagal! Periksa log Jenkins di console output."
        }
    }
}