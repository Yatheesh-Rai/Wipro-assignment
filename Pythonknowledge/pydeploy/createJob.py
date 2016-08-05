#!/usr/bin/env python

'''
require python-jenkins module
'''



import argparse
import os
import traceback
import pylogger
import xml.dom.minidom
import jenkins

#system wide objects
logger = None
JENKINS_TEMPLATE_JOB_NAME='_JENKINS_JOB_TEMPLATE_'
DEFAULT_NOTIFICATION_LIST=['hr_continuous_integration@group.apple.com', 'guest-ci-alerts@group.apple.com']

def get_env_opt():
    '''
    parameters below can get from environmnet variables
        [main variables]
        - JK_GROUP_NAME (String, ex: TAP)
        - JK_REPO_NAME (String, git|svn)
        - JK_ARCHIVE_TYPE (String, lib|exe)
        - JK_DEPLOYABLE_NAME (String, ex: Facade)

        --> ganerate Jenkins Job as "TAP_git_exe_Facade"


        [settings variables]
        - JK_DESCRIPTION (String, ex: "Time Away System Implmentation (Implementation of the new leave system).")
        - JK_REPOSITORY (String, ex: "git@gitlab.corp.apple.com:tap/timeawayfacade.git")
        - JK_BRANCH (String, ex: "facadev1")

        --> refrects Jenkins Job settings
    '''
    opts_dict = {}
    main_variables    = ['JK_GROUP_NAME', 'JK_REPO_NAME', 'JK_ARCHIVE_TYPE', 'JK_DEPLOYABLE_NAME']
    setting_variables = ['JK_REPOSITORY', 'JK_BRANCH']

    #main variables
    for key in main_variables:
        if key in os.environ:
            opts_dict[key] = os.environ[key]
        else:
            logger.warning("can't find variable %s, set blank" % key)
            opts_dict[key] = ""

    #setting variables
    for key in setting_variables:
        if key in os.environ:
            opts_dict[key] = os.environ[key]
        else:
            logger.error("can't find variable %s, set blank" % key)
            opts_dict[key] = ""

    return opts_dict

def _update_scm(doc, scm, opts_dict):
    scm.appendChild(_get_xml_textnode(doc, "configVersion", "2"))

    if opts_dict["JK_REPO_NAME"] == "git":
        scm.setAttribute("class", "hudson.plugins.git.GitSCM")
        scm.setAttribute("plugin", opts_dict["JK_REPO_NAME"])
        userRemoteConfigs = doc.createElement("userRemoteConfigs")
        hudson_plugins_git_userremoteconfig = doc.createElement("hudson.plugins.git.UserRemoteConfig")
        hudson_plugins_git_userremoteconfig.appendChild(_get_xml_textnode(doc, "url", opts_dict["JK_REPOSITORY"]))
        userRemoteConfigs.appendChild(hudson_plugins_git_userremoteconfig)
        scm.appendChild(userRemoteConfigs)

        branches = doc.createElement("branches")
        hudson_plugins_git_BranchSpec = doc.createElement("hudson.plugins.git.BranchSpec")
        hudson_plugins_git_BranchSpec.appendChild(_get_xml_textnode(doc, "name", opts_dict["JK_BRANCH"]))
        branches.appendChild(hudson_plugins_git_BranchSpec)
        scm.appendChild(branches)

    elif opts_dict["JK_REPO_NAME"] == "svn":
        scm.setAttribute("class", "hudson.scm.SubversionSCM")
        scm.setAttribute("plugin", "subversion")

        location = doc.createElement("locations")
        hudson_scm_subversion_scm = doc.createElement("hudson.scm.SubversionSCM_-ModuleLocation")
        hudson_scm_subversion_scm.appendChild(_get_xml_textnode(doc, "remote", opts_dict["JK_REPOSITORY"]))
        hudson_scm_subversion_scm.appendChild(_get_xml_textnode(doc, "local", opts_dict["JK_DEPLOYABLE_NAME"]))
        hudson_scm_subversion_scm.appendChild(_get_xml_textnode(doc, "depthOption", "infinity"))
        hudson_scm_subversion_scm.appendChild(_get_xml_textnode(doc, "ignoreExternalsOption", "false"))
        location.appendChild(hudson_scm_subversion_scm)
        scm.appendChild(location)

        scm.appendChild(doc.createElement("excludedRegions"))
        scm.appendChild(doc.createElement("includedRegions"))
        scm.appendChild(doc.createElement("excludedUsers"))
        scm.appendChild(doc.createElement("excludedRevprop"))
        scm.appendChild(doc.createElement("excludedCommitMessages"))
        workspace_updater = doc.createElement("workspaceUpdater")
        workspace_updater.setAttribute("class", "hudson.scm.subversion.UpdateUpdater")
        scm.appendChild(workspace_updater)
        scm.appendChild(_get_xml_textnode(doc, "ignoreDirPropChanges", "false"))
        scm.appendChild(_get_xml_textnode(doc, "filterChangelog", "false"))


    scm.appendChild(_get_xml_textnode(doc, "doGenerateSubmoduleConfigurations", "false"))
    submoduleCfg = doc.createElement("submoduleCfg")
    submoduleCfg.setAttribute("class", "list")
    scm.appendChild(submoduleCfg)
    scm.appendChild(doc.createElement("extensions"))

    return scm

def _update_notification(doc, mailer, opts_dict):
    notification_list = DEFAULT_NOTIFICATION_LIST
    notification_list.append("ci-notification-%s@group.apple.com" % opts_dict["JK_GROUP_NAME"])

    recipients = mailer.getElementsByTagName("recipients")[0]
    recipients.appendChild(doc.createTextNode(", ".join(notification_list)))

def _get_xml_textnode(doc, elementName, textNode):
    element = doc.createElement(elementName)
    element.appendChild(doc.createTextNode(textNode))

    return element

def get_create_job_xml(opts_dict, jk):
    job_name = _create_jk_job_name(opts_dict)
    logger.info("creating %s" % job_name)

    #copy from template
    jk.copy_job(JENKINS_TEMPLATE_JOB_NAME, job_name)

    #read config.xml as DOM
    job_dom = xml.dom.minidom.parseString(jk.get_job_config(job_name))
    scm = job_dom.getElementsByTagName("scm")[0]

    #update scm
    _update_scm(job_dom, scm, opts_dict)

    #update notification list
    mailer = job_dom.getElementsByTagName("hudson.maven.reporters.MavenMailer")[0]
    _update_notification(job_dom, mailer, opts_dict)

    #generate new config.xml
    config_xml = job_dom.toprettyxml("", "", "UTF-8")
    logger.debug("update config.xml for %s as below\n%s" % (job_name, config_xml))

    #update job
    logger.info("updating %s config.xml" % job_name)
    jk.reconfig_job(job_name, config_xml)


def _create_jk_job_name(opts_dict):
    return "%s_%s_%s_%s" % (opts_dict["JK_GROUP_NAME"], opts_dict["JK_REPO_NAME"],
                         opts_dict["JK_ARCHIVE_TYPE"], opts_dict["JK_DEPLOYABLE_NAME"])

def get_jenkins(jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    logger.info("got jenkins version via API = %s" % jk.get_version())

    return jk

def _get_create_view_xml(view_name, job_name):
    dom = xml.dom.minidom
    doc = dom.Document()

    #top level "project"
    list_view = doc.createElement("hudson.model.ListView")
    doc.appendChild(list_view)

    list_view.appendChild(_get_xml_textnode(doc, "name", view_name))
    list_view.appendChild(_get_xml_textnode(doc, "filterExecutors", "false"))
    list_view.appendChild(_get_xml_textnode(doc, "filterQueue", "false"))
    properties = doc.createElement("properties")
    properties.setAttribute("class", "hudson.model.View$PropertyList")
    list_view.appendChild(properties)

    #jobNames
    job_names = doc.createElement("jobNames")
    comparator = doc.createElement("comparator")
    comparator.setAttribute("class", "hudson.util.CaseInsensitiveComparator")
    job_names.appendChild(comparator)
    job_names.appendChild(_get_xml_textnode(doc, "string", job_name))
    list_view.appendChild(job_names)

    #jobFilters
    list_view.appendChild(doc.createElement("jobFilters"))

    #columns
    columns = doc.createElement("columns")
    columns.appendChild(doc.createElement("hudson.views.StatusColumn"))
    columns.appendChild(doc.createElement("hudson.views.WeatherColumn"))
    columns.appendChild(doc.createElement("hudson.views.JobColumn"))
    columns.appendChild(doc.createElement("hudson.views.LastSuccessColumn"))
    columns.appendChild(doc.createElement("hudson.views.LastFailureColumn"))
    columns.appendChild(doc.createElement("hudson.views.LastDurationColumn"))
    columns.appendChild(doc.createElement("hudson.views.BuildButtonColumn"))
    list_view.appendChild(columns)

    #recurse
    list_view.appendChild(_get_xml_textnode(doc, "recurse", "false"))

    result_xml = doc.toprettyxml("", "", "UTF-8")
    logger.debug("created XML as below\n%s" % result_xml)
    return result_xml

def update_jk_view(jk, view_name, job_name):
    if jk.view_exists(view_name):
        logger.info("add view %s to %s" % (view_name, job_name))
        #add
        view_dom = xml.dom.minidom.parseString(jk.get_view_config(view_name))
        jobs = view_dom.getElementsByTagName("jobNames")[0]
        jobs.appendChild(_get_xml_textnode(view_dom, "string", job_name))
        result_xml = view_dom.toprettyxml("", "", "UTF-8")

        logger.debug("created XML as below\n%s" % result_xml)
        jk.reconfig_view(view_name, result_xml)
    else:
        logger.info("create view : %s" % view_name)
        #create
        create_view_xml = _get_create_view_xml(view_name, job_name)
        jk.create_view(view_name, create_view_xml)

def get_arg_opt():
    parser = argparse.ArgumentParser(description='Submit Maven release build to Jenkins')
    parser.add_argument('--jenkins', dest="jk_url", required=True,
                        help="Jenkins URL (http://localhost:8080/jenkins)")
    parser.add_argument('--user', dest="jk_user", required=True,
                        help="Jenkins username")
    parser.add_argument('--pass', dest="jk_pass", required=True,
                        help="Jenkins password")

    opt = parser.parse_args()

    return opt

#
# main function
#
def main (opt, jk_url, jk_user, jk_pass):
    #get Jenkins object
    jk = get_jenkins(jk_url, jk_user, jk_pass)

    #get create_job XML
    job_xml = get_create_job_xml(env_opt, jk)

    #
    # [disabled due to weired behavior] update Jenkins view(tab)
    #
    #result = update_jk_view(jk, env_opt["JK_GROUP_NAME"], _create_jk_job_name(env_opt))


if __name__ == '__main__':
    try:
        logger = pylogger.set_pylogger_config(__name__, True)

        jk_opt = get_arg_opt()
        env_opt = get_env_opt()

        main(env_opt, jk_opt.jk_url, jk_opt.jk_user, jk_opt.jk_pass)

    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()
        os.exit(1)