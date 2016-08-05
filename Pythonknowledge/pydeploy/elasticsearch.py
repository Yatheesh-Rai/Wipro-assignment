#!/usr/bin/env python

import jenkins
import httplib
import json
import datetime
import argparse

import pylogger
import traceback
import os

from urlparse import urlparse

logger = None

def _is_release_build(build_info):
    '''
    build_info['actions'][0]['parameters'][0]['name']
    u'MVN_RELEASE_VERSION'
    '''
    for key in build_info.keys():
        if key == 'actions':
            actions = build_info[key]

            for action in actions:
                if 'parameters' in action:
                    for parameter in action['parameters']:
                        if parameter['name'] == 'MVN_RELEASE_VERSION':
                            logger.info("%s is a \"RELEASE\" build" % build_info['fullDisplayName'])
                            return "Release"

    logger.info("%s is a \"SNAPSHOT\" build" % build_info['fullDisplayName'])
    return "Snapshot"


def _get_tab_name(job_name):
    groups = job_name.split('_')
    logger.info("determined tab name as %s" % groups[0])

    return groups[0]


def _get_es_host(es_url):
    url = urlparse(es_url)

    return url.hostname

def _get_es_port(es_url):
    url = urlparse(es_url)

    if url.port:
        return url.port
    else:
        logger.info("assume ES port = 80")
        return 80

def _get_es_path(es_url):
    url = urlparse(es_url)
    path = ''

    if url.path:
        path = url.path
    else:
        path = ""

    if not path.endswith('/'):
        path = path + "/"

    return path

def _has_index(build_name, opt):
    headers = {"Content-type": "applicaiton/json"}
    param = dict({'query' : dict({'match_phrase' : dict({'fullDisplayName' : build_name })})})

    h1 = httplib.HTTPConnection(_get_es_host(opt.es_url), _get_es_port(opt.es_url))
    h1.request("GET", _get_es_path(opt.es_url) + "_search", json.dumps(param, indent=4), headers)
    res = h1.getresponse()

    if res.status == 200:
        try:
            data = json.loads(res.read())
            logger.info("%s has %s index" %(build_name, str(data['hits']['total'])))

            if data['hits']['total'] > 0:
                return True
        except:
            return False

def process(opt):
    jk = jenkins.Jenkins(opt.jk_url, username=opt.jk_user, password=opt.jk_pass)
    jobs=jk.get_jobs()
    headers = {"Content-type": "applicaiton/json"}

    for job in jobs:
        builds = jk.get_job_info(job['name'])['builds']

        for build in builds:
            build_info = jk.get_build_info(job['name'], build['number'])

            #
            # if building, skip
            #
            if build_info['building']:
                logger.info("%s is building, skip" % build_info['fullDisplayName'])
                continue

            #
            # already index or not
            #
            if _has_index(build_info['fullDisplayName'], opt):
                logger.info("%s already indexed, skip" % build_info['fullDisplayName'])
                continue

            #
            # for index purpose
            #
            build_info['job'] = job
            build_info['group'] = _get_tab_name(job['name'])
            build_info['is_release_build'] = _is_release_build(build_info)

            # change unixtime to datetime
            #    yyyyMMdd'T'HHmmss.SSSZ
            #
            if 'timestamp' in build_info:
                unixtime = build_info['timestamp'] / 1000
                build_info['timestamp'] = datetime.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%dT%H:%M:%S')
                logger.info("convert from %d to %s" %(unixtime, build_info['timestamp']))
            else:
                logger.warning("couldn't find timestamp for %s" % build_info['fullDisplayName'])
                build_info['timestamp'] = "2000-01-01 00:00:00"

            #
            # submit to ElasticSearch
            #
            if not opt.dryrun:
                logger.info("submit a log to ElastisSearch for %s" % build_info['fullDisplayName'])
                h1 = httplib.HTTPConnection(_get_es_host(opt.es_url), _get_es_port(opt.es_url))
                h1.request("POST", _get_es_path(opt.es_url), json.dumps(build_info, indent=4), headers)
                res = h1.getresponse()

                print res.status
            else:
                logger.warning("dryrun, skip to submit to ElasticSearch for %s" % build_info['fullDisplayName'])


def get_opt():
    parser = argparse.ArgumentParser(description='Submit Jenkins build log to ElasticSearch')
    parser.add_argument('--jenkins', dest="jk_url", required=True,
                        help="Jenkins URL (http://localhost:8080/jenkins)")
    parser.add_argument('--user', dest="jk_user", required=True,
                        help="Jenkins username")
    parser.add_argument('--pass', dest="jk_pass", required=True,
                        help="Jenkins password")
    parser.add_argument('--es', dest="es_url", required=True,
                        help="ElasticSearch URL (http://localhost:9200/my_index/mydata/)")
    parser.add_argument('--dryrun', help="doesn't perform Release build", action='store_true')

    opt = parser.parse_args()
    print "a"
    return opt


def main():
    try:
        opt = get_opt()
        process(opt)

    except Exception as e:
        logger.info(str(e))
        traceback.print_exc()
        os.exit(1)

if __name__ == '__main__':
    logger = pylogger.set_pylogger_config(__name__, True)
    main()

