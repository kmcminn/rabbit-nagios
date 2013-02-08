#!/usr/bin/env /usr/bin/python  
  
from optparse import OptionParser  
import urllib2  
import json  
from pprint import pprint
import time  
import datetime  
  
def getOptions():  
    arguments = OptionParser()  
    arguments.add_option("--host", dest="host", help="Host rabbitmq is running on", type="string", default="localhost")  
    arguments.add_option("--queue", dest="queue", help="Name of the queue in inspect", type="string", default="celery")  
    arguments.add_option("--username", dest="username", help="RabbitMQ API username", type="string", default="guest")  
    arguments.add_option("--password", dest="password", help="RabbitMQ API password", type="string", default="guest")  
    arguments.add_option("--port", dest="port", help="RabbitMQ API port", type="string", default="15672")  
    arguments.add_option("--vhost", dest="vhost", help="RabbitMQ vhost", type="string", default='%2F')
      
    arguments.add_option("--warning-queue-size", dest="warn_queue", help="Size of the queue to alert as warning", type="int", default=10000)  
    arguments.add_option("--critical-queue-size", dest="crit_queue", help="Size of the queue to alert as critical", type="int", default=20000)  
  
    arguments.add_option("--warning-seconds", dest="warn_seconds", help="Last event processes in seconds ago to alert as warning", type="int", default=3600)  
    arguments.add_option("--critical-seconds", dest="crit_seconds", help="Last event processes in seconds ago to alert as critical", type="int", default=14400)  
          
    return arguments.parse_args()[0]  

def doApiGet(a, u, p):
    # handle HTTP Auth
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    top_level_url = a
    password_mgr.add_password(None, top_level_url, u, p)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)

    response = None
    try:
        request = opener.open(url)
        response = request.read()
        request.close()
    except urllib2.HTTPError, e:
        print "Error code %s hitting %s" % (e.code, url)
        return False

    return response

  
if __name__ == '__main__':  
      
    options = getOptions()      
      
    url = "http://%s:%s/api/queues/%s/%s" % (options.host, options.port, options.vhost, options.queue)  
      
    content = doApiGet(url, options.username, options.password)
          
    data = json.loads(content)  
      
    pprint(data)  
      
    num_messages = data.get("messages")  
    if num_messages > options.crit_queue or num_messages > options.warn_queue:  
        print "%s messages in %s queue" % (num_messages, options.queue)  
        exit(1 if num_messages > options.crit_queue else 2)   
      
    message_stats = data.get("message_stats")  
    deliver_details = message_stats.get("deliver_details")  
    rate = deliver_details.get("rate")  
      
    #1309542487   
    #1309548601517      
    last_event = deliver_details.get("last_event") / 1000  
    last_event_time = time.ctime(last_event)  
      
    #diff = abs(last_event_time - datetime.datetime.today())  
    #last_event_time_diff_seconds = diff.seconds + diff.days * 86400  
    last_event_time_diff_seconds = abs(last_event - int(time.time()))  
    if last_event_time_diff_seconds > options.crit_seconds or last_event_time_diff_seconds > options.warn_seconds:  
        print "%s seconds since last event consumed on %s" % (last_event_time_diff_seconds, options.queue)  
        exit(1 if last_event_time_diff_seconds > options.crit_seconds else 2)  
      
    print "Last event consumed: %s" % last_event_time
