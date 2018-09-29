#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()
import sys
import time
import json
import requests
from argv2dict import argv2dict

import gevent
from gevent.pool import Group
from gevent.queue import Queue

class Crawler(object):
    def __init__(self, seed, port='30000', **kwargs):
        self.result = {}
        self.probed = set()
        self.task_lst = Queue()
        self.pool = Group()

        addr = seed.split(':')    ### Invalid the seed if conf NOT set
        if len(addr)==1: ### if seed str not contain port, use conf['port'] or default
            addr += [port]
        elif len(addr) > 2:
            ### TODO: Usage
            sys.stderr.write('Invalid seed %s\n' % seed)
            exit(22)

        self.task_lst.put_nowait(dict(Host=':'.join(addr)))
        sys.stderr.write('Crawler start from %s\n' % (':'.join(addr)))

    def req(self, ip, port=30003, apiId='1', apiVer='3.0', method='getchordringinfo', params={}, timeout=20, **kwargs):
        d = dict(id=apiId, jsonrpc=apiVer, method=method, params=params)
        try:
            r = requests.post('http://%s:%s' % (ip, port), json=d, headers={'Content-Type':'application/json'}, timeout=timeout)
        except Exception as e:
            sys.stderr.write('%s: POST %s:%s met error %s\n' % (time.strftime('%F %T'), ip, port, e.message))
            return ''
        return r.text

    def parse(self, resp):
        try:
            d = json.loads(resp)
        except Exception as e:
            sys.stderr.write('%s: json load [%s] met error %s\n' % (time.strftime('%F %T'), resp, e.message))
            return

        for vn in d.get('result',{}).get('Vnodes',[]):
            Id = vn.get('Id','')
            Host, chord_port = vn.get('Host','').split(':')

            ### Save craw result
            succ_lst = [ n for n in vn.pop('Successors',[]) if n ]
            succ_lst += [ n for n in vn.pop('Finger',[]) if n ]
            succ_lst += [ vn.pop('Predecessor') or {} ]
            self.result[Id] = vn

            ### craw Successor
            for succ in succ_lst:
                if succ.get('Id', '') in self.probed:
                    continue    ### craw already
                self.task_lst.put_nowait(succ)

    def worker(self, timeout=20):
        while True:
            try:
                t = self.task_lst.get(timeout=timeout)
                if t.get('Id', '') in self.probed:
                    continue    ### craw already
                else:
                    self.probed.add(t.get('Id', ''))

                n = t.get('Host','').split(':')
                if len(n) != 2:
                    continue    ### invalid Host

                host, chord_port = n
                self.parse(self.req(host, int(chord_port)+3))
            except AttributeError as e:
                sys.stderr.write('%s: worker exit req %s met err %s\n' % (time.strftime('%F %T'), str(n),type(e)))
                continue
            except Exception as e:
                sys.stderr.write('%s: worker exit due to err %s\n' % (time.strftime('%F %T'), type(e)))
                break

    def debug(self, interval=5):
        while True:
            sys.stderr.write('Craw results %d\n' % len(self.result))
            gevent.sleep(interval)

    def run(self, timeout=20, thread=1, **kwargs):
        gevent.spawn(self.debug, 5)
        self.pool.map(self.worker, [int(timeout)]*int(thread))
        self.pool.join()
        sys.stderr.write('Total: %d Nodes\n' % len(self.result))

if __name__ == "__main__":
    conf = argv2dict(*sys.argv[1:])

    craw = Crawler(**conf)
    craw.run(**conf)

    [ sys.stdout.write('%s\n' % json.dumps(n)) for n in craw.result.values() ]
