#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import json
import traceback

from gevent.queue import Empty

from argv2dict import argv2dict
from nkn_crawler import Crawler

class ChordCrawler(Crawler):
    def __init__(self, seed, port='30003', method='getchordringinfo', **kwargs):
        kwargs['method'] = method
        super(ChordCrawler, self).__init__(seed, port, **kwargs)

        self.task_lst.put_nowait(dict(id='', addr=seed.strip('http://').split(':')[0], jsonRpcPort=port))

    def parse(self, resp):
        d = resp.get('result') or {}
        lnode = d.pop('localNode', {})
        lnode.update(d)
        return lnode

    ### return ID, ip, port
    def info_from_task(self, task):
        ### TODO: Support IPv6
        uri = task.get('addr', '')
        if uri.find('://') != -1:   ### if has 'any://' prefix
            uri = uri.split('://')[1]   ### strip it
        return task.get('id', ''), uri.split(':')[0], task.get('jsonRpcPort', 30003)

    def task_to_node(self, node):
        ret = node.get('successors', [])
        ret += node.get('predecessors', [])
        return reduce(lambda x,y:x+y, node.get('fingerTable', {}).values(), ret)

    def worker(self, timeout=20):
        while True:
            try:
                t = self.task_lst.get(timeout=timeout)
                Id, ip, port = self.info_from_task(t)

                if ip and port and Id not in self.probed: ### Is valid task and Not crawl yet
                    if Id:  self.probed.add(Id) ### mark it as crawled already. Empty Id means task from sys.argv
                    new_node = self.parse(self.req(ip, port, **self.conf))
                    Id = new_node.get('id')
                    if Id:  self.result[Id] = new_node    ### Add to crawl result
                    [ self.task_lst.put_nowait(n) for n in self.task_to_node(new_node) if n.get('id') not in self.probed ] ### add new task_to_node into task_lst
            except Empty as e:
                sys.stderr.write('%s: worker exit due to err %s\n' % (time.strftime('%F %T'), type(e)))
                break
            except Exception as e:
                sys.stderr.write('%s: worker req %s met err %s\n' % (time.strftime('%F %T'), str(t), type(e)))
                sys.stderr.write(traceback.format_exc(e)) ### stay for debug
                continue

if __name__ == "__main__":
    conf = argv2dict(*sys.argv[1:])
    if conf.has_key('timeout'):
        conf['timeout'] = float(conf['timeout'])

    craw = ChordCrawler(**conf)
    craw.run(**conf)

    [ sys.stdout.write('%s\n' % json.dumps(n)) for n in craw.result.values() ]
