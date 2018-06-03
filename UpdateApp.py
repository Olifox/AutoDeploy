import sys
import time
import os
import wasspinner
import md5
import zipfile


def get_hash_md5(f):
    m = md5.new()
    m.update(f)
    return m.hexdigest()
	
def extract_war_file(zipFile):
    z = zipfile.ZipFile(zipFile, 'r')
    file = z.read('DefaultWebApplication.war')
    z.close()
    return repr (file[:10])
    
def hash_compare(file1, file2):
    f1 = extract_war_file(file1)
    f2 = extract_war_file(file2)
    h1 = get_hash_md5(f1)
    print h1
    h2 = get_hash_md5(f2)
    print h2
    if h1==h2:
        return 1
    else:
        return 0
    

def updateApplication(application,dist,backupFolder):
    print 'Searchable application was found. Starting to update!'
    updatedApplication = wasspinner.Application(application) 
    updatedApplication.stop()
    updatedApplication.export(backupFolder)
    backupDist = getDist(backupFolder)
    if hash_compare(dist,backupDist):
        print 'The application distribution has not been updated. Aborting update.'
        updateApplication.start()
    else:
        try:
            updatedApplication.update(dist)
        except:
            print 'Update %s is failed. Aborting update. Starting a backup restore.'%application
            updatedApplication.install(backupDist)
            os.remove(backupDist)
        wasspinner.save()
    time.sleep(15) 
    os.remove(dist)

def getDist(folder):
    filename = wasspinner.findDistrName(folder)
    distr = folder+"/"+filename
    print distr
    return distr

distrFolder = sys.argv[0] 
application = sys.argv[1] 
backupFolder = sys.argv[0]+'/Backup'
try:
    dist = getDist(distrFolder)
    updateApplication(application,dist,backupFolder)
except:
    print 'There is no distrib files! Check folder!'
    sys.exit()