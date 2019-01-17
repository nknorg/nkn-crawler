#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()
import sys
import time
import json
import requests
import traceback
from argv2dict import argv2dict

import gevent
from gevent.pool import Group
from gevent.queue import Queue
from gevent.queue import Empty

class Crawler(object):
    def __init__(self, seed, port='30000', **kwargs):
        self.result = {}
        self.probed = set()
        self.task_lst = Queue()
        self.pool = Group()
        self.conf = kwargs

        addr = seed.split(':')    ### Invalid the seed if conf NOT set
        if len(addr)==1: ### if seed str not contain port, use conf['port'] or default
            addr += [port]
        elif len(addr) > 2:
            ### TODO: Usage
            sys.stderr.write('Invalid seed %s\n' % seed)
            exit(22)

        #self.task_lst.put_nowait(dict(Host=':'.join(addr)))
        sys.stderr.write('Crawler start from %s\n' % (':'.join(addr)))

    def req(self, ip, port=30003, apiId='1', apiVer='3.0', method='getchordringinfo', params={}, timeout=20, **kwargs):
        r = ''
        ret = {}
        d = dict(id=apiId, jsonrpc=apiVer, method=method, params=params)
        try:
            r = requests.post('http://%s:%s' % (ip, port), json=d, headers={'Content-Type':'application/json'}, timeout=timeout)
            ret = json.loads(r.text)
        except Exception as e:
            sys.stderr.write('%s: met Error [%s] when request [%s] from %s:%s resp [%s]\n' % (
                time.strftime('%F %T'), e.message, method, ip, port, r.text if r else ''
            ))
            raise e
        return ret

    def parse(self, resp):
        succ_lst = []
        for vn in resp.get('result',{}).get('Vnodes',[]):
            ### new discovery
            succ_lst += [ n for n in vn.pop('Successors',[]) if n ]
            succ_lst += [ n for n in vn.pop('Finger',[]) if n ]
            succ_lst += [ vn.pop('Predecessor') or {} ]
        return succ_lst

    def info_from_task(self, task):
        ip, port = task.get('Host', '').split(':')
        return task.get('Id', ''), ip, int(port)+3

    def task_to_node(self, task):
        return task

    def worker(self, timeout=20):
        while True:
            try:
                t = self.task_lst.get(timeout=timeout)
                Id, ip, port = self.info_from_task(t)

                if ip and port and Id not in self.probed: ### Is valid task and Not crawl yet
                    self.probed.add(Id) ### mark it as crawled whatever success or fail
                    new_nodes = self.parse(self.req(ip, port, **self.conf))
                    self.result[Id] = self.task_to_node(t)    ### Add to crawl result
                    [ self.task_lst.put_nowait(n) for n in new_nodes ] ### add new_nodes into task_lst
            except Empty as e:
                sys.stderr.write('%s: worker exit due to err %s\n' % (time.strftime('%F %T'), type(e)))
                break
            except Exception as e:
                sys.stderr.write('%s: worker req %s met err %s\n' % (time.strftime('%F %T'), str(t), type(e)))
                # print traceback.format_exc(e) ### stay for debug
                continue

    def debug(self, interval=5):
        while True:
            sys.stderr.write('Craw results %d\n' % len(self.result))
            gevent.sleep(interval)

    def run(self, timeout=20, thread=1, **kwargs):
        gevent.spawn(self.debug, 5)
        self.pool.map(self.worker, [timeout]*int(thread))
        self.pool.join()
        sys.stderr.write('Total: %d Nodes\n' % len(self.result))

if __name__ == "__main__":
    conf = argv2dict(*sys.argv[1:])
    if conf.has_key('timeout'):
        conf['timeout'] = float(conf['timeout'])

    craw = Crawler(**conf)
    craw.run(**conf)

    [ sys.stdout.write('%s\n' % json.dumps(n)) for n in craw.result.values() ]
