
#author: june

import os
import plistlib
from abstracttool import Tool
import globals as G


########################################################################
class PlistUtil(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, path):
        """Constructor"""
        self.plist_path = path
        
        self.plutil = "/usr/bin/plutil"
        if not os.path.exists(self.plutil):
            self.plutil = "/usr/bin/plistutil"
        if not os.path.exists(self.plutil):
            self.plutil = None
            G.log(G.INFO, "plutil not found")
            
        self.plist2dic()
        
    
    
    #----------------------------------------------------------------------
    def plist2dic(self):
        """"""
        if not self.plutil:
            G.log(G.INFO, "plutil not found")
            return None
        #convert to standard xml        
        cmd = "%s -convert xml1 \"%s\"" % (os.path.realpath(self.plutil), self.plist_path)        
        r = self.exec_shell(cmd)
        try:
            self.dic = plistlib.readPlist(self.plist_path)
            return self.dic            
        except:
            G.log(G.INFO, 'Read \'{}\'failed because it is not in correct format.')
            self.dic = None
            return None
        
    
    
    #----------------------------------------------------------------------
    def get_property(self, key):
        """"""
        if self.dic is None:
            return None
    
        if key in self.dic:
            return self.dic[key]
        else:
            #print key , "NOT FOUND."
            return None    

    
    #----------------------------------------------------------------------
    def view_detail(self):
        """"""
        if self.dic is not None:
            print self.dic