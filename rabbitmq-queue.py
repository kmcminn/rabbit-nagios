#!/usr/bin/env /usr/bin/python

from optparse import OptionParser
import urllib2
import json
from pprint import pprint
from pynagios import Plugin, make_option
import time
import datetime


class RabbitQueueCheck(Plugin):
    """
    performs a nagios compliant check on a single queue and
    attempts to catch all errors. expected usage is with a critical threshold of 0
    """

    username = make_option("--username", dest="username", help="RabbitMQ API username", type="string", default="guest")
    password = make_option("--password", dest="password", help="RabbitMQ API password", type="string", default="guest")
    port = make_option("--port", dest="port", help="RabbitMQ API port", type="string", default="15672")
    vhost = make_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')
    queue = make_option("--queue", dest="queue", help="Name of the queue in inspect", type="string", default="queue")

    def doApiGet(self):
        """
        performs and returns content from an api get
        """
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.url, self.options.username, self.options.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)

        response = None
        try:
            request = opener.open(self.url)
            response = request.read()
            request.close()
        except Exception, e:
            response = False
            self.rabbit_error = 2
            self.rabbit_note = "problem with api get:", e

        return response

    def makeQueueUrl(self):
        """
        forms self.url, a correct url to polling a rabbit queue
        """
        try:
            self.url = "http://%s:%s/api/queues/%s/%s" % (self.options.hostname,
                       self.options.port, self.options.vhost, self.options.queue)
            return True
        except Exception, e:
            self.rabbit_error = 3
            self.rabbit_note = "problem forming api url:", e
            return False

    def testOptions(self):
        """
        returns false if necessary options aren't present
        """

        if not self.options.hostname or not self.options.port \
                or not self.options.vhost or not self.options.queue:

            return False

        return True

    def quickExit(self, v):
        """
        zero out the perf data and return
        """

        result = self.response_for_value(v, m)

        if not self.options.queue:
            queue = 'queue'
        else:
            queue = self.options.queue

        result.set_perf_data(queue + "_messages", 0)
        result.set_perf_data(queue + "_rate", 0)
        result.set_perf_data(queue + "_consumers", 0)
        result.set_perf_data("rabbit_error", self.rabbit_error)
        result.message = self.rabbit_note

        return result

    def parseJson(self, response):
        """
        parse test and return api json
        """
        try:
            data = json.loads(response)
        except Exception, e:
            data = None
            self.rabbit_error = 4
            self.rabbit_note = "problem with json parse:", e

        return data

    def check(self):
        """
        returns a response and perf data for this check
        """

        self.rabbit_error = 0
        self.rabbit_note = "action performed successfully"

        if not self.testOptions():
            return self.quickExit(255)

        if not self.makeQueueUrl():
            return self.quickExit(255)

        response = self.doApiGet()

        if self.rabbit_error > 0:
            return self.quickExit(255)

        data = self.parseJson(response)

        if self.rabbit_error > 0:
            return self.quickExit(255)

        queue = self.options.queue

        result = self.response_for_value(self.rabbit_error)
        result.set_perf_data(queue + "_messages", data['messages'])
        result.set_perf_data(queue + "_rate", data['messages_details']['rate'])
        result.set_perf_data(queue + "_consumers", data['consumers'])
        result.set_perf_data("rabbit_error", self.rabbit_error)
        result.message = self.rabbit_note

        return result


if __name__ == "__main__":

    obj = RabbitQueueCheck()
    obj.check().exit()
