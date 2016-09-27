


#author: june


from abstracttool import Tool
import json
import base64
import binascii
import re
import tempfile
#from prettytable import PrettyTable
from PlistUtil import PlistUtil


########################################################################
class KeychainUtil(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, sshopt):
        """Constructor"""
        super(self.__class__, self).__init__()
        self.sshopt = sshopt
        self.data = None
        
        
    #----------------------------------------------------------------------
    def dump(self):
        """"""
        #keychaineditor --action dump
        if not self.tool_path.has_key("keychaineditor"):
            return None
        
        if not self.sshopt.file_exists(self.tool_path['keychaineditor']):
            return None
        
        
        cmd = "{} --action dump".format(self.tool_path['keychaineditor'])
        #json.dumps(self.sshopt.ssh_exec(cmd))
        
        try:
            self.data = json.loads(''.join(self.sshopt.ssh_exec(cmd)))
        except ValueError, e:        
            self.data = None
            
        return self.data
    
    

    #----------------------------------------------------------------------
    def parse0x0D_XML(self, inStr):
        """"""
        if str(inStr).find('\n') != -1:
            if str(inStr).startswith('<?xml') != -1:
                return 'Plist file'
        return inStr
    
    
    #----------------------------------------------------------------------
    def parse(self):
        """"""
        self.dump()
        
        if self.data is None:
            return None
        
        '''
        #result = "ID\tEntitlementGroup    \tAccount    \tService    \tProtection    \tUserPresence    \tCreation Time    \tModified Time\n"

        result = PrettyTable(["ID", "EntitlementGroup", "Account", "Service", "Protection", "UserPresence", "Creation Time", "Modified Time", "Data", "Base64(Data)"])
        #result.align["ID"] = "l"# Left align 
        result.align["EntitlementGroup"] = "l"
        result.align["Account"] = "l"
        result.align["Service"] = "l"
        result.align["Protection"] = "l"
        #result.align["UserPresence"] = "l"
        #result.align["Creation Time"] = "l"
        #result.align["Modified Time"] = "l"
        result.align["Data"] = "l"
        result.align["Base64(Data)"] = "l"
        '''
        
        res = ''
        
        for i in range(len(self.data)):
            k = i+1
            record = self.data[str(k)]
            EntitlementGroup = record['EntitlementGroup'].encode("utf-8").strip() 
            Account = record['Account'].encode("utf-8").strip() 
            Service = record['Service'].encode("utf-8").strip() 
            Protection = record['Protection'].encode("utf-8").strip() 
            UserPresence = record['UserPresence'].encode("utf-8").strip() 
            Creation = record['Creation Time'].encode("utf-8").strip() 
            Modified = record['Modified Time'].encode("utf-8").strip() 
            Data = record['Data'].encode("utf-8").strip()
            #t = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
            #print '==>', isinstance(record['Data'], str)
            #print '==>', isinstance(record['Data'], unicode)
            #print '==>', isinstance(record['Data'], basestring)
            base64Data = base64.decodestring(Data)
            
            if str(base64Data).startswith('bplist'):
                #plist file, should show plist?!
                with tempfile.NamedTemporaryFile() as temp:
                    temp.write(base64Data)
                    temp.flush()
                    plist_obj = PlistUtil(temp.name)
                    temp.seek(0)
                    #got plist file content, not print yet
                    content = ''
                    for line in temp.readlines():
                        content += line                 
                    temp.close()
                    
                #base64Data = content
                base64Data = "<Plist file>"
            else:
                #printable charector?
                canPrintFlag = True #default true
                for j in range(len(base64Data)):
                    c = ord(base64Data[j])
                    if c < 32 or c > 126:
                        canPrintFlag = False
                        break;
                    
            
            res += ('Num: ' + str(k).encode("utf-8").strip() + '\n')
            res += ('EntitlementGroup: ' + self.parse0x0D_XML(EntitlementGroup) + '\n')
            res += ('Account: ' + self.parse0x0D_XML(Account) + '\n')
            res += ('Service: ' + self.parse0x0D_XML(Service) + '\n')
            res += ('Protection: ' + self.parse0x0D_XML(Protection) + '\n')
            res += ('UserPresence: ' + self.parse0x0D_XML(UserPresence) + '\n')
            res += ('Creation: ' + self.parse0x0D_XML(Creation) + '\n')
            res += ('Modified: ' + self.parse0x0D_XML(Modified) + '\n')
            res += ('Data: ' + Data + '\n')
            res += ('base64Data: ' + (base64Data if canPrintFlag else '') + '\n')
            res += '\n'
            
            
            '''
            result.add_row([str(k).encode("utf-8").strip(), 
                      self.parse0x0D_XML(EntitlementGroup),
                      self.parse0x0D_XML(Account),
                      self.parse0x0D_XML(Service),
                      self.parse0x0D_XML(Protection),
                      self.parse0x0D_XML(UserPresence),
                      self.parse0x0D_XML(Creation),
                      self.parse0x0D_XML(Modified),
                      Data,
                      (base64Data if canPrintFlag else '')])
            '''
        
        return res
    
    
    #----------------------------------------------------------------------
    def delete_by_asg(self, account, service, agroup):
        """"""
        cmd = "{} --action delete --account \"{}\" --service \"{}\" --agroup \"{}\"".format(self.tool_path['keychaineditor'], account, service, agroup)
        
        return self.sshopt.ssh_exec(cmd)
    
    
    #----------------------------------------------------------------------
    def delete_by_ID(self, dataID):
        """"""
        if self.data is None:
            self.dump()
        
        if self.data is None:
            return False        
        
        record = self.data[str(dataID)]
        if record is None:
            return False
        
        account = record['Account'].encode("utf-8").strip() 
        service = record['Service'].encode("utf-8").strip()
        agroup = record['EntitlementGroup'].encode("utf-8").strip()
        
        result = self.delete_by_asg(account, service, agroup)
        
        if str(result).find('Operation successfully completed.') != -1:
            return True
        else:
            return False        


    #----------------------------------------------------------------------
    def edit_by_asg(self, account, service, agroup, newData):
        """"""
        cmd = "{} --action edit --account \"{}\" --service \"{}\" --agroup \"{}\" --data \"{}\"".format(self.tool_path['keychaineditor'], account, service, agroup, newData)
        
        return self.sshopt.ssh_exec(cmd)     
        
    
    #----------------------------------------------------------------------
    def edit_by_id(self, dataID, newData, with_base64=False):
        """"""
        if self.data is None:
            self.dump()
            
        if self.data is None:
            return False        
    
        record = self.data[str(dataID)]
        if record is None:
            return False
    
        account = record['Account'].encode("utf-8").strip() 
        service = record['Service'].encode("utf-8").strip()
        agroup = record['EntitlementGroup'].encode("utf-8").strip()
        
        if with_base64 == False:
            result = self.edit_by_asg(account, service, agroup, base64.encodestring(newData))
        else:
            result = self.edit_by_asg(account, service, agroup, newData)
            
        if str(result).find('Operation successfully completed.') != -1:
            return True
        else:
            return False
        
        
    #----------------------------------------------------------------------
    def grep_keychain(self, pattern):
        """"""
        if self.data is None:
            self.dump()
            
        if self.data is None:
            return None
        
        '''
        result = PrettyTable(["ID", "EntitlementGroup", "Account", "Service", "Protection", "UserPresence", "Creation Time", "Modified Time", "Data", "Base64(Data)"])
        #result.align["ID"] = "l"# Left align 
        result.align["EntitlementGroup"] = "l"
        result.align["Account"] = "l"
        result.align["Service"] = "l"
        result.align["Protection"] = "l"
        #result.align["UserPresence"] = "l"
        #result.align["Creation Time"] = "l"
        #result.align["Modified Time"] = "l"
        result.align["Data"] = "l"
        result.align["Base64(Data)"] = "l"
        '''
        
        res = ''
        
        for i in range(len(self.data)):
            k = i+1
            
            record = self.data[str(k)]
            EntitlementGroup = record['EntitlementGroup'].encode("utf-8").strip() 
            Account = record['Account'].encode("utf-8").strip() 
            Service = record['Service'].encode("utf-8").strip() 
            Protection = record['Protection'].encode("utf-8").strip() 
            UserPresence = record['UserPresence'].encode("utf-8").strip() 
            Creation = record['Creation Time'].encode("utf-8").strip() 
            Modified = record['Modified Time'].encode("utf-8").strip() 
            Data = record['Data'].encode("utf-8").strip()
            base64Data = base64.decodestring(Data)
        
            canPrintFlag = True
            if str(base64Data).startswith('bplist'):
                with tempfile.NamedTemporaryFile() as temp:
                    temp.write(base64Data)
                    temp.flush()
                    plist_obj = PlistUtil(temp.name)
                    temp.seek(0)
                    content = ''
                    for line in temp.readlines():
                        content += line                 
                    temp.close()
                    
                    base64Data = content
            else: 
                for j in range(len(base64Data)):
                    c = ord(base64Data[j])
                    if c < 32 or c > 126:
                        canPrintFlag = False
                        break;       
                    
            if EntitlementGroup.find(pattern) != -1 \
               or Account.find(pattern) != -1 \
               or Service.find(pattern) != -1 \
               or Protection.find(pattern) != -1 \
               or UserPresence.find(pattern) != -1 \
               or Creation.find(pattern) != -1 \
               or Modified.find(pattern) != -1 \
               or Data.find(pattern) != -1 \
               or base64Data.find(pattern) != -1 :
                
                res += ('Num: ' + str(k).encode("utf-8").strip() + '\n')
                res += ('EntitlementGroup: ' + self.parse0x0D_XML(EntitlementGroup) + '\n')
                res += ('Account: ' + self.parse0x0D_XML(Account) + '\n')
                res += ('Service: ' + self.parse0x0D_XML(Service) + '\n')
                res += ('Protection: ' + self.parse0x0D_XML(Protection) + '\n')
                res += ('UserPresence: ' + self.parse0x0D_XML(UserPresence) + '\n')
                res += ('Creation: ' + self.parse0x0D_XML(Creation) + '\n')
                res += ('Modified: ' + self.parse0x0D_XML(Modified) + '\n')
                res += ('Data: ' + Data + '\n')
                res += ('base64Data: ' + (base64Data if canPrintFlag else '') + '\n')
                res += '\n'

                '''
                result.add_row([str(k).encode("utf-8").strip(), 
                                self.parse0x0D_XML(EntitlementGroup),
                                self.parse0x0D_XML(Account),
                                self.parse0x0D_XML(Service),
                                self.parse0x0D_XML(Protection),
                                self.parse0x0D_XML(UserPresence),
                                self.parse0x0D_XML(Creation),
                                self.parse0x0D_XML(Modified),
                                Data,
                                (base64Data if canPrintFlag else '')])
                '''
                
        return res