import sys, os, requests, optparse, transporturistore
'''
This script is used to enable content replication on a previously queued AEM replication agent by retrieving
the original value from a file and deleting the file once complete.
It is intended to be called from the command line or a orchestration tool like Jenkins.
The use case is when performing a code deployment to a multi author/publish server environment while content 
Authoring is occurring in parallel.

Sample replication agent: publish
Sample TransportURI value: http://localhost:4503/bin/receive?sling:authRequestLogin=1
Sample call aem-content-enable.py -a publish -e  http://localhost:4502 -u admin -p admin -c C:\certificate.cer
'''

#Custom Exception to raise on non fatal errors
class Failure(Exception):
    def __init__(self, msg):
        self.msg = msg

#Enable the replication agent
def EnableContent(replicationagent, environment, username, password, certificate):
    #Create the URL used to access the replication agent.  The assumption is that this is an Author Instance
    jsonUrl = environment + '/etc/replication/agents.author/' + replicationagent + '/jcr:content/.json'
    try:
        print 'Retrieving correct transport uri value....'
        transportUri = transporturistore.RetrieveTransportUri(replicationagent)
        if transportUri:
            print 'Transport URI is %s' % transportUri
            print 'Enable Content on %s ...' % (jsonUrl)
            payload = {'transportUri': transportUri}
            response = requests.post(jsonUrl, auth=(username, password), verify=certificate, data=payload)
            if response.status_code != 200:
                raise Failure('Failure enabling content replication. %s %s' % (response.status_code, response.reason))
            else:
                jsonResponse = requests.get(jsonUrl, auth=(username, password))
                data = jsonResponse.json()
                #Check to make sure the transportUri is what we expect
                correctTransportUri = data['transportUri']
                if correctTransportUri == transportUri:
                    print 'Content has successfully been enabled. TransportUri = %s' % transportUri
                    #Clean up
                    transporturistore.DeleteTransportUriStore(replicationagent)
                else:
                    raise Failure('Transport Uri does not match what is expected.')
                response.close()
        else:
            raise Failure('There is not a stored transport Uri Value')
    except Failure, e:
        print e.msg
        return 1
    except requests.exceptions.ConnectionError, e:
        print 'ConnectionError %s' % (e, )
    except Exception, e:
        print 'Error: %s' % (e.args, )

def main(argv):
        parser = optparse.OptionParser(description="Sample call: aem-content-enable.py -a publish -e  http://localhost:4502 -u admin -p admin -c C:\certificate.cer")
        parser.add_option("--replicationagent", "-a", dest="replicationagent", default="", help="Replication Agent")
        parser.add_option("--environment", "-e", dest="environment", default="", help="Author Environment")
        parser.add_option("--username", "-u", dest="username", default="", help="Username")
        parser.add_option("--password", "-p", dest="password", default="", help="Password")
        parser.add_option("--certificate", "-c", dest="certificate", default="", help="Certificate")
        (options, args) = parser.parse_args()
        return EnableContent(options.replicationagent, options.environment, options.username, options.password, options.certificate)

if __name__ == "__main__":
   sys.exit(main(sys))