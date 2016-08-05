class ciConstants:
    ciSuperId='c1219267'
    ciSuperCiphercode=b'sc\x00\x02\xb4\xdc%3`\x80@Sh\x82\xa0\x0e\x9e\x1c>\xa2\x98W\x9b\xd5\x8c\xa4a"\xfa\x0b\x904"\x0f\x85\x99\xf2<\x83U\xf3\xde\xd1\xea\xe2\x8f\xfd\x1aU\xdbH\xd8\xed\xa3\r7\xecM\xff\xda\xa7\xde8?\xcc\xaf\xff\x0f\xd7\xf2\x97\xf0+\x10\xc6\xa8\xb2\xb7'
    appIdLoginPrompt = '.*\> '
    shutdownApp='bin/shutdown.sh'
    startupApp='bin/startup.sh'
    jmaster='rn2-empsysd-lapp145.rno.apple.com'

class envAppIDs:
    LT = {
    	'applicationId':'empsysd'
    }
    IT1=IT2=FT1=FT2=MT=TR = {
    	'applicationId':'empsyst'
    }
    old_IT1=old_IT2 = {
    	'applicationId':'curot'
    }

class repoConstants:
    svnRepoRoot="https://istsvn.corp.apple.com:1080/SVNROOT"
    gitEnvPropBaseUrl = 'https://gitlab.corp.apple.com/citeam/EnvironmentProperties_nonprod'
    ciSuperGitTocken='xyUtG5qboFMTRyXyzKVS'
    nexusRepo="http://nexusrepo.corp.apple.com/content/repositories"
    nexusMavenRepo="http://nexusrepo.corp.apple.com/service/local/artifact/maven"
    curoReleaseRepo="http://nexusrepo.corp.apple.com/content/repositories/curo-releases"

class deployAction:
    deploy_FULL = 'deploy_FULL'
    deploy_tars = 'deploy_tars'
    deploy_configs = 'deploy_configs'
    deploy_appConfigs = 'deploy_appConfigs'
    deploy_envConfigs = 'deploy_envConfigs'
    jetty_status = 'jetty_status'
    jetty_stopService = 'stop_jetty'
    jetty_startService = 'start_jetty'
    jetty_restartService = 'restart_jetty'    
    deployable_packages = ['deploy_FULL', 'deploy_tars', 'deploy_configs', 'deploy_appConfigs', 'deploy_envConfigs']
    jetty_actions = ['jetty_status', 'stop_jetty', 'start_jetty', 'restart_jetty']
    appConfFileTypes_bin = ['-app-settings.sh']    
    appConfFileTypes_conf = ['-ssl.xml']


