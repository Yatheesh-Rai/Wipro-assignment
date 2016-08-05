#!/usr/bin/env python

import urllib
import httplib
import os
import traceback
import pylogger
import argparse
import jenkins
import re
import mechanize

from urlparse import urlparse
from mechanize import ParseResponse, urlopen, urljoin
from base64 import b64encode

'''
require mechanize package (pip install mechanize)
'''

logger = None

def get_m2release_param(m2release_form):
    #main params
    params = {}
    params["releaseVersion"] = m2release_form["releaseVersion"]
    params["developmentVersion"] = m2release_form["developmentVersion"]
    params["scmUsername"] = m2release_form["scmUsername"]
    params["scmPassword"] = m2release_form["scmPassword"]
    params["scmCommentPrefix"] = m2release_form["scmCommentPrefix"]
    params["scmTag"] = m2release_form["scmTag"]
    params["Submit"] = m2release_form["Submit"]
    if m2release_form["specifyScmTag"]:
        params["specifyScmTag"] = "on"
    else:
        params["specifyScmTag"] = ""

    #json params
    my_json = {}
    my_json["releaseVersion"] = m2release_form["releaseVersion"]
    my_json["developmentVersion"] = m2release_form["developmentVersion"]
    if m2release_form["isDryRun"]:
        my_json["isDryRun"] = True
    else:
        my_json["isDryRun"] = False

    if m2release_form["specifyScmTag"]:
        my_json["specifyScmTag"] = {"scmTag" : m2release_form["scmTag"]}
    params["json"] = my_json

    return urllib.urlencode(params)

def _is_jenkins_https(jk_url):
    url = urlparse(jk_url)

    if url.scheme == "https":
        logger.info("Jenkins is https")
        return True
    else:
        logger.info("Jenkins is http")
        return False

def _get_jenkins_host(jk_url):
    url = urlparse(jk_url)

    logger.info("hostname is %s" % url.hostname)
    return url.hostname

def _get_jenkins_port(jk_url):
    url = urlparse(jk_url)

    if url.port:
        logger.info("port is %s" % url.port)
        return url.port
    else:
        logger.info("port is 80")
        return 80

def _get_jenkins_path(jk_url):
    url = urlparse(jk_url)

    if url.path:
        logger.info("path is %s" % url.path)
        return url.path
    else:
        logger.info("path is root(/)")
        return ""

def get_m2release_form(jk_url, prj_name):
    full_url = "%s/job/%s/m2release/" % (jk_url, prj_name)

    #load "Perform Maven Release" page
    logger.info("retrieve maven release info from %s" % full_url)

    try:
        response = urlopen(full_url)
        forms = ParseResponse(response, backwards_compat=False)

        return forms[1] #form[0] is search box
    except Exception as e:
        #probably doesn't configure Maven Release Build plugin
        logger.error(str(e) + " : " + full_url)
        return None

def submit_request(jk_url, prj_name, jk_user, jk_pass, params):
    full_path = "%s/job/%s/m2release/submit" % (_get_jenkins_path(jk_url), prj_name)
    userAndPass = b64encode(b"%s:%s" % (jk_user, jk_pass)).decode("ascii")
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "Authorization" : "Basic %s" % userAndPass
               }
    if _is_jenkins_https(jk_url):
        conn = httplib.HTTPSConnection(_get_jenkins_host(jk_url), _get_jenkins_port(jk_url))
    else:
        conn = httplib.HTTPConnection(_get_jenkins_host(jk_url), _get_jenkins_port(jk_url))

    logger.info("submit release build to %s" % full_path)
    conn.request("POST", full_path, params, headers)

    return conn.getresponse()

def _get_last_release_build(job, jk_url, jk_user, jk_pass):
    regex = r'^.+\s#(\d+) \[.*$' # 'ESMerlinAdmin_git_exe_Recruitment #12 [Jenkins]'

    full_url = "%s/job/%s/lastRelease/" % (jk_url, job)

    #load "lastRelease" page
    logger.info("retrieve last release info from %s" % full_url)

    br = mechanize.Browser()
    try:
        br.open(full_url)
    except Exception as e:
        logger.warning("%s never have release build" % job)
        return 0

    #get title
    title = br.title()
    m = re.match(regex, title)
    if not m:
        logger.error("couldn't get build number, abort : %s" % title)
        return 0
    else:
        last_release = int(m.group(1))
        logger.info("%s latest release build is %d" % (job, last_release))
        return last_release


def is_lastBuild_Successful(job, jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    last_build_num = 0
    last_successful_build_num = 0

    # get lastBuild number#
    job_info = jk.get_job_info(job)
    if job_info["lastBuild"]:
        last_build_num = job_info["lastBuild"]["number"]
    else:
        logger.warning("%s never have any build, skip" % job)
        return False

    # get lastSuccessfulBuild number#
    job_info = jk.get_job_info(job)
    if job_info["lastSuccessfulBuild"]:
        last_successful_build_num = job_info["lastSuccessfulBuild"]["number"]
    else:
        logger.warning("%s never have any successful build, skip" % job)
        return False

    if last_build_num > last_successful_build_num:
        logger.info("%s last build is not successful, skip" % job)
        return False

    return True


def check_lastSuccessfulBuild(job, jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    last_successful_build_num = 0
    last_release_build_num = 0

    # get lastSuccessfulBuild build#
    job_info = jk.get_job_info(job)
    if job_info["lastSuccessfulBuild"]:
        last_successful_build_num = job_info["lastSuccessfulBuild"]["number"]
    else:
        logger.warning("%s never have any successful build, skip" % job)
        return False

    #get last release build#
    last_release_build_num = _get_last_release_build(job, jk_url, jk_user, jk_pass)

    #never have release build
    if last_release_build_num == 0:
        logger.info("%s never have any release build, skip" % job)
        return False

    logger.info("%s : last_success_build(%d) vs last_release_build(%d)" %
                (job, last_successful_build_num, last_release_build_num))

    if last_successful_build_num == last_release_build_num:
        logger.info("%s last success build is release build, skip" % job)
        return False

    return True


def get_opt():
    parser = argparse.ArgumentParser(description='Submit Maven release build to Jenkins')
    parser.add_argument('--jenkins', dest="jk_url", required=True,
                        help="Jenkins URL (http://localhost:8080/jenkins)")
    parser.add_argument('--job', dest="prj_name", help="Specify Jenkins Job name")
    parser.add_argument('--user', dest="jk_user", required=True,
                        help="Jenkins username")
    parser.add_argument('--pass', dest="jk_pass", required=True,
                        help="Jenkins password")
    parser.add_argument('--dryrun', help="doesn't perform Release build", action='store_true')

    opt = parser.parse_args()

    return opt

def filter_jenkins_jobs_by_name(jobs):
    filtered_jobs = []
    regex = r"^.+_.+_(exe|lib)_.+$"
    exclude_jobs = [
			'ESMerlinAdmin_git_exe_BenefitTransactions',
			'ESMerlinAdmin_git_exe_BenefitTransactions_Dev',
			'ESMerlinAdmin_git_exe_CompTransactions',
			'ESMerlinAdmin_git_exe_CompTransactions_Dev',
			'ESMerlinAdmin_git_exe_Facade',
			'ESMerlinAdmin_git_exe_Payroll',
			'ESMerlinAdmin_git_exe_Payroll_Dev',
			'ESMerlinAdmin_git_exe_PersonService',
			'ESMerlinAdmin_git_exe_Routing',
			'ESMerlinAdmin_git_exe_Tools'
		]
    for job in jobs:
        job_name = job['name']

        m = re.match(regex, job_name) and job_name not in exclude_jobs and not job_name.startswith('TAP_')
        if m:
            filtered_jobs.append(job_name)
        else:
            logger.warning("Jenkins job %s will be ignored" % job_name)

    return filtered_jobs

def get_jenkins_jobs(jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    logger.info("Jenkins API version = %s" % jk.get_version())

    jobs = jk.get_jobs()
    logger.info("Jenkins has %d jobs" % len(jobs))

    return jobs

def main():
    opt = get_opt()

    if opt.prj_name:
        #perform only specified job
        target_jobs = [opt.prj_name]
    else:
        #perform all jobs
        jk_jobs = get_jenkins_jobs(opt.jk_url, opt.jk_user, opt.jk_pass)
        target_jobs = filter_jenkins_jobs_by_name(jk_jobs)

    for job in target_jobs:
        #
        # 1. try to get Maven Release form
        #
        m2release_form = get_m2release_form(opt.jk_url, job)
        if not m2release_form:
            logger.warning("%s doesn't configure Maven Release Build plugin, ignore" % job)
            continue

        #
        # 2. check if "lastBuild" is successful
        #
        if not is_lastBuild_Successful(job, opt.jk_url, opt.jk_user, opt.jk_pass):
            logger.warning("%s doesn't meet a requirement to submit release build, ignore" % job)
            continue

        #
        # 3. compare last "lastSuccessfulBuild" and last-release-build
        #
        if not check_lastSuccessfulBuild(job, opt.jk_url, opt.jk_user, opt.jk_pass):
            logger.warning("%s doesn't meet a requirement to submit release build, ignore" % job)
            continue

        #
        # 4. construct POST form
        #
        params = get_m2release_param(m2release_form)

        #
        # 5. submit release build
        #
        logger.info("=== perform release build for %s ===" % job)
        if opt.dryrun:
            logger.info("dryrun, skip")
        else:
            response = submit_request(opt.jk_url, job, opt.jk_user, opt.jk_pass, params)
            logger.info("submit release build for %s result \"%s %s\"" % (job, response.status, response.reason))


if __name__ == '__main__':
    try:
        logger = pylogger.set_pylogger_config(__name__, True)
        main()

    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()
        os.exit(1)
