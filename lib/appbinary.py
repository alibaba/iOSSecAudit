

#author: june


import os
from otoolUtil import OtoolUtil
from abstracttool import Tool


########################################################################
class AppBinary(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, path):
        """Constructor"""
        self.local_path = path
        self.otool = OtoolUtil(self.local_path)
        
    
    #----------------------------------------------------------------------
    def is_encrypt(self):
        """"""
        if (self.otool is not None) and (self.otool.load_cmds is not None):
            for (k, v) in self.otool.load_cmds.items():
                if v['cmd'].strip().startswith("LC_ENCRYPTION_INFO") and v['cryptid'].strip() == str(1):
                    return True
        
        return False
    
    
    #----------------------------------------------------------------------
    def get_cryptid(self):
        """"""
        if (self.otool is not None) and (self.otool.load_cmds is not None):
            for (k, v) in self.otool.load_cmds.items():
                if v['cmd'].strip().startswith("LC_ENCRYPTION_INFO"):
                    return v['cryptid'].strip()
                
        return None
    
    
    #----------------------------------------------------------------------
    def is_PIE_set(self):
        """"""
        return self.otool.pie
    
    
    #----------------------------------------------------------------------
    def is_ARC_set(self):
        """"""
        return self.otool.arc
    
    
    #----------------------------------------------------------------------
    def is_stack_canaries_set(self):
        """"""
        return self.otool.stack_canaries
    
    
    #----------------------------------------------------------------------
    def all_strings(self):
        """"""
        cmd = "strings {}".format(self.local_path)
        return self.exec_shell(cmd)