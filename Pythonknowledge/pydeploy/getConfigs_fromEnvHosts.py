#!/usr/bin/python35
import os
import sys
import socket
import re
import traceback
import pexpect
import pylogger
import urllib.request, urllib.error, urllib.parse
from simplecrypt import decrypt
from xml.etree import ElementTree
from optparse import Option, OptionParser

from applicationConstants import appConstants as AC
from deployConstants import ciConstants as CC
from deployConstants import envAppIDs as EA
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
    parser.add_option('-d', '--deployable', help='Select deployable component to get configs')
    parser.add_option('-p', '--path', help='Select target path to copy configs')
    parser.add_option('-e', '--env', help='Select source environment to get configs')
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
        logger.error('Specify deployable component to get configs.')
        raise Exception()

    if not opts_dict['path']:
        logger.error('Specify target path to copy configs.')
        raise Exception()

    if not opts_dict['env']:
        logger.error('Specify source environment to get configs.')
        raise Exception()


def initParams():
    '''Initialize the parameters'''
    pdict={}
    logger.info("***** Initializing deployment parameters *****")
    deployableName = opts_dict['deployable']
    artifactName = eval("AC.%s['artifactName']" %deployableName)
    ciSuperPw = decrypt('password',CC.ciSuperCiphercode).decode('ascii')
    appId = eval("EA.%s['applicationId']" %opts_dict['env'])
    sudoCmd = '/usr/bin/sudo su - %s' %appId
    envHosts = eval("EH.%s['%s']" %(deployableName, opts_dict['env']))
    hostList = re.sub(r'\s+', '', envHosts).split(",")

    appGroup = eval("AC.%s['appGroup']" %deployableName)
    appRootPath = '~/softwares/%s/applications' %appGroup
    appPathSpl = eval("AC.%s['appPath']" %deployableName)
    if appPathSpl :
        appRootPath = appPathSpl

    cdAppRootCmd = 'if [[ ! -e {appRoot} ]]; then mkdir -p {appRoot}; fi; cd {appRoot}'.format(appRoot=appRootPath)
    applicationPath = '{appRoot}/{appName}'.format(appRoot=appRootPath, appName=artifactName)

    configPath = '%s/conf' %applicationPath
    confPathSpl = eval("AC.%s['confPath']" %deployableName)
    if confPathSpl :
        configPath = confPathSpl

    envPropFiles = eval("AC.%s['envProperties']" %deployableName)
    envPropFilesList = re.sub(r'\s+', '', envPropFiles).split(",")

    pdict['deployable'] = opts_dict['deployable']
    pdict['destBasePath'] = opts_dict['path']
    pdict['env'] = opts_dict['env']
    pdict['hostList'] = hostList
    pdict['envPropFilesList'] = envPropFilesList
    pdict['applicationPath'] = applicationPath
    pdict['configPath'] = configPath
    pdict['_1_sudoCmd'] = sudoCmd

    logger.debug('deployableName: %s' %deployableName)
    logger.debug('artifactName: %s' %artifactName)

    for key in sorted(pdict.keys()):
        logger.info("%s: %s" % (key, pdict[key]))

    pdict['ciSuperPw'] = ciSuperPw
    return pdict


def conectHost(sourceHost, params_dict):
    logger.info('\n\n********** Connecting to HOST: %s **********\n' %sourceHost)
    hostip = socket.gethostbyname(sourceHost)
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
    child.logfile = sys.stdout
    return child

def copy_envConfigs(sourceHost, child, params_dict):
    global appIdPrompt
    destPath='{destBasePath}/configs/{appName}/{env}'.format(destBasePath=params_dict['destBasePath'], appName=params_dict['deployable'], env=params_dict['env'])
    if not os.path.exists(destPath):
        logger.info('Creating path: %s' %destPath)
        os.makedirs(destPath, exist_ok=True)
        os.system('chmod 755 -R %s' %params_dict['destBasePath'])
        os.chmod(destPath, 0o777)

    logger.info('Copying envPropFile(s)...')

    for envPropFile in params_dict['envPropFilesList']:
        if envPropFile.endswith('.sh'):
            copyEnvPropCmd = 'scp {appPath}/bin/{file} {id}@{destHost}:{destPath}/{file}_{sourceHost}'.format(appPath=params_dict['applicationPath'], file=envPropFile, id=CC.ciSuperId, destHost=destHost, destPath=destPath, sourceHost=sourceHost)
        else :
            copyEnvPropCmd = 'scp {confPath}/{file} {id}@{destHost}:{destPath}/{file}_{sourceHost}'.format(confPath=params_dict['configPath'], file=envPropFile, id=CC.ciSuperId, destHost=destHost, destPath=destPath, sourceHost=sourceHost)
        logger.debug('copyEnvPropCmd: %s' %copyEnvPropCmd)
        child.logfile = sys.stdout
        child.sendline(copyEnvPropCmd)
        child.logfile = None
        ssh_newkey = 'Are you sure you want to continue connecting (yes/no)?'
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
        if i == 0: # Timeout
            logger.error('SSH could not login. SSH message:')
            logger.info(child.before, child.after)
            return None
        if i == 1: # SSH does not have the public key. Accept it to continue connection.
            child.sendline('yes')
            i = child.expect([pexpect.TIMEOUT, 'password: '])
            if i == 0: # Timeout
                logger.error('SSH could not login. SSH message:')
                logger.info(child.before, child.after)
                return None
        child.sendline(params_dict['ciSuperPw'])
        child.logfile = sys.stdout
        child.expect(appIdPrompt)
    chmodCmd = 'ssh {id}@{destHost} "chmod 755 {destPath}/*"'.format(id=CC.ciSuperId, destHost=destHost, destPath=destPath)
    child.sendline(chmodCmd)
    child.expect('password: ')
    child.logfile = None
    child.sendline(params_dict['ciSuperPw'])
    child.expect(appIdPrompt)


appIdPrompt = '.*\> '
destHost=CC.jmaster

def main ():
    validateOptions(opts_dict)
    params_dictionary = initParams()
    
    for sourceHost in params_dictionary['hostList']:
        child = conectHost(sourceHost, params_dictionary)
        copy_envConfigs(sourceHost, child, params_dictionary)
        child.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(("Usage: %s -c deployableName -d targetPath -e environment " % sys.argv[0]))
        logger.info(str(e))
        traceback.print_exc()
        os._exit(1)

