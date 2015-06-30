import sys, requests, optparse, transporturistore
'''
This script is used to queue content replication on an AEM replication agent by storing the
current transportUri and pointing it to a temporary dummy endpoint.  It is intended to be
called from the command line or an orchestration tool like Jenkins.  The use case is when 
performing a code deployment to a multi author/publish server environment while content 
Authoring is occurring in parallel.

Sample replication agent: publish
Sample TransportURI value: http://localhost:4503/bin/receive?sling:authRequestLogin=1
Sample call aem-content-queue.py -a publish -e  http://localhost:4502 -u admin -p admin -c C:\certificate.cer
'''

#Custom Exception to raise on non fatal errors
class Failure(Exception):
    def __init__(self, msg):
        self.msg = msg

#Queue any content
def QueueContent(replicationagent, environment, username, password, certificate):
    #Create the URL used to access the replication agent.  The assumption is that this is an Author Instance
    jsonUrl = environment + '/etc/replication/agents.author/' + replicationagent + '/jcr:content/.json'
    #Get the current transportUri value and store it for future use
    print 'Getting current transport uri value from %s' % jsonUrl
    jsonResponse = requests.get(jsonUrl, auth=(username, password))
    print 'Response status code: %s' % jsonResponse.status_code
    data = jsonResponse.json()
    if not data.get('transportUri'):
        raise Failure('No transportUri node found. Exiting program...')
    elif data['transportUri'] == 'fake':
        raise Failure('Current transportUri value is: %s. Exiting Program...' % data['transportUri'])
    transportUri = data['transportUri']
    print 'Transport URI: %s ' % transportUri
    transporturistore.StoreTransportUri(transportUri, replicationagent)
    #Queue Content.  We do this by setting the transportUri to a temporary dummy value.
    print 'Queuing Content on %s ...' % (jsonUrl)
    payload = {'transportUri': 'fake'}
    response = requests.post(jsonUrl, auth=(username, password), verify=certificate, data=payload)
    if response.status_code != 200:
        raise Failure('Failure queuing content. %s %s' % (response.status_code, response.reason))
    else:
        jsonResponse = requests.get(jsonUrl, auth=(username, password))
        data = jsonResponse.json()
        transportUri = data['transportUri']
        if transportUri == 'fake':
            print 'Content has successfully been queued. TransportUri = %s' % transportUri
        else:
            print 'Transport Uri does not match what is expected. TransportUri = %s' % transportUri'
        response.close()
def main(argv):
    try:
        parser = optparse.OptionParser(description="Sample call: aem-content-queue.py -a publish -e  http://localhost:4502 -u admin -p admin -c C:\certificate.cer")
        parser.add_option("--replicationagent", "-a", dest="replicationagent", default="", help="Replication Agent")
        parser.add_option("--environment", "-e", dest="environment", default="", help="Author Environment")
        parser.add_option("--username", "-u", dest="username", default="", help="Username")
        parser.add_option("--password", "-p", dest="password", default="", help="Password")
        parser.add_option("--certificate", "-c", dest="certificate", default="", help="Certificate")
        (options, args) = parser.parse_args()
        QueueContent(options.replicationagent, options.environment, options.username, options.password, options.certificate)
    except Failure, e:
        print e.msg
        return 1
    except requests.exceptions.ConnectionError, e:
        print 'ConnectionError %s' % (e, )
        return 1
    except Exception, e:
        print 'Error: %s' % (e.args, )
        return 1
if __name__ == "__main__":
   sys.exit(main(sys))