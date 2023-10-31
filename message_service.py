#!/usr/bin/python
#coding=utf-8

'''This script is to send message for phone.
'''
import random
import sys
import os
import re
import math
import string
import json
import MySQLdb
import traceback
import urllib
#import httplib2
import time
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from twisted.python import logfile

sys.path.insert(0, '.')
reload(sys)
sys.setdefaultencoding("utf-8")

class TestResource(resource.Resource):
    isLeaf = True#key important.Delete it will cause ERROR
    def render_GET(self, request):
        request.setHeader("content-type", "application/json; charset=UTF-8")
        #print request.path
        #print request.uri
        start_time = int(time.time() * 1000)
        if request.path == "/warn_messages":
            params_dict = self.parse_request(request)
            phone_str = params_dict.get('p', '1')
            url_msgg = params_dict.get('m', '')
            msgg_unicode = urllib.unquote(url_msgg)
            msgg = msgg_unicode.encode('gbk')
            self.send_message(phone_str, msgg)
            consume_time = int(time.time() * 1000) - start_time
            result = "phone:" + phone_str, "msgg:" + msgg
            self.print_log(str(request.uri) + "\t" + str(result), consume_time)
            if "callback" in params_dict:
                return self.add_callback(params_dict["callback"], result)
            return result

    def parse_request(self, request):
        qs = ''
        params = []
        qindex = request.uri.find('?')
        params_dict = {}
        if qindex != -1:
            qs = request.uri[qindex + 1:]
            params = qs.split('&')
            for param in params:
                pindex = param.find('=')
                if pindex != -1:
                    key, value = param.split('=')
                    params_dict[key] = value
        print(params_dict)
        return params_dict

    def send_message(self, phone_str, msgg):
        phone_list = phone_str.split(';')
        for phone in phone_list:
            cmd = "GET -edst 5 'http://115.182.51.124:7070/thirdPartner/letvqxtmt?corpID=800070&srcAddr=1069032901305724&destAddr=%s&msg=%s'" %(phone,msgg)
            os.system(cmd)
            print("send message done")

    def add_callback(self, callback_function, json_result):
        return "%s(%s)" %(callback_function, json_result)

    def print_log(self, message, consume_time):
        print("message:%s\ttime:%d" % (message, consume_time))

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print >> sys.stderr, "Usage : %s ip port log_file log_folder" % sys.argv[0]
        sys.exit(1)
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    log_file = sys.argv[3]
    log_folder = sys.argv[4]
    data_access_log_file = logfile.DailyLogFile(log_file, log_folder)
    log.startLogging(data_access_log_file)
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(server_port, server.Site(TestResource()))
    reactor.run()
