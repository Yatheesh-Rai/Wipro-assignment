class appConstants:
    DefaultApplication = {
    	'componentName':'ApplicationName',
    	'artifactName':'ArtifactName',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'xx-releases',
    	'groupId':'com.apple.ist.xx',
    	'appGroup':'xx_apps',
    	'appPath':'~/softwares/{appGroup}/applications/{artifactName}',
    	'confPath':'~/softwares/{appGroup}/applications/{artifactName}/conf',
    	'envProperties':'{artifactName}.properties',
    	'appLogFile':'{artifactName}.log'
    }
    CMMCompensation = {
    	'componentName':'CMMCompensation',
    	'artifactName':'CMMCompensationService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMCompensation',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMCompensationService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMContainer = {
    	'componentName':'CMMContainer',
    	'artifactName':'CMMContainerService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMContainer',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMContainerService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMHRReports = {
    	'componentName':'CMMHRReports',
    	'artifactName':'CMMHRReportsService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMHRReports',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMHRReportsService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMHumanResources = {
    	'componentName':'CMMHumanResources',
    	'artifactName':'CMMHumanResourcesService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMHumanResources',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMHumanResourcesService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMRecruitment = {
    	'componentName':'CMMRecruitment',
    	'artifactName':'CMMRecruitmentService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMRecruitment',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMRecruitmentService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMRetail = {
    	'componentName':'CMMRetailReports',
    	'artifactName':'CMMRetailReportsService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMRetail',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMRetailReportsService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMRetailReports = {
    	'componentName':'CMMRetailReports',
    	'artifactName':'CMMRetailReportsService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMRetailReports',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMRetailReportsService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMRouting = {
    	'componentName':'CMMRouting',
    	'artifactName':'CMMCompensationService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMRouting',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMRoutingService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    CMMTime = {
    	'componentName':'CMMTime',
    	'artifactName':'CMMTimeService',
    	'type':'tar.gz',
    	'classifier':'distrib-oracle',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.curo.es',
    	'appGroup':'es_apps',
    	'appPath':'~/softwares/es_apps/applications/CMMTime',
    	'confPath':'~/softwares/es_apps/config/es_configs/CMMTimeService/conf',
    	'envProperties':'curo.core.params.env.properties',
        'appLogFile':''
    }
    ESMerlinBenefitsTransactions = {
    	'componentName':'ESMerlinBenefitsTransactions',
    	'artifactName':'es-benefits-transactions-service',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'es-benefits-transaction-service.properties, es-benefits-transaction-app-settings.sh, jetty-es-benefits-transaction-ssl.xml',
        'appLogFile':''
    }
    ESMerlinCompensation = {
    	'componentName':'ESMerlinCompensation',
    	'artifactName':'ESMerlinCompensationService',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'esmerlincompensationservice.properties, esmerlincompensationservice-app-settings.sh, jetty-esmerlincompensationservice-ssl.xml',
        'appLogFile':''
    }
    ESMerlinCompTransactions = {
    	'componentName':'ESMerlinCompTransactions',
    	'artifactName':'es-comp-transactions-service',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'es-comp-transactions-service.properties, es-comp-transactions-service-app-settings.sh, jetty-es-comp-transactions-service-ssl.xml',
        'appLogFile':''
    }
    ESMerlinFacade = {
    	'componentName':'ESMerlinFacade',
    	'artifactName':'es-merlin-facade-service',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'es-merlin-facade.properties, es-merlin-facade-app-settings.sh, jetty-es-merlin-facade-ssl.xml, facade-mapping.properties',
        'appLogFile':''
    }
    ESMerlinHumanResources = {
    	'componentName':'ESMerlinHumanResources',
    	'artifactName':'ESMerlinHumanResourcesService',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'esmerlinhumanresourcesservice.properties, esmerlinhumanresourcesservice-app-settings.sh, jetty-esmerlinhumanresourcesservice-ssl.xml',
        'appLogFile':''
    }
    ESMerlinRecruitment = {
    	'componentName':'ESMerlinRecruitment',
    	'artifactName':'ESMerlinRecruitmentService',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'esmerlinrecruitmentservice.properties, esmerlinrecruitmentservice-app-settings.sh, jetty-esmerlinrecruitmentservice-ssl.xml',
        'appLogFile':''
    }
    ESMerlinPersonTransactions = {
    	'componentName':'ESPersonTransactions',
    	'artifactName':'es-person-service',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'person-service.properties, person-service-app-settings.sh, jetty-person-service-ssl.xml',
        'appLogFile':''
    }
    G2Engine = {
    	'componentName':'G2Engine',
    	'artifactName':'es-g2-engine',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'application.conf, applicationProperties.properties',
    	'appLogFile':'g2-engine.log'
    }
    G2Services = {
    	'componentName':'G2Services',
    	'artifactName':'es-g2-service',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'curo-releases',
    	'groupId':'com.apple.ist.es',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'g2-service.properties',
        'appLogFile':''
    }
    TAP_Services = {
    	'componentName':'TAP_Services',
    	'artifactName':'timeaway',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'tap-releases',
    	'groupId':'com.apple.ist.employeesystems',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'config.properties',
        'appLogFile':''
    }
    TAP_Facade = {
    	'componentName':'TAP_Facade',
    	'artifactName':'timeaway-facade',
    	'type':'tar.gz',
    	'classifier':'distrib',
    	'releaseRepo':'tap-releases',
    	'groupId':'com.apple.ist.employeesystems',
    	'appGroup':'es_apps',
    	'appPath':'',
    	'confPath':'',
    	'envProperties':'config.properties',
        'appLogFile':''
    }

