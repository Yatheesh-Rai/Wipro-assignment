#!/usr/bin/python35
import os
import sys
import socket
import re
import traceback
import pexpect
import pylogger
import time
import urllib.request, urllib.error, urllib.parse
from simplecrypt import decrypt
from xml.etree import ElementTree
from optparse import Option, OptionParser

from applicationConstants import appConstants as AC
from deployConstants import ciConstants as CC
from deployConstants import repoConstants as RC
from deployConstants import envAppIDs as EA
from deployConstants import deployAction as DA
from environmentHosts import envHosts as EH

class MultipleOption(Option):
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            values.ensure_value(dest, []).append(value)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

def get_opt_parser():
    '''
    Option Parser to get command ACline args and store them in options_dict
    '''
    parser = OptionParser(option_class=MultipleOption)
    parser.add_option('-d', '--deployable', help='Select deployable for deployment')
    parser.add_option('-a', '--deploy_action', help='Select deploy_package FULL|env_configs or jetty_action Status|Stop|Start|Restart')
    parser.add_option('-b', '--buildtype', help='release | snapshot build of artifact')
    parser.add_option('-v', '--version', help='Select artifact version number')
    parser.add_option('-e', '--env', help='Select deploy environment')
    parser.add_option('-R', '--dry_run', help='Dry run mode')
    parser.add_option('--debug', help='Enable debug log level', action='store_true')

    return parser

opt_parser = get_opt_parser()
(opts, args) = opt_parser.parse_args()
opts_dict = vars(opts)

logger = pylogger.set_pylogger_config(__name__, opts_dict['debug'])


def validateOptions(opts_dict):
    ''' Validate option parameters '''
    logger.info("***** Validating the option parameters *****")
    if not opts_dict['deployable']:
        logger.error('Specify deployable to deploy.')
        raise Exception()

    if not opts_dict['env']:
        logger.error('Specify an environment to deploy.')
        raise Exception()

    if not opts_dict['deploy_action'] or opts_dict['deploy_action'] not in (DA.deployable_packages + DA.jetty_actions):
        logger.info('Selected deploy_action: %s - is not in deployable_packages: %s or not in jetty_actions: %s' %(opts_dict['deploy_action'], DA.deployable_packages, DA.jetty_actions))
        logger.error('Select appropriate deploy_action.')
        raise Exception('Error in deploy_action.')

    if opts_dict['deploy_action'] in (DA.deploy_FULL, DA.deploy_tars):
        if not opts_dict['version']:
            logger.error('Specify acrtifact version for deploy_action "FULL", "tars".')
            raise Exception()
    '''
    if opts_dict['deploy_action'] in (DA.deploy_FULL, DA.deploy_configs, DA.deploy_appConfigs):
        if not opts_dict['appConf_version']:
            logger.error('Provide appConfig_version for deploy_action "FULL", "app_configs" and "configs".')
            raise Exception()
    '''


def initParams():
    '''Initialize the parameters'''
    pdict={}
    logger.info("***** Initializing deployment parameters *****")
    deployableName = opts_dict['deployable']
    deploy_action = opts_dict['deploy_action']
    artifactName = eval("AC.%s['artifactName']" %deployableName)
    artifactType = eval("AC.%s['type']" %deployableName)
    artifactClassifier = eval("AC.%s['classifier']" %deployableName)
    artifactGroupId = eval("AC.%s['groupId']" %deployableName)
    artifactGroupPath = artifactGroupId.replace('.','/')
    artifactBuildRepo = eval("AC.%s['releaseRepo']" %deployableName)
    artifactVersion = opts_dict['version']

    ciSuperPw = decrypt('password',CC.ciSuperCiphercode).decode('ascii')
    appId = eval("EA.%s['applicationId']" %opts_dict['env'])
    sudoCmd = '/usr/bin/sudo su - %s' %appId
    envHosts = eval("EH.%s['%s']" %(deployableName, opts_dict['env']))
    hostList = re.sub(r'\s+', '', envHosts).split(",")

    if opts_dict['dry_run'].lower() == 'true':
        if os.environ.get('WORKSPACE'):
            appRootPath = '%s/dryrun' %os.environ['WORKSPACE']
        else:
            appRootPath = '/tmp/dryrun'
        applicationPath = '{appRoot}/{appName}'.format(appRoot=appRootPath, appName=artifactName)
        configPath = '%s/conf' %applicationPath
    else:
        appGroup = eval("AC.%s['appGroup']" %deployableName)
        appRootPath = '~/softwares/%s/applications' %appGroup
        appPathSpl = eval("AC.%s['appPath']" %deployableName)
        if appPathSpl:
            appRootPath = appPathSpl

        applicationPath = '{appRoot}/{appName}'.format(appRoot=appRootPath, appName=artifactName)
        configPath = '%s/conf' %applicationPath
        confPathSpl = eval("AC.%s['confPath']" %deployableName)
        if confPathSpl:
            configPath = confPathSpl

    cdAppRootCmd = 'if [[ ! -e {appRoot} ]]; then mkdir -p {appRoot}; fi; cd {appRoot}'.format(appRoot=appRootPath)
    backupAppDirCmd = 'cd {appRoot}; if [[ -d {artiDir} ]]; then tar -czpf backup/{artiDir}_backup.tar.gz {artiDir}/*; fi'.format(appRoot=appRootPath, artiDir=artifactName)
    backupConfDirCmd = 'cd {appRoot}; if [[ -d {confDir} ]]; then tar -czpf backup/{appName}_conf_backup.tar.gz {confDir}/*; fi'.format(appRoot=appRootPath, confDir=configPath, appName=artifactName)

    artifactMetaUrl = '{nexusRepo}/resolve?r={buildRepo}&g={groupID}&a={artiName}&v=LATEST&c={classifier}&e={artiType}'.format(nexusRepo=RC.nexusMavenRepo, buildRepo=artifactBuildRepo, groupID=artifactGroupId, artiName=artifactName, classifier=artifactClassifier, artiType=artifactType)
    if not artifactVersion or artifactVersion in ('LATEST', 'latest'):
        artifactVersion = ElementTree.fromstring(urllib.request.urlopen(artifactMetaUrl).read()).findall('data/version')[0].text

    artifactUrl = '{baseUrl}/{buildRepo}/{groupPath}/{artifact}/{version}/{artifact}-{version}-{classifier}.{artiType}'.format(baseUrl=RC.nexusRepo, buildRepo=artifactBuildRepo, groupPath=artifactGroupPath, artifact=artifactName, version=artifactVersion, classifier=artifactClassifier, artiType=artifactType)
    downloadArtifactCmd = 'cd {appRoot}; curl -L {artifacFulltUrl} -o {artifact}.{artiType}'.format(appRoot=appRootPath, artifacFulltUrl=artifactUrl, artifact=artifactName, artiType=artifactType)
    envPropBaseUrl='{url}/raw/master/{appName}'.format(url=RC.gitEnvPropBaseUrl, appName=deployableName)
    envPropFiles = eval("AC.%s['envProperties']" %deployableName)
    envPropFilesList = re.sub(r'\s+', '', envPropFiles).split(",")
    untarCmd = 'cd {appRoot}; if [[ -d {appDir} ]]; then rm -rf {appDir}; fi; mkdir -p {appDir} && tar xf {appDir}.{artiType} -C {appDir} --strip-components=1 && if [[ ! -e backup ]]; then mkdir backup; fi; mv {appDir}.{artiType} backup/'.format(appRoot=appRootPath, appDir=artifactName, artiType=artifactType)
    stopAppCmd = "pid=`ps -eaf |grep %s |grep -v grep | awk '{ printf $2 }'`; if [ ! -z $pid ]; then cd %s; %s/%s; fi" %(artifactName, appRootPath, artifactName, CC.shutdownApp)
    startAppCmd = "pid=`ps -eaf |grep %s |grep -v grep | awk '{ printf $2 }'`; if [ -z $pid ]; then cd %s; %s/%s; fi" %(artifactName, appRootPath, artifactName, CC.startupApp)
    appStatusCmd = 'status=`ps -eaf |grep {appName} |grep -v grep`; if [ ! -z "$status" ]; then echo "### {appName} is UP ### [$status]"; else echo "### {appName} is DOWN ###"; fi'.format(appName=artifactName)

    logPath = '%s/log' %applicationPath
    logFile = eval("AC.%s['appLogFile']" %deployableName)
    if not logFile :
        logFile = '*.log'
    displayLogsCmd = 'cd {appRoot}; if [[ -f {logDir}/{logFile} ]]; then tail -n 10 {logDir}/{logFile} | nl; fi'.format(appRoot=appRootPath, logDir=logPath, logFile=logFile)

    pdict['hostList'] = hostList
    pdict['deployable'] = deployableName
    pdict['deploy_action'] = deploy_action
    pdict['envPropFilesList'] = envPropFilesList
    pdict['envPropBaseUrl'] = envPropBaseUrl
    pdict['appPath'] = applicationPath
    pdict['configPath'] = configPath
    pdict['artifactUrl'] = artifactUrl
    pdict['_1_sudoCmd'] = sudoCmd
    pdict['_2_cdAppRootCmd'] = cdAppRootCmd
    pdict['_3_backupAppDirCmd'] = backupAppDirCmd
    pdict['_4_backupConfDirCmd'] = backupConfDirCmd
    pdict['_5_downloadArtifactCmd'] = downloadArtifactCmd
    pdict['_6_stopAppCmd'] = stopAppCmd
    pdict['_7_untarCmd'] = untarCmd
    pdict['_8_startAppCmd'] = startAppCmd
    pdict['_9_displayLogsCmd'] = displayLogsCmd
    pdict['appStatusCmd'] = appStatusCmd

    logger.debug('deployableName: %s' %deployableName)
    logger.debug('artifactName: %s' %artifactName)
    logger.debug('artifactType: %s' %artifactType)
    logger.debug('artifactClassifier: %s' %artifactClassifier)
    logger.debug('artifactGroupPath: %s' %artifactGroupPath)
    logger.debug('artifactBuildRepo: %s' %artifactBuildRepo)
    logger.debug('artifactVersion: %s' %artifactVersion)
    logger.debug("artifactMetaUrl: %s" %artifactMetaUrl)
    logger.debug("artifactUrl: %s" %artifactUrl)

    for key in sorted(pdict.keys()):
        logger.info("%s: %s" % (key, pdict[key]))

    pdict['ciSuperPw'] = ciSuperPw
    return pdict


def validateParams(params_dict):
    ''' Validate deployment parameters '''
    logger.info("***** Validating deployment parameters *****")
    try:
        r = urllib.request.urlopen(params_dict['artifactUrl'])
        logger.debug('ArtifactUrl access code: %s' % r.getcode())
    except Exception as e:
        logger.error(str('ArtifactUrl HTTP code: %s' % e))
        raise Exception()


def conectHost(hostName, params_dict):
    logger.info('Connecting to host %s' %hostName)
    hostip = socket.gethostbyname(hostName)
    ssh_newkey = 'Are you sure you want to continue connecting (yes/no)?'
    child = pexpect.spawn('ssh %s@%s' %(CC.ciSuperId, hostip), echo=False)
    child.logfile = None
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        logger.error('SSH could not login. SSH message:')
        logger.info(child.before, child.after)
        return None
    if i == 1: # SSH does not have the public key. Accept it to continue connection.
        child.sendline('yes')
        #child.expect('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            logger.error('SSH could not login. SSH message:')
            logger.info(child.before, child.after)
            return None
    child.sendline(params_dict['ciSuperPw'])
    child.expect(".*\$ ")

    child.sendline(params_dict['_1_sudoCmd'])
    child.expect(['.*password.*', appIdPrompt])
    child.sendline(params_dict['ciSuperPw'])
    child.expect(appIdPrompt)
    child.sendline('')
    child.logfile = sys.stdout
    return child


def backupAppDir(child, params_dict):
    global appIdPrompt
    logger.info('***** Backing up application directory *****')
    child.sendline(params_dict['_3_backupAppDirCmd'])
    child.expect (appIdPrompt)
    logger.info('Backing up application directory completed')


def backupConfDir(child, params_dict):
    global appIdPrompt
    logger.info('***** Backing up application/conf directory *****')
    child.sendline(params_dict['_4_backupConfDirCmd'])
    child.expect (appIdPrompt)
    logger.info('Backing up application/conf  directory completed')


def downloadArtifact(child, params_dict):
    global appIdPrompt
    logger.info('***** Downloading the artifact from Nexus repository *****')
    child.sendline(params_dict['_5_downloadArtifactCmd'])
    child.timeout=300
    child.expect('%')
    child.expect(appIdPrompt)
    logger.info('Artifact downloaded')


def unpackArtifact(child, params_dict):
    global appIdPrompt
    logger.info('***** Unpacking the artifact *****')
    child.sendline(params_dict['_7_untarCmd'])
    child.expect(appIdPrompt)
    logger.info('Artifact unpacked')


def generate_downloadEnvPropCmd(envPropFile, params_dict):
    if envPropFile.endswith(tuple(DA.appConfFileTypes_bin)):
        downloadCmd='if [[ ! -e {appPath}/bin ]]; then mkdir -p {appPath}/bin; fi; curl {baseUrl}/{file}?private_token={token} -o {appPath}/bin/{file}'.format(baseUrl=params_dict['envPropBaseUrl'], file=envPropFile, token=RC.ciSuperGitTocken, appPath=params_dict['appPath'])

    elif envPropFile.endswith(tuple(DA.appConfFileTypes_conf)):
        downloadCmd='if [[ ! -e {confPath} ]]; then mkdir -p {confPath}; fi; curl {baseUrl}/{file}?private_token={token} -o {confPath}/{file}'.format(baseUrl=params_dict['envPropBaseUrl'], file=envPropFile, token=RC.ciSuperGitTocken, confPath=params_dict['configPath'])

    else:
        downloadCmd='if [[ ! -e {confPath} ]]; then mkdir -p {confPath}; fi; curl {baseUrl}/{env}/{file}?private_token={token} -o {confPath}/{file}'.format(baseUrl=params_dict['envPropBaseUrl'], env=opts_dict['env'], file=envPropFile, token=RC.ciSuperGitTocken, confPath=params_dict['configPath'])

    return downloadCmd


def downloadEnvProp(child, downloadEnvPropCmd):
    global appIdPrompt
    logger.info('***** downloadEnvPropCmd: %s *****' %downloadEnvPropCmd)
    child.sendline(downloadEnvPropCmd)
    child.expect(appIdPrompt)


def stopApplication(child, params_dict):
    global appIdPrompt
    logger.info('***** Stopping application service: %s *****' %params_dict['deployable'])
    child.sendline(params_dict['_6_stopAppCmd'])
    child.expect('Waiting for .* to shutdown')
    child.expect(appIdPrompt)
    logger.info('%s stopped\n' %params_dict['deployable'])


def startApplication(child, params_dict):
    global appIdPrompt
    logger.info('***** Starting application service: %s *****' %params_dict['deployable'])
    child.sendline(params_dict['_8_startAppCmd'])
    child.expect(appIdPrompt)
    logger.info('%s started' %params_dict['deployable'])


def getApplicationStatus(child, params_dict):
    global appIdPrompt
    logger.info('***** Checking status of %s *****' %params_dict['deployable'])
    child.sendline(params_dict['appStatusCmd'])
    child.readline()


def parseLog(child, params_dict):
    global appIdPrompt
    logger.info('***** Parsing application log files *****')
    statupMessage = '[Ss]tarted'
    child.sendline(params_dict['_9_displayLogsCmd'])
    child.expect(appIdPrompt)


def deploy_code_and_configs(hostName, params_dict):
    child = conectHost(hostName, params_dict)
    backupAppDir(child, params_dict)
    backupConfDir(child, params_dict)
    downloadArtifact(child, params_dict)
    stopApplication(child, params_dict)
    unpackArtifact(child, params_dict)
    for envPropFile in params_dict['envPropFilesList']:
        downloadEnvPropCmd = generate_downloadEnvPropCmd(envPropFile, params_dict)
        downloadEnvProp(child, downloadEnvPropCmd)
    startApplication(child, params_dict)
    getApplicationStatus(child, params_dict)
    parseLog(child, params_dict)
    logger.info('Deployment completed on Host: %s\n' %hostName)
    child.close()


def deploy_envConfigs(hostName, params_dict):
    child = conectHost(hostName, params_dict)
    backupConfDir(child, params_dict)
    stopApplication(child, params_dict)
    for envPropFile in params_dict['envPropFilesList']:
        downloadEnvPropCmd = generate_downloadEnvPropCmd(envPropFile, params_dict)
        downloadEnvProp(child, downloadEnvPropCmd)
    startApplication(child, params_dict)
    getApplicationStatus(child, params_dict)
    parseLog(child, params_dict)
    logger.info('Deployment completed on Host: %s\n' %hostName)
    child.close()


def jetty_action(hostName, params_dict):
    child = conectHost(hostName, params_dict)

    if opts_dict['deploy_action'] == DA.jetty_status:
        getApplicationStatus(child, params_dict)

    elif opts_dict['deploy_action'] == DA.jetty_stopService:
        stopApplication(child, params_dict)

    elif opts_dict['deploy_action'] == DA.jetty_startService:
        startApplication(child, params_dict)
        parseLog(child, params_dict)

    elif opts_dict['deploy_action'] == DA.jetty_restartService:
        stopApplication(child, params_dict)
        startApplication(child, params_dict)
        parseLog(child, params_dict)
    child.close()

def deploy_dryrun(params_dict):
    logger.info('cdAppRootCmd: %s' %params_dict['_2_cdAppRootCmd'])
    os.system(params_dict['_2_cdAppRootCmd'])

    logger.info('downloadArtifactCmd: %s' %params_dict['_5_downloadArtifactCmd'])
    os.system(params_dict['_5_downloadArtifactCmd'])

    logger.info('untarCmd: %s' %params_dict['_7_untarCmd'])
    os.system(params_dict['_7_untarCmd'])

    for envPropFile in params_dict['envPropFilesList']:
        downloadEnvPropCmd = generate_downloadEnvPropCmd(envPropFile, params_dict)
        logger.info('downloadEnvPropCmd: %s' %downloadEnvPropCmd)
        os.system(downloadEnvPropCmd)


appIdPrompt = CC.appIdLoginPrompt


def main ():
    validateOptions(opts_dict)
    params_dictionary = initParams()
    validateParams(params_dictionary)

    if opts_dict['dry_run'].lower() == 'true':
        logger.info('\n\n***** Jenkins dry_run mode: %s *****\n' %opts_dict['dry_run'])
        deploy_dryrun(params_dictionary)

    else :
        for hostName in params_dictionary['hostList']:
            logger.info('\n\n********** Deploy_Action on HOST: %s **********\n' %hostName)

            if opts_dict['deploy_action'] == DA.deploy_FULL:
                deploy_code_and_configs(hostName, params_dictionary)

            elif opts_dict['deploy_action'] == DA.deploy_envConfigs:
                deploy_envConfigs(hostName, params_dictionary)

            elif opts_dict['deploy_action'] in (DA.jetty_actions):
                jetty_action(hostName, params_dictionary)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(("Usage: %s -d deployable -a deploy_action -v version -e environment " % sys.argv[0]))
        logger.info(str(e))
        traceback.print_exc()
        os._exit(1)

