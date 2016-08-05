import pylogger
import traceback
import os
import jenkins
import argparse
import mechanize
import re
import datetime
import time
import csv


from base64 import b64encode
from xml.dom.minidom import parseString
from prettytable import PrettyTable



logger = None
JOB_HISTORY_RANGE = 7 * 24 * 60 * 60 #7 days


def get_opt():
    parser = argparse.ArgumentParser(description='Submit Maven release build to Jenkins')
    parser.add_argument('--jenkins', dest="jk_url", required=True,
                        help="Jenkins URL (http://localhost:8080/jenkins)")
    parser.add_argument('--job', dest="job_name", help="Specify Jenkins Job name")
    parser.add_argument('--user', dest="jk_user", required=True,
                        help="Jenkins username")
    parser.add_argument('--pass', dest="jk_pass", required=True,
                        help="Jenkins password")
    parser.add_argument('--dryrun', help="doesn't perform Release build", action='store_true')

    opt = parser.parse_args()

    return opt

def get_jenkins_jobs(jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    logger.info("Jenkins API version = %s" % jk.get_version())

    jobs = jk.get_jobs()
    logger.info("Jenkins has %d jobs" % len(jobs))

    return jobs


def _get_maven_goal(job, jk_url, jk_user, jk_pass):
    full_url = "%s/job/%s/config.xml" % (jk_url, job)
    userAndPass = b64encode(b"%s:%s" % (jk_user, jk_pass)).decode("ascii")

    br = mechanize.Browser()
    br.addheaders.append(('Authorization', 'Basic %s' % userAndPass))
    try:
        br.open(full_url)
        res = br.response()
    except Exception as e:
        logger.error("%s doesnt' have maven goal" % job)
        return None

    config_xml = res.read()

    try:
        dom = parseString(config_xml)
        goals_element = dom.getElementsByTagName("goals")[0]
        goals = goals_element.childNodes[0].data

        return goals

    except Exception as e:
        logger.error("couldn't parse XML %s" % config_xml)
        return None


def _is_checkstyle_enabled(mvn_goal):
    if mvn_goal.find("checkstyle:checkstyle") > 1:
        logger.info("found checkstyle setting in mvn goal : %s" % mvn_goal)
        return True
    else:
        logger.info("NOT found checkstyle setting in mvn goal : %s" % mvn_goal)
        return False

def _is_pmd_enabled(mvn_goal):
    if mvn_goal.find("pmd:pmd") > 1:
        logger.info("found pmd setting in mvn goal : %s" % mvn_goal)
        return True
    else:
        logger.info("NOT found pmd setting in mvn goal : %s" % mvn_goal)
        return False

def _is_findbugs_enabled(mvn_goal):
    if mvn_goal.find("findbugs:findbugs") > 1:
        logger.info("found pmd setting in findbugs goal : %s" % mvn_goal)
        return True
    else:
        logger.info("NOT found pmd setting in findbugs goal : %s" % mvn_goal)
        return False

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


def _get_last_snapshot_build(job, jk_url, jk_user, jk_pass):
    build_histories = _get_build_history(job, jk_url, jk_user, jk_pass, False)
    latest_timestamp = 0
    latest_snapshot_build_num = 0

    for build_history in build_histories:
        if not build_history['isRelease']:
            if latest_timestamp < int(build_history['timestamp']):
                latest_timestamp = int(build_history['timestamp'])
                latest_snapshot_build_num = build_history['number']
                logger.info("%s last snapshot build %d" % (job, latest_snapshot_build_num))

    return latest_snapshot_build_num


def _is_release_build(build_info):
    actions = build_info['actions']

    #
    # release build has parameters
    # ex: {u'parameters': [{u'name': u'MVN_RELEASE_VERSION', u'value': u'1.1.9'}, {u'name': u'MVN_DEV_VERSION', u'value': u'1.1.10-SNAPSHOT'}, {u'name': u'MVN_ISDRYRUN', u'value': False}]}

    #
    for action in actions:
        if 'parameters' in action:
            parameters = action['parameters']

            for parameter in parameters:
                if parameter['name'].find("MVN") >= 0:
                    logger.info("%s is release build" % build_info['fullDisplayName'])
                    return True

    return False


def _get_build_history(job, jk_url, jk_user, jk_pass, is_skip_older):
    build_histories = []

    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    logger.info("Jenkins API version = %s" % jk.get_version())

    builds = jk.get_job_info(job)['builds']
    logger.info("%s has %d builds" % (job, len(builds)))

    for build in builds:
        build_info = jk.get_build_info(job, build['number'])

        #skip more than 1 week ago
        if is_skip_older:
            unixtime = int(build_info['timestamp']) / 1000
            a_week_ago = time.time() - JOB_HISTORY_RANGE
            if unixtime < a_week_ago:
                logger.info("%s:%d is older than a week(%s), skip" %
                        (job,
                         int(build['number']),
                         datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')))
                continue

        build_history = build_info
        build_history["version"] = build_info["mavenVersionUsed"]
        build_history["isRelease"] = _is_release_build(build_info)

        build_histories.append(build_history)

    return build_histories

def _get_datetime_by_build_num(job, num, jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    build_info = jk.get_build_info(job, num)
    unixtime = int(build_info['timestamp']) / 1000
    timestamp = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

    logger.info("convert timestamp from %s to %s" %(build_info['timestamp'], timestamp))

    return timestamp

def _build_statistics(job, histories):
    result = {}
    result["snapshot_success"] = 0
    result["snapshot_fail"] = 0
    result["snapshot_count"] = 0
    result["snapshot_ratio"] = 0.0
    result["release_success"] = 0
    result["release_fail"] = 0
    result["release_count"] = 0
    result["release_ratio"] = 0.0

    for history in histories:
        #if building
        if history['building']:
            logger.info("%s %d is building, skip" %(job, history["number"]))
            continue

        #check success or not
        is_success = False
        if history["result"].find("SUCCESS") == 0:
            is_success = True

        #release build
        if history["isRelease"] :
            result["release_count"] = result["release_count"] + 1
            if is_success:
                result["release_success"] = result["release_success"] + 1
            else:
                result["release_fail"] = result["release_fail"] + 1

        #snapshot build
        else:
            result["snapshot_count"] = result["snapshot_count"] + 1
            if is_success:
                result["snapshot_success"] = result["snapshot_success"] + 1
            else:
                result["snapshot_fail"] = result["snapshot_fail"] + 1

    #success ratio
    if result["snapshot_count"] > 0:
        result["snapshot_ratio"] = (float(result["snapshot_success"])/float(result["snapshot_count"])) * 100.0
    else:
        result["snapshot_ratio"] = 0

    if result["release_count"] > 0:
        result["release_ratio"] = (float(result["release_success"])/float(result["release_count"])) * 100.0
    else:
        result["release_ratio"] = 0

    return result

'''
- Static Code Analyzer(CheckStyle, PMD, FindBugs) enable or not
- snapshot / release build success / failure rate on 1 week range
- last snapshot build version and date
- last release build version and date
- UT code coverage (Cobertura enabling)
'''
def get_report(job, jk_url, jk_user, jk_pass):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)
    logger.info("Jenkins API version = %s" % jk.get_version())

    report = {}
    report["job"] = job

    #quality
    mvn_goal = _get_maven_goal(job, jk_url, jk_user, jk_pass)
    if mvn_goal:
        report["checkstyle_enabled"] = _is_checkstyle_enabled(mvn_goal)
        report["pmd_enabled"] = _is_pmd_enabled(mvn_goal)
        report["findbugs_enabled"] = _is_findbugs_enabled(mvn_goal)
    else:
        logger.warning("%s doesn't have maven goal" % job)
        report["checkstyle_enabled"] = "None"
        report["pmd_enabled"] = "None"
        report["findbugs_enabled"] = "None"

    #build statistics
    job_histories = _get_build_history(job, jk_url, jk_user, jk_pass, True)
    report["statistics"] = _build_statistics(job, job_histories)

    #last release build
    build_num = _get_last_release_build(job, jk_url, jk_user, jk_pass)
    build_datetime = "-"
    is_had_build_before = False
    if build_num > 0:
        build_datetime = _get_datetime_by_build_num(job, build_num, jk_url, jk_user, jk_pass)
        is_had_build_before = True

    logger.info("%s : last release build number = %d" % (job, build_num))
    logger.info("%s : last release build datetime = %s" % (job, build_num))
    report["last_release_build_num"] = build_num
    report["last_release_build_datetime"] = build_datetime
    report["is_had_release_build_before"] = is_had_build_before


    #last snapshot build
    build_num = _get_last_snapshot_build(job, jk_url, jk_user, jk_pass)
    build_datetime = "-"
    is_had_build_before = False
    if build_num > 0:
        build_datetime = _get_datetime_by_build_num(job, build_num, jk_url, jk_user, jk_pass)
        is_had_build_before = True

    logger.info("%s : last snapshot build number = %d" % (job, build_num))
    logger.info("%s : last snapshot build datetime = %s" % (job, build_num))
    report["last_snapshot_build_num"] = build_num
    report["last_snapshot_build_datetime"] = build_datetime
    report["is_had_snapshot_build_before"] = is_had_build_before

    return report

def filter_jenkins_jobs_by_name(jobs):
    filtered_jobs = []
    regex = r"^.+_.+_(exe|lib)_.+$"

    for job in jobs:
        job_name = job['name']

        m = re.match(regex, job_name)
        if m:
            filtered_jobs.append(job_name)
        else:
            logger.warning("Jenkins job %s will be ignored" % job_name)

    return filtered_jobs

def _get_statistics_string(success, fail, total, ratio, is_had_release_before):
    if total > 0:
        return "%d + %d = %d (%d %% success)" % (success, fail, total, ratio)
    else:
        if is_had_release_before:
            return "None this week"
        else:
            return "-"

    pass


def print_report(reports):
    table = PrettyTable(["Job Name",
                         "CheckStyle", "PMD", "Findbugs",

                         "last snapshot build #", "last snapshot date",
                         "# of snapshot (success + fail = total (ratio))",

                         "last release build #", "last release date",
                         "# of release (success + fail = total (ratio))"
                         ])
    '''
    statistics
    result["snapshot_success"] = 0
    result["snapshot_fail"] = 0
    result["snapshot_count"] = 0
    result["snapshot_ratio"] = 0
    result["release_success"] = 0
    result["release_fail"] = 0
    result["release_count"] = 0
    result["release_ratio"] = 0
'''

    for report in reports:
        table.add_row([
            report['job'],
            report["checkstyle_enabled"], report["pmd_enabled"], report["findbugs_enabled"],

            report["last_snapshot_build_num"], report["last_snapshot_build_datetime"],
            _get_statistics_string(report["statistics"]["snapshot_success"],
                                   report["statistics"]["snapshot_fail"],
                                   report["statistics"]["snapshot_count"],
                                   report["statistics"]["snapshot_ratio"],
                                   report["is_had_snapshot_build_before"]),

            report["last_release_build_num"], report["last_release_build_datetime"],
            _get_statistics_string(report["statistics"]["release_success"],
                                   report["statistics"]["release_fail"],
                                   report["statistics"]["release_count"],
                                   report["statistics"]["release_ratio"],
                                   report["is_had_release_build_before"])
        ])

    print table

def print_csv(reports):
    #print header
    print "Job Name, CheckStyle, PMD, Findbugs, \
    \last snapshot build #, last snapshot date, # of snapshot (success + fail = total (ratio)), \
    \last release build #, last release date, # of release (success + fail = total (ratio))"

    for report in reports:
        print "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
            report['job'],
            report["checkstyle_enabled"], report["pmd_enabled"], report["findbugs_enabled"],

            report["last_snapshot_build_num"], report["last_snapshot_build_datetime"],
            _get_statistics_string(report["statistics"]["snapshot_success"],
                                   report["statistics"]["snapshot_fail"],
                                   report["statistics"]["snapshot_count"],
                                   report["statistics"]["snapshot_ratio"],
                                   report["is_had_snapshot_build_before"]),

            report["last_release_build_num"], report["last_release_build_datetime"],
            _get_statistics_string(report["statistics"]["release_success"],
                                   report["statistics"]["release_fail"],
                                   report["statistics"]["release_count"],
                                   report["statistics"]["release_ratio"],
                                   report["is_had_release_build_before"])
        )

def save_csv(reports):
    f = open('report.csv', 'wb')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["Job Name", "CheckStyle", "PMD", "Findbugs",
                         "last snapshot build #", "last snapshot date", "# of snapshot (success + fail = total (ratio))",
                         "last release build #", "last release date", "# of release (success + fail = total (ratio))"])
    for report in reports:
        csv_writer.writerow([
            report['job'],
            report["checkstyle_enabled"], report["pmd_enabled"], report["findbugs_enabled"],

            report["last_snapshot_build_num"], report["last_snapshot_build_datetime"],
            _get_statistics_string(report["statistics"]["snapshot_success"],
                                   report["statistics"]["snapshot_fail"],
                                   report["statistics"]["snapshot_count"],
                                   report["statistics"]["snapshot_ratio"],
                                   report["is_had_snapshot_build_before"]),

            report["last_release_build_num"], report["last_release_build_datetime"],
            _get_statistics_string(report["statistics"]["release_success"],
                                   report["statistics"]["release_fail"],
                                   report["statistics"]["release_count"],
                                   report["statistics"]["release_ratio"],
                                   report["is_had_release_build_before"])
        ])


def send_email(filename):
    pass

def main(arg_opt):
    jobs = []
    reports = []

    #either single job or all jobs
    if arg_opt.job_name:
        jobs.append(arg_opt.job_name)
    else:
        jk_jobs = get_jenkins_jobs(arg_opt.jk_url, arg_opt.jk_user, arg_opt.jk_pass)
        jobs = filter_jenkins_jobs_by_name(jk_jobs)

    #get report
    for job in jobs:
        report = get_report(job, arg_opt.jk_url, arg_opt.jk_user, arg_opt.jk_pass)
        if report:
            reports.append(report)

    print_report(reports)
    print_csv(reports)
    filename=save_csv(reports)
    #send_email(filename)

if __name__ == '__main__':
    try:
        logger = pylogger.set_pylogger_config(__name__, True)
        arg_opt = get_opt()
        main(arg_opt)

    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()
        os.exit(1)
