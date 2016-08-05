import pylogger
import traceback
import os
import argparse
import re
import mechanize
import jenkins

from base64 import b64encode
from radarclient import RadarClient, AuthenticationStrategySPNego, Person, ClientSystemIdentifier

logger = None

def _get_upstream_job(raw_string):
    #msg = 'Started by upstream project "CMA_git_exe_SMADAPTER" build number 19'
    regex = "Started by upstream project \"(.*)\" build number (\d+)"

    logger.info("try to find upstream job : %s" % raw_string)
    m = re.match(regex, raw_string)

    if m:
        #'CMA_git_exe_SMADAPTER'
        job = m.group(1)

        #'19'
        build_number = int(m.group(2))
        logger.info("found upstream job as %s %d" % (job, build_number))
        return (job, build_number)

    else:
        logger.error("couldn't find parent job, abort : %" % raw_string)
        return (None, None)

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

def _construct_description(jk_url, job, build_number):
    desc = """
    Release build has been FAILED

    Please check the build log below to identify the root cause.
    %s/job/%s/%d/consoleFull
    """ % (jk_url, job, build_number)

    return desc


def submit_radar(desc, job, build_num):
    system_identifier = ClientSystemIdentifier('EMP-SYS', '1.0')
    radar_client = RadarClient(AuthenticationStrategySPNego(), system_identifier)

    data = {
        'title': "Build failure detected: %s #%d" % (job, build_num),
        'component': {'name': 'EMP-SYS CI-CD', 'version': 'Build Issue'},
        'description': desc,
        'classification': 'Task',
        'reproducible': 'Not Applicable',
    }

    logger.info("try to submit a radar")
    radar = radar_client.create_radar(data)


def get_opt():
    parser = argparse.ArgumentParser(description='Submit Jenkins build log to ElasticSearch')
    parser.add_argument('--jenkins', dest="jk_url", required=True,
                        help="Jenkins URL (http://localhost:8080/jenkins)")
    parser.add_argument('--user', dest="jk_user", required=True,
                        help="Jenkins username")
    parser.add_argument('--pass', dest="jk_pass", required=True,
                        help="Jenkins password")
    parser.add_argument('--snapshot', help="submit a ticket even if snapshot build", action='store_true')
    parser.add_argument('--dryrun', help="doesn't perform Release build", action='store_true')

    opt = parser.parse_args()

    return opt


def get_build_log(jk_user, jk_pass):
    '''
    curl -L $BUILD_URL/consoleText
    '''

    BUILD_URL = "BUILD_URL"
    url = None

    #get this URL
    if BUILD_URL in os.environ:
        url = os.environ[BUILD_URL]
    else:
        logger.warning("can't find variable %s, abort" % BUILD_URL)
        return None

    #get /consoleText
    full_url = "%s/consoleText" % url
    userAndPass = b64encode(b"%s:%s" % (jk_user, jk_pass)).decode("ascii")

    br = mechanize.Browser()
    br.addheaders.append(('Authorization', 'Basic %s' % userAndPass))
    try:
        br.open(full_url)
        res = br.response()
    except Exception as e:
        logger.error("%s doesn't have log, abort" % full_url)
        return None

    full_log = res.read()

    return full_log

def get_build_info(jk_url, jk_user, jk_pass, job, build_number):
    jk = jenkins.Jenkins(jk_url, username=jk_user, password=jk_pass)

    build_info = jk.get_build_info(job, build_number)

    if build_info:
        logger.info("got a build_info for %s %d" % (job, build_number))
        return build_info
    else:
        logger.error("couldn't get build_info for %s %d" % (job, build_number))
        return None

def main(opt):
    #get current build log
    build_log = get_build_log(opt.jk_user, opt.jk_pass)
    if not build_log:
        raise("failed to get current build log, abort")

    #identify upstream job
    (upstream_job, build_number) = _get_upstream_job(build_log)
    if not upstream_job:
        raise("failed to get upstream job, abort")

    #get build_info
    build_info = get_build_info(opt.jk_url, opt.jk_user, opt.jk_pass, upstream_job, build_number)
    if build_info:
        #is release or snapshot
        is_release = _is_release_build(build_info)
    else:
        logger.error("failed to get build_info, force submit a ticket")
        is_release = True

    #no matter snapshot or release
    if opt.snapshot:
        logger.info("submit for snapshot build")
        is_release = True

    #construct description
    desc = _construct_description(opt.jk_url, upstream_job, build_number)

    #submit radar ticket only release build
    if is_release:
        if not opt.dryrun:
            submit_radar(desc, upstream_job, build_number)
        else:
            logger.info("dry run, not submit")
    else:
        logger.info("%s %d is snapshot build, skip" % (upstream_job, build_number))

if __name__ == '__main__':
    try:
        logger = pylogger.set_pylogger_config(__name__, True)
        arg_opt = get_opt()
        main(arg_opt)

    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()
        os.exit(1)
