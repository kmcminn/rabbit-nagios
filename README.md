rabbit-nagios
=============
more simpler nagios plugin for the rabbit mgmt api. a continuation/refinemant from Chase Seibert's work here http://chase-seibert.github.com/blog/2011/07/01/checking-rabbitmq-queue-sizeage-with-nagios.html


### Install ###
```
$ git clone https://github.com/kmcminn/rabbit-nagios.git && cp rabbit-nagios/rabbitmq-nagios.py /usr/lib/nagios/plugins/
```
### Usage ###
The plugin can be used as command line tool or a python module for getting stats

```
Usage: rabbitmq-nagios.py [options]

Options:
  -h, --help            show this help message and exit
  --host=HOST           Host rabbitmq is running on
  --queue=QUEUE         Name of the queue in inspect
  --username=USERNAME   RabbitMQ API username
  --password=PASSWORD   RabbitMQ API password
  --port=PORT           RabbitMQ API port
  --vhost=VHOST         RabbitMQ vhost
  --warning-queue-size=WARN_QUEUE
                        Size of the queue to alert as warning
  --critical-queue-size=CRIT_QUEUE
                        Size of the queue to alert as critical
  --warning-seconds=WARN_SECONDS
                        Last event processes in seconds ago to alert as
                        warning
  --critical-seconds=CRIT_SECONDS
                        Last event processes in seconds ago to alert as
                        critical
```
