#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

from argv2dict import argv2dict
from nkn_crawler import Crawler

class NodeCrawler(Crawler):
    def __init__(self, seed, port='30001', method='getneighbor', **kwargs):
        kwargs['method'] = method
        super(NodeCrawler, self).__init__(seed, port, **kwargs)

        ip16 = [0]*12 + [ int(b) for b in seed.split('.') ]
        self.task_lst.put_nowait(dict(ID='', IpAddr=ip16, Port=port))

    def parse(self, resp):
        return resp.get('result')

    ### return ID, ip, port
    def info_from_task(self, task):
        port = task.get('Port', 30001)
        ### TODO: Support IPv6
        ip = '.'.join([ str(b) for b in task.get('IpAddr', [])[12:] ])
        return task.get('ID', ''), ip, int(port)+2

    def task_to_node(self, task):
        ip = '.'.join([ str(b) for b in task.pop('IpAddr', [])[12:] ])
        task['IpAddr'] = ip
        task.pop('Time', None)
        return task

if __name__ == "__main__":
    conf = argv2dict(*sys.argv[1:])
    craw = NodeCrawler(**conf)
    craw.run(**conf)

    [ sys.stdout.write('%s\n' % json.dumps(n)) for n in craw.result.values() ]
