

#author: june


import os
import re
#from prettytable import PrettyTable
from abstracttool import Tool
from sqlite3Util import Sqlite3Util
from iosCertTrustManager import *
import globals as G


########################################################################
class CertficateUtil(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, sshopt):
        """Constructor"""
        super(self.__class__, self).__init__()
        self.sshopt = sshopt
        self.trust_store_path = '/private/var/Keychains/TrustStore.sqlite3'
        self.local_store_path = self.tmp_path() + 'device/TrustStore.sqlite3'
        self.CA_list = {}
        
        
    #----------------------------------------------------------------------
    def install_burp_cert(self):
        """"""
        if self.tool_path.has_key('uiopen'):
            tool = self.tool_path['uiopen']
        elif self.tool_path.has_key('openurl'):
            tool = self.tool_path['openurl']
        elif self.tool_path.has_key('openURL'):
            tool = self.tool_path['openURL']
        else:
            return False
        
        cmd = "%s %s" % (tool, 'http://burp/cert')
        self.sshopt.ssh_exec(cmd)
        return True
    
    
    #----------------------------------------------------------------------
    def list_certs(self):
        """"""
        if os.path.exists(self.local_store_path):
            try:
                os.remove(self.local_store_path)
            except OSError:
                return None
        
        path = self.sshopt.cache_file(self.trust_store_path, self.local_store_path)
        
        store = TrustStore(path)
        
        '''
        result = PrettyTable(["ID", "subject", "issuer", "notBefore", "notAfter"])
        
        result.align["subject"] = "l"
        result.align["issuer"] = "l"
        #result.align["notBefore"] = "l"
        #result.align["notAfter"] = "l"
        '''
        
        
        res = ''
        
        l = store.list_certificates()
        for i in range(len(l)):
            e = l[i]
            self.CA_list[str(i)] = e
            attr = filter(None, str(e).split('\n'))
            if len(attr) != 4:
                G.log(G.INFO, 'Not a standard CA cert.')
                continue
            subject = attr[0]
            issuer = attr[1]
            not_before = attr[2]
            not_after = attr[3]
            
            res += ('Num: ' + str(i) + '\n')
            res += ('subject: ' + re.sub(", ", "\n\t", subject.split('subject= ')[1]) + '\n')
            res += ('issuer: ' + re.sub(", ", "\n\t", issuer.split('issuer= ')[1]) + '\n')
            res += ('not_before: ' + not_before.split('notBefore=')[1] + '\n')
            res += ('not_after: ' + not_after.split('notAfter=')[1] + '\n')
            res += '\n'
            
            '''
            result.add_row([str(i), 
                            re.sub("=", ":", re.sub(", ", "\n", subject.split('subject= ')[1])),
                            re.sub("=", ":", re.sub(", ", "\n", issuer.split('issuer= ')[1])),
                            not_before.split('notBefore=')[1],
                            not_after.split('notAfter=')[1]])
            '''
            
            
            
        return res
    
    
    #----------------------------------------------------------------------
    def delete_cert(self, cert_id):
        """"""
        #if CA list is None, select first
        if self.CA_list == {}:
            self.list_certs()
        
        #if id not in range, return error no.
        if not self.CA_list.has_key(cert_id):
            G.log(G.INFO, 'Cert ID:{} not in range.'.format(cert_id))
            return False
        
        #delete local sqlite
        cert = self.CA_list[cert_id]
        store = TrustStore(self.local_store_path)
        r = store.delete_cert_by_subject(cert)
        
        if r == False:
            return False
        
        #delete local success, async sqlite to device
        self.sshopt.minisftp.putfile(self.trust_store_path, self.local_store_path, None)

        return True
    
    
    #----------------------------------------------------------------------
    def add_cert(self, certificate_filepath, truststore_filepath=None):
        """"""
        if not os.path.exists(self.local_store_path):
            store_path = self.sshopt.cache_file(self.trust_store_path, self.local_store_path)        

        cert = Certificate()
        #if pem type file, use load PEM method
        if certificate_filepath.find('.pem') != -1:
            cert.load_PEMfile(certificate_filepath)
        else:
            #defaults DER file
            cert.load_DERfile(certificate_filepath)
        print cert.get_subject()

        if truststore_filepath is None:
            truststore_filepath = self.local_store_path
        
        if truststore_filepath:
            if query_yes_no("Import certificate to " + 'device', "no") == "yes":
                tstore = TrustStore(truststore_filepath)
                tstore.add_certificate(cert)
                
        self.sshopt.minisftp.putfile(self.trust_store_path, truststore_filepath, None)
        
        return True
    
    
    #----------------------------------------------------------------------
    def export_cert(self, path):
        """"""
        if not os.path.exists(self.local_store_path):
            store_path = self.sshopt.cache_file(self.trust_store_path, self.local_store_path)

        store = TrustStore(self.local_store_path)
        
        store.export_certificates(path)
        
        return True