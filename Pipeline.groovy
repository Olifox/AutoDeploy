#!/usr/bin/env groovy

def copySource(){
    result = sh (
        script:"ansible-playbook CopyFile.yml -i ${ansiblehome}hosts -v --extra-vars \"win_path=${winpath} workspace_path=${env.WORKSPACE}\"" , 
        returnStdout:true)
    echo (result)
}

def startUpdate(){
    result = sh (
        script:"ansible-playbook updateApp.yml -i ${ansiblehome}hosts -v --vault-password-file ${masterPassword} --extra-vars \"win_path=${winpath} workspace_path=${env.WORKSPACE} appname=${appname}\"" , 
        returnStdout:true)
    print result
    reg = /(.*)Aborting update.(.*)/
    if (result =~ reg)
        error("Update ${appname} is aborted. Stoppage job.")
}

def smokeTest(){
    result = sh (
        script:"ansible-playbook SmokeTest.yml -i ${ansiblehome}hosts -v --vault-password-file ${masterPassword} --extra-vars \"win_path=${winpath} workspace_path=${env.WORKSPACE} appname=${appname}\"" , 
        returnStdout:true)
    echo (result)
}

return this