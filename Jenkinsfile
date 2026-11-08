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
                echo "===> Mengambil kode sumber dari branch main..."
                checkout scm
            }
        }

        stage('2. Syntax Check') {
            steps {
                echo "===> Memverifikasi sintaks Python..."
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
                echo "===> Menjalankan deployment kontainer backend..."
                sh '''
                    docker stop guestbook-backend || true
                    docker rm guestbook-backend || true
                    docker run -d \
                        --name guestbook-backend \
                        --network appnet \
                        --network-alias backend \
                        --restart unless-stopped \
                        -e DATA_DIR=/data \
                        -v guestbook-db-data:/data \
                        guestbook-backend:latest
                '''
            }
        }

        stage('5. Health Check') {
            steps {
                echo "===> Memverifikasi kesehatan aplikasi..."
                sleep 5
                sh '''
                    docker exec guestbook-backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/health').read().decode())"
                '''
                echo "===> Deployment SUKSES! Sistem Sehat dan Aktif!"
            }
        }
    }

    post {
        success {
            echo "Pipeline Berhasil! Image aktif dengan tag :${BUILD_NUMBER} dan :${GIT_COMMIT_SHORT}"
        }
        failure {
            echo "Pipeline Gagal! Periksa riwayat log di Console Output."
        }
    }
}