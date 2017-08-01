{%- from "dcache/map.jinja" import dcache with context -%}
#!/usr/bin/env python

import pexpect
import pickle
import re
import socket
import struct
import time
from xml.dom import minidom

def getElement(line, element, sep = ' '):
    parts = line.split(sep)
    parts = filter(None, parts)
    if (len(parts) > element):
        return parts[element]
    else:
        return ''

def getValue(lines, keyText, element):
    for i in lines:
        if keyText in i:
            return getElement(i, element)
    return ''

def getLinesBetween(input, before, after):
    lines = []
    started = False
    for i in input:
        if (started):
            if (i != after):
                lines.append(i)
            else:
                return lines
        else:
            if (i == before):
                started = True
                lines.append(i)
    return lines


class Metric:
    def __init__(self, n, v, t):
        self.name = n
        self.value = v
        self.timestamp = t


class PoolInfo:
    def __init__(self, xml):
        self.name = ""
        self.restore_queued = -1
        self.restore_active = -1
        self.regular_queued = -1
        self.regular_active = -1
        self.p2p_client_active = -1
        self.p2p_client_queued = -1
        self.store_active = -1
        self.store_queued = -1
        self.p2p_active = -1
        self.p2p_queued = -1
        self.size = -1
        self.precious = -1
        self.removable = -1
        self.used = -1
        self.free = -1
        self.timestamp = int(time.time())
        self.metric_readerrors = 0

        self.name = xml.getAttribute('name')
        queues = xml.getElementsByTagName('queue')
        if (len(queues) == 0):
            self.metric_readerrors += 1
        for q in queues:
            active = -1
            queued = -1
            type = q.getAttribute('type')
            name = q.getAttribute('name')
            if (type == ""):
                type = name
            metrics = q.getElementsByTagName('metric')
            for m in metrics:
                name = m.getAttribute('name')
                if (name == "active"):
                    active = int(m.firstChild.nodeValue)
                elif (name == "queued"):
                    queued = int(m.firstChild.nodeValue)
            if (type == "restore"):
                self.restore_queued = queued
                self.restore_active = active
            elif (type == "regular"):
                self.regular_queued = queued
                self.regular_active = active
            elif (type == "p2p-clientqueue"):
                self.p2p_client_queued = queued
                self.p2p_client_active = active
            elif (type == "store"):
                self.store_queued = queued
                self.store_active = active
            elif (type == "p2p-queue"):
                self.p2p_queued = queued
                self.p2p_active = active
            else:
                print 'unknown queue type:',name
                self.metric_readerrors += 1

        space = xml.getElementsByTagName('space')
        if (len(space) == 1):
            metrics = space[0].getElementsByTagName('metric')
            for m in metrics:
                name = m.getAttribute('name')
                value = m.firstChild.nodeValue
                if (name == "total"):
                    self.size = long(value)
                elif (name == "precious"):
                    self.precious = long(value)
                elif (name == "removable"):
                    self.removable = long(value)
                elif (name == "used"):
                    self.used = long(value)
                elif (name == "free"):
                    self.free = long(value)
                elif (name == "break-even"):
                    pass
                elif (name == "gap"):
                    pass
                elif (name == "LRU-seconds"):
                    pass
                else:
                    print 'unknown space value type:',name
                    self.metric_readerrors += 1

        if (self.name == ""):
            self.metric_readerrors += 1
        if (self.restore_queued == -1):
            self.metric_readerrors += 1
        if (self.restore_active == -1):
            self.metric_readerrors += 1
        if (self.regular_queued == -1):
            self.metric_readerrors += 1
        if (self.regular_active == -1):
            self.metric_readerrors += 1
        if (self.p2p_client_active == -1):
            self.metric_readerrors += 1
        if (self.p2p_client_queued == -1):
            self.metric_readerrors += 1
        if (self.store_active == -1):
            self.metric_readerrors += 1
        if (self.store_queued == -1):
            self.metric_readerrors += 1
        if (self.p2p_active == -1):
            self.metric_readerrors += 1
        if (self.p2p_queued == -1):
            self.metric_readerrors += 1
        if (self.size == -1):
            self.metric_readerrors += 1
        if (self.precious == -1):
            self.metric_readerrors += 1
        if (self.removable == -1):
            self.metric_readerrors += 1
        if (self.used == -1):
            self.metric_readerrors += 1
        if (self.free == -1):
            self.metric_readerrors += 1

        return

    def metrics(self):
        metrics = []
        if (self.restore_queued >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.restore.queued', self.restore_queued, self.timestamp))
        if (self.restore_active >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.restore.active', self.restore_active, self.timestamp))
        if (self.regular_queued >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.regular.queued', self.regular_queued, self.timestamp))
        if (self.regular_active >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.regular.active', self.regular_active, self.timestamp))
        if (self.p2p_client_queued >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.p2p_client.queued', self.p2p_client_queued, self.timestamp))
        if (self.p2p_client_active >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.p2p_client.active', self.p2p_client_active, self.timestamp))
        if (self.store_queued >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.store.queued', self.store_queued, self.timestamp))
        if (self.store_active >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.store.active', self.store_active, self.timestamp))
        if (self.p2p_queued >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.p2p.queued', self.p2p_queued, self.timestamp))
        if (self.p2p_active >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.queue.p2p.active', self.p2p_active, self.timestamp))
        if (self.size >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.size', self.size, self.timestamp))
        if (self.precious >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.precious', self.precious, self.timestamp))
        if (self.removable >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.removable', self.removable, self.timestamp))
        if (self.used >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.used', self.used, self.timestamp))
        if (self.free >= 0):
            metrics.append(Metric('dcache.pool.' + self.name + '.free', self.free, self.timestamp))
        metrics.append(Metric('dcache.pool.' + self.name + '.metric_errors', self.metric_readerrors, self.timestamp))
        return metrics



class PoolGroupInfo:
    def __init__(self, xml, poolInfo):
        self.name = ""
        self.pools = []
        self.restore_queued = -1
        self.restore_active = -1
        self.regular_queued = -1
        self.regular_active = -1
        self.p2p_client_active = -1
        self.p2p_client_queued = -1
        self.store_active = -1
        self.store_queued = -1
        self.p2p_active = -1
        self.p2p_queued = -1
        self.size = -1
        self.precious = -1
        self.removable = -1
        self.used = -1
        self.free = -1
        self.timestamp = int(time.time())
        self.metric_readerrors = 0


        self.name = xml.getAttribute('name')
        pools = xml.getElementsByTagName('pools')
        if (len(pools) == 1):
            poolrefs = pools[0].getElementsByTagName('poolref')
            for pool in poolrefs:
                name = pool.getAttribute('name')
                if (name != ""):
                    self.pools.append(name)

        self.restore_queued = self.sum(poolInfo, 'restore_queued')
        self.restore_active = self.sum(poolInfo, 'restore_active')
        self.regular_queued = self.sum(poolInfo, 'regular_queued')
        self.regular_active = self.sum(poolInfo, 'regular_active')
        self.p2p_client_active = self.sum(poolInfo, 'p2p_client_active')
        self.p2p_client_queued = self.sum(poolInfo, 'p2p_client_queued')
        self.store_active = self.sum(poolInfo, 'store_active')
        self.store_queued = self.sum(poolInfo, 'store_queued')
        self.p2p_active = self.sum(poolInfo, 'p2p_active')
        self.p2p_queued = self.sum(poolInfo, 'p2p_queued')
        self.size = self.sum(poolInfo, 'size')
        self.precious = self.sum(poolInfo, 'precious')
        self.removable = self.sum(poolInfo, 'removable')
        self.used = self.sum(poolInfo, 'used')
        self.free = self.sum(poolInfo, 'free')
        return

    def metrics(self):
        metrics = []
        if (self.restore_queued >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.restore.queued', self.restore_queued, self.timestamp))
        if (self.restore_active >= 0):
             metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.restore.active', self.restore_active, self.timestamp))
        if (self.regular_queued >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.regular.queued', self.regular_queued, self.timestamp))
        if (self.regular_active >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.regular.active', self.regular_active, self.timestamp))
        if (self.p2p_client_queued >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.p2p_client.queued', self.p2p_client_queued, self.timestamp))
        if (self.p2p_client_active >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.p2p_client.active', self.p2p_client_active, self.timestamp))
        if (self.store_queued >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.store.queued', self.store_queued, self.timestamp))
        if (self.store_active >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.store.active', self.store_active, self.timestamp))
        if (self.p2p_queued >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.p2p.queued', self.p2p_queued, self.timestamp))
        if (self.p2p_active >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.queue.p2p.active', self.p2p_active, self.timestamp))
        if (self.size >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.size', self.size, self.timestamp))
        if (self.precious >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.precious', self.precious, self.timestamp))
        if (self.removable >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.removable', self.removable, self.timestamp))
        if (self.used >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.used', self.used, self.timestamp))
        if (self.free >= 0):
            metrics.append(Metric('dcache.pgroup.' + self.name + '.free', self.free, self.timestamp))
        metrics.append(Metric('dcache.pgroup.' + self.name + '.metric_errors', self.metric_readerrors, self.timestamp))
        return metrics

    def sum(self, poolInfo, key):
        value = int(0)
        for i in poolInfo:
            if (i.name in self.pools):
                v = getattr(i, key)
                if (v >= 0):
                    value += getattr(i, key)
                else:
                    self.metric_readerrors += 1
        return value


class NFSDoorInfo:
    def __init__(self, name, info, transfers):
        self.name = name
        self.clients = -1
        self.transfers = -1
        self.reads = -1
        self.writes = -1
        self.timestamp = int(time.time())
        self.metric_readerrors = 0

        self.clients = getValue(info, "Number of NFSv4 clients :", 5)
        self.transfers = len(transfers)
        self.reads = 0
        self.writes = 0
        for i in transfers:
            type = getElement(i, 4)
            if (type == "READ"):
                self.reads += 1
            elif (type == "WRITE"):
                self.writes += 1
            else:
                self.metric_readerrors += 1
        return

    def metrics(self):
        metrics = []
        if (self.clients >= 0):
            metrics.append(Metric('dcache.door.nfs.' + self.name + '.clients', self.clients, self.timestamp))
        if (self.transfers >= 0):
            metrics.append(Metric('dcache.door.nfs.' + self.name + '.transfers', self.transfers, self.timestamp))
        if (self.reads >= 0):
            metrics.append(Metric('dcache.door.nfs.' + self.name + '.reads', self.reads, self.timestamp))
        if (self.writes >= 0):
            metrics.append(Metric('dcache.door.nfs.' + self.name + '.writes', self.writes, self.timestamp))
        metrics.append(Metric('dcache.door.nfs.' + self.name + '.metric_errors', self.metric_readerrors, self.timestamp))
        return metrics


class XrootdDoorInfo:
    def __init__(self, name, info, connections):
        self.name = name
        self.clients = -1
        self.connections = -1
        self.timestamp = int(time.time())
        self.metric_readerrors = 0

        self.clients = getValue(info, "Active :", 2)
        self.connections = len(connections)
        if (self.clients == -1):
            self.metric_readerrors += 1
        if (self.connections == -1):
            self.metric_readerrors += 1
        return

    def metrics(self):
        metrics = []
        if (self.clients >= 0):
            metrics.append(Metric('dcache.door.xrootd.' + self.name + '.clients', self.clients, self.timestamp))
        if (self.connections >= 0):
            metrics.append(Metric('dcache.door.xrootd.' + self.name + '.connections', self.connections, self.timestamp))
        metrics.append(Metric('dcache.door.xrootd.' + self.name + '.metric_errors', self.metric_readerrors, self.timestamp))
        return metrics


class FTPDoorInfo:
    def __init__(self, name, info):
        self.name = name
        self.clients = -1
        self.timestamp = int(time.time())
        self.metric_readerrors = 0

        a = getValue(info, "Logins/max     :", 2)
        self.clients = getElement(a, 0, "/")
        if (self.clients == -1):
            self.metric_readerrors += 1
        return

    def metrics(self):
        metrics = []
        if (self.clients >= 0):
            metrics.append(Metric('dcache.door.gftp.' + self.name + '.clients', self.clients, self.timestamp))
        metrics.append(Metric('dcache.door.gftp.' + self.name + '.metric_errors', self.metric_readerrors, self.timestamp))
        return metrics



class DCacheGraphite:
    def __init__(self, adminHost, carbonServer):
        self.adminConsole = pexpect.spawn('ssh -l admin -p 22224 127.0.0.1')
        self.adminHost = adminHost
        self.carbonServer = carbonServer
        self.pools = []
        self.poolgroups = []
        self.metrics = []
        self.nfsDoorInfo = 0
        self.xrootdDoorInfo = 0
        self.ftpDoorInfo = 0

        self.adminConsole.expect([pexpect.TIMEOUT, '\[<=' + self.adminHost + '=>\] \('], timeout=10)
        self.adminConsole.expect([pexpect.TIMEOUT, '> '], timeout=10)
        return

    def close(self):
        self.adminConsole.sendline('\q')
        return

    def sendMetrics(self, tuples):
        payload = pickle.dumps(tuples, protocol=2)
        header = struct.pack("!L", len(payload))
        self.sock.sendall(header)
        self.sock.sendall(payload)
        return

    def sendAllMetrics(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.carbonServer, 2004))
        tuples = ([])
        count = 0
        for i in self.metrics:
            tuples.append((i.name, (i.timestamp, i.value)))
            count += 1
            if (count == 200):
                self.sendMetrics(tuples)
                count = 0
                tuples = ([])
                time.sleep(0.1)
        if (count > 0):
            self.sendMetrics(tuples)
        self.sock.close()
        return

    def printMetrics(self):
        for i in self.metrics:
            print i.name, i.value, i.timestamp
        return

    def getOutput(self):
        self.adminConsole.expect([pexpect.TIMEOUT, '\[<=' + self.adminHost + '=>\] \('], timeout=10)
        output = self.adminConsole.before
        self.adminConsole.expect([pexpect.TIMEOUT, '> '], timeout=10)
        lines = re.split('\n\r', output)
        if (lines):
            lines.pop(0)
        if (lines):
            lines.pop()
        if (lines and lines[len(lines)-1].strip() == ""):
            lines.pop()
        return lines

    def getStringOutput(self):
        lines = self.getOutput()
        output = ""
        for l in lines:
            if (l != ""):
                output = output + l + "\n"
        return output

    def getMetrics(self):
        self.getDoors()
        self.getPools()
        self.getPoolGroups()
        self.getNFSDoor()
        self.getXrootdDoor()
        self.getFTPDoor()

        self.metrics = []
        for i in self.pools:
            m = i.metrics()
            for j in m:
                self.metrics.append(j)

        for i in self.poolgroups:
            m = i.metrics()
            for j in m:
                self.metrics.append(j)
        m = self.nfsDoorInfo.metrics()
        for j in m:
            self.metrics.append(j)
        m = self.xrootdDoorInfo.metrics()
        for j in m:
            self.metrics.append(j)
        m = self.ftpDoorInfo.metrics()
        for j in m:
            self.metrics.append(j)
        return

    def getDoors(self):
        self.adminConsole.sendline('\c info')
        self.getOutput()
        self.adminConsole.sendline('state output xml')
        self.getOutput()
        self.adminConsole.sendline('state ls doors')
        xmldoc = minidom.parseString(self.getStringOutput())
        doors = xmldoc.getElementsByTagName('door')
        for door in doors:
            metrics = door.getElementsByTagName('metric')
            for metric in metrics:
                name = metric.getAttribute('name')
                if (name == "cell"):
                    door_name = metric.firstChild.nodeValue
            protocols = door.getElementsByTagName('protocol')
            for protocol in protocols:
                metrics = protocol.getElementsByTagName('metric')
                for metric in metrics:
                    name = metric.getAttribute('name')
                    if (name == "family"):
                        type = metric.firstChild.nodeValue
                        if type == "gsiftp":
                            self.ftpDoorName = door_name
                        elif type == "file":
                            self.nfsDoorName = door_name
                        elif type == "root":
                            self.xrootdDoorName = door_name
        return

    def getPools(self):
        self.pools = []
        self.adminConsole.sendline('\c info')
        self.getOutput()
        self.adminConsole.sendline('state output xml')
        self.getOutput()
        self.adminConsole.sendline('state ls pools')
        xmldoc = minidom.parseString(self.getStringOutput())
        pools = xmldoc.getElementsByTagName('pool')
        for pool in pools:
            self.pools.append(PoolInfo(pool))
        return

    def getPoolGroups(self):
        self.poolgroups = []
        self.adminConsole.sendline('\c info')
        self.getOutput()
        self.adminConsole.sendline('state output xml')
        self.getOutput()
        self.adminConsole.sendline('state ls poolgroups')
        xmldoc = minidom.parseString(self.getStringOutput())
        pools = xmldoc.getElementsByTagName('poolgroup')
        for poolgroup in pools:
            self.pools.append(PoolGroupInfo(poolgroup, self.pools))
        return

    def getNFSDoor(self):
        self.adminConsole.sendline('\c ' + self.nfsDoorName)
        self.getOutput()
        self.adminConsole.sendline('info')
        info = self.getOutput()
        self.adminConsole.sendline('show transfers')
        transfers = self.getOutput()
        self.nfsDoorInfo = NFSDoorInfo(self.nfsDoorName, info, transfers)
        return

    def getXrootdDoor(self):
        self.adminConsole.sendline('\c ' + self.xrootdDoorName)
        self.getOutput()
        self.adminConsole.sendline('info')
        info = self.getOutput()
        self.adminConsole.sendline('connections')
        connections = self.getOutput()
        self.xrootdDoorInfo = XrootdDoorInfo(self.xrootdDoorName, info, connections)
        return

    def getFTPDoor(self):
        self.adminConsole.sendline('\c ' + self.ftpDoorName)
        self.getOutput()
        self.adminConsole.sendline('info')
        info = self.getOutput()
        self.ftpDoorInfo = FTPDoorInfo(self.ftpDoorName, info)
        return


dcacheGraphite = DCacheGraphite("{{ grains.host }}", "{{ dcache.graphite_monitoring.carbon_server }}")
dcacheGraphite.getMetrics()
#dcacheGraphite.printMetrics()
dcacheGraphite.sendAllMetrics()
#print 'Metrics sent:', len(dcacheGraphite.metrics)
dcacheGraphite.close()
