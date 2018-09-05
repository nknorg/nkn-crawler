[![NKN](https://github.com/nknorg/nkn/wiki/img/nkn_logo.png)](https://nkn.org)

# nkn-crawler

A crawler of NKN network for discover nodes online.

## Prerequisites
> Python 2.7
* Module json
* Module requests
* Module gevent

## Node Crawler Usage

```
./node_crawler.py seed=${IP}[:${ChortPort}] [thread=$N] [timeout=$T]

:param IP:
    IP address should be one of online nodes. x.x.x.x or x.x.x.x:port both of acceptable
:param ChordPort:
    Chord Port of the node. It will be overrided by "param IP" if it provided :port suffix.
    Default: 30000
:param thread:
    Concurrent N threads for crawler.
    Default: 1
:param timeout:
    The timeout threshold for waiting response or no new nodes any more.
    Default: 20
```
