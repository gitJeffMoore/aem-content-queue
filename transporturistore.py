import sys, os
#Write the current transportUri value to a file for future use
def StoreTransportUri(uri, replicationagent):
    fileName = "%s_transportUri_store.txt" % (replicationagent)
    print 'Creating %s...' % fileName
    transportStore = open(fileName,"w")
    print '%s created' % fileName
    transportStore.write(uri);
    print '%s written to file' % uri
    transportStore.close()
#Retrieve the Uri value previously stored by the aem-content-queue script
def RetrieveTransportUri(replicationagent):
    print 'Opening %s_transportUri_store.txt' % (replicationagent)
    fileName = "%s_transportUri_store.txt" % (replicationagent)
    #Open the file in read only
    transportStore = open(fileName,"r")
    #Read the file. There should only be one value in it
    storedValue = transportStore.read()
    return storedValue
#Delete the file after use
def DeleteTransportUriStore(replicationagent):
    fileName = "%s_transportUri_store.txt" % (replicationagent)
    print 'Deleting %s' % (fileName)
    os.remove(fileName)