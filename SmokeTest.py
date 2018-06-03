import sys
import time
import os
import wasspinner

def testApplication(application,dist):
    print 'Start smoke test application.'
    updatedApplication = wasspinner.Application(application) 
    server = updatedApplication.server()['name']
    node = updatedApplication.server()['nodeName']
    appserver = wasspinner.ApplicationServer(server)
    appserver.stopAppServer(server, node)
    appserver.startAppServer(server, node)
    updatedApplication.start()
    if updatedApplication.isready() != 'true':
        print 'Application is not ready. Starting a backup restore.'
        updatedApplication.update(dist)
    else:
        print 'Application is ready.'
    wasspinner.save()
    os.remove(dist)

backupFolder = sys.argv[0]+'/Backup'
application = sys.argv[1] 

try:
    filename = wasspinner.findDistrName(backupFolder)
    dist = backupFolder+"/"+filename
    print dist
    testApplication(application)
except:
    print 'Backup not found! Check folder!'
    sys.exit()
'''
filename = wasspinner.findDistrName(backupFolder)
dist = backupFolder+"/"+filename
print dist
testApplication(application,dist)
'''