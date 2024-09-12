pipeline {
    agent { label 'docker-fabric' }
    options {
        timeout(time: 1, unit: 'HOURS')
    }
    stages {
        stage ('Test backend-json') {
            steps {
                ansiColor('xterm') {
                    sh 'echo hi'
                }
            }
        }
    }
    post {
        always {
            step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: "mhershberger@connectify.me", sendToIndividuals: true])
        }
    }
}
