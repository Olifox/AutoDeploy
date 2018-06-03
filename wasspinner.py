global AdminNodeManagement
import sys
import time
import os
import AdminNodeManagement

def _splitlines(s):
    rv = [s]
    if '\r' in s:
        rv = s.split('\r\n')
    elif '\n' in s:
        rv = s.split('\n')
    if rv[-1] == '':
        rv = rv[:-1]
    return rv

'''
def getAdminAppViewValue(name, keyname, parsename):
    verboseString = AdminApp.view(name, keyname)
    verboseStringList = _splitlines(verboseString)
    resultList = []
    for str in verboseStringList:
        if str.startswith(parsename):
            resultString = str[len(parsename):].strip()
            resultList.append(resultString)
    return resultList

    print "Exit. Did not find value from application parameters. Returning None."
    return None
'''

class ApplicationServer:
    def __init__(self, name):
        self.name = name
        self.object = AdminControl.completeObjectName('WebSphere:type=Server,name=' + self.name + ',*')
        self.id = AdminConfig.getid('/Server:' + self.name)

    def startAppServer(self, name, nodename):
        try:
            state = AdminControl.getAttribute(self.object,"state")
            print "%s already started!"%name
        except:
            print "Starting %s initiated."%name
            AdminControl.startServer( name, nodename, 120)

    def stopAppServer(self, name, nodename):
        try:
            state = AdminControl.getAttribute(self.object,"state")
            AdminControl.stopServer( name, nodename, 120)
        except:
            print "%s is already stopped."%name


class Application:
    def __init__(self, name):
        self.name = name
        self.cell = AdminControl.getCell()
        self.servers = []
        self.MapResRefToEJBDict = {}
        self._getmodules(name)
        '''
        self.contextRoot = getAdminAppViewValue(name,'-CtxRootForWebMod', 'Context Root:')
        try:
            self.resourceRef = getAdminAppViewValue(name,'-MapResRefToEJB', 'Resource Reference:')
            self.mappingString = '-MapResRefToEJB ['
            for ref in resourceRef:
                self.targetJNDI = getAdminAppViewValue(name,'-MapResRefToEJB', 'Target Resource JNDI Name:')
                self.uri = getAdminAppViewValue(name,'-MapResRefToEJB', 'URI:')
                self.module = getAdminAppViewValue(name,'-MapResRefToEJB', 'Module:')
                self.resType = getAdminAppViewValue(name,'-MapResRefToEJB', 'Resource type:')
                self.MapResRefToEJBDict[ref] = [targetJNDI, uri, module, resType]
                mapping = '[ ' + module + ' "" ' + uri + ' ' + resourceReference + ' ' + ResourceType + ' ' + targetJNDI + ' "" "" "" ]'
                mappingString = mappingString + mapping
        except:
            self.mappingString = ""
        '''

    def server(self):
        return self.servers[0]

    def _getmodules(self, name):
        modsline = AdminApp.listModules(name, '-server')
        modswithoutname = modsline[modsline.find(':') + 1:]
        mods = modswithoutname.split(':')
        #for mod in mods:
        modparams = {}
        #curmod = mod.split(',')
        curmod = mods[1].split(',')
        for cur in curmod:
            par, value = cur.split('=')
            modparams[par] = value
        serverparams = {}
        servername = modparams['server']
        serverappmanager = AdminControl.completeObjectName(
            'type=ApplicationManager,process=' + servername + ',*')
        serverobject = AdminControl.completeObjectName('WebSphere:type=Server,name=' + servername + ',*')
        servernodename = modparams['node']
        servernodeobject = AdminControl.completeObjectName(
            'WebSphere:type=NodeAgent,name=' + servernodename)
        serverparams['name'] = servername
        serverparams['object'] = serverobject
        serverparams['applicationManager'] = serverappmanager
        serverparams['nodeName'] = servernodename
        serverparams['nodeObject'] = servernodeobject
        self.servers.append(serverparams)

    def status(self):
        appmbean = AdminControl.queryNames('type=Application,name=' + self.name + ',*')
        if len(appmbean) != 0:
            return "started"
        return "stopped"

    def isready(self):
        return AdminApp.isAppReady(self.name)

    def stop(self):
        if self.status() != "started":
            print "App " + self.name + " already stopped"
        else:
            AdminControl.invoke(self.servers[0]['applicationManager'], 'stopApplication', self.name)
            while self.status() != "stopped":
                time.sleep(5)
            print "App " + self.name + " is stopped"

    def start(self):
        if self.status() != "stopped":
            print "App " + self.name + " already started"
        else:
            AdminControl.invoke(self.servers[0]['applicationManager'], 'startApplication', self.name)
            while AdminApp.isAppReady(self.name) != "true" and self.status() != "started":
                time.sleep(5)
            print "App " + self.name + " is started"

    def restart(self):
        self.stop()
        while self.isready() != "true":
            print "Waiting till app " + self.name + " stops"
            time.sleep(5)
        self.start()
        while self.isready() != "false":
            print "Waiting till app " + self.name + " starts"
            time.sleep(5)

    def update(self, distrpath):
        AdminApp.uninstall(self.name)
        for server in self.servers:
                opts = "[" + \
                       "-node " + server['nodeName'] + " " + \
                       "-cell " + self.cell + " " + \
                       "-server " + server['name'] + " " + \
                       "-appname " + self.name + " " + \
                       "]"
                AdminApp.install(distrpath, opts)

    def uninstall(self):
        AdminApp.uninstall(self.name)

    def export(self, exportpath):
        try:
            AdminApp.export(self.name,exportpath+'/'+self.name+'.ear','[-exportToLocal]')
            print self.name+" export to "+exportpath
        except:
            print "Export %s is failed."%self.name

    def install(self, distrpath):
        for server in self.servers:
                opts = "[" + \
                       "-node " + server['nodeName'] + " " + \
                       "-cell " + self.cell + " " + \
                       "-server " + server['name'] + " " + \
                       "-appname " + self.name + " " + \
                       "]"
                AdminApp.install(distrpath, opts)


def save():
    AdminConfig.save()


def findDistrName(distrFolder):
    folderElementsList = os.listdir(distrFolder)
    for elem in folderElementsList:
        filename, file_ext = os.path.splitext(elem)
        if file_ext == '.ear':
            filename = filename+file_ext
            print filename
            return filename