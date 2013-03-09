#!//usr/bin/python

""""
    quick rabbitmq end to end test perf data plugin
"""


import socket
import argparse
import sys
import csv
from pprint import pprint
import re
import pika
import logging
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--publish', help="publish a string",
        dest="publish")
    parser.add_argument('-c', '--consume', help="empty a queue ",
        dest="consume")
    parser.add_argument('-i', '--iterations', help="how many items to publish",
        dest="iterations", type=int)

    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger('pika').setLevel(logging.ERROR)


    """ do action on argument """
    if args.publish and args.consume:
        print "Error: use publish and consume independently"
        return 2

    if args.publish:

        iterations = 100 if not args.iterations else args.iterations
        params = {}

        fields = { 'eventbus_test' : True, 'x-match': 'all' }

        con = pika.BlockingConnection(pika.ConnectionParameters('prod-rabbit-02'))
        channel = con.channel()
        channel.queue_declare(queue='test',durable=True,arguments=params)

        for num in range(0, iterations):
            #channel.basic_publish(exchange='eventbus.headers',routing_key='test',body=args.publish)
            channel.basic_publish(exchange='eventbus.headers',routing_key='',body=args.publish,
                properties=pika.BasicProperties(headers = fields))

        con.close()
        return 0


    if args.consume:

        iterations = 100 if not args.iterations else args.iterations
        con = pika.BlockingConnection(pika.ConnectionParameters('prod-rabbit-02'))
        channel = con.channel()
        i = 0

        print "Consuming on %s, Ctrl+C to exit" % args.consume

        time.sleep(1)

        try:

            for num in range(0, iterations):
                b = channel.basic_get(args.consume, no_ack=True)
                #print "iteration %s: message body: %s" % (i, b)
                #channel.basic_ack(m.delivery_tag)
                i = i + 1

        except KeyboardInterrupt:

            print "\nExiting"

        channel.close()
        con.close()

 



if __name__ == "__main__":
    sys.exit(main())
