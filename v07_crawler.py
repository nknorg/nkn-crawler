#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

from argv2dict import argv2dict
from nkn_crawler import Crawler

class V07Crawler(Crawler):
    def __init__(self, seed, port='30003', method='getneighbor', **kwargs):
        kwargs['method'] = method
        super(V07Crawler, self).__init__(seed, port, **kwargs)

        self.task_lst.put_nowait(dict(id='', addr=seed.strip('http://').split(':')[0], jsonRpcPort=port))

    def parse(self, resp):
        return resp.get('result')

    ### return ID, ip, port
    def info_from_task(self, task):
        ### TODO: Support IPv6
        uri = task.get('addr', '')
        if uri.find('://') != -1:   ### if has 'any://' prefix
            uri = uri.split('://')[1]   ### strip it
        return task.get('id', ''), uri.split(':')[0], task.get('jsonRpcPort', 30003)

    def task_to_node(self, task):
        return task

if __name__ == "__main__":
    conf = argv2dict(*sys.argv[1:])
    if conf.has_key('timeout'):
        conf['timeout'] = float(conf['timeout'])

    craw = V07Crawler(**conf)
    craw.run(**conf)

    [ sys.stdout.write('%s\n' % json.dumps(n)) for n in craw.result.values() ]
