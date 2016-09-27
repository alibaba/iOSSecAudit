

#author: june

import os
from PlistUtil import *


########################################################################
class IOS8LastLaunchServicesMap(PlistUtil):
    """"""

    #----------------------------------------------------------------------
    #def __init__(self, path):
    #    """Constructor"""
    
    
    #----------------------------------------------------------------------
    def data_dir_by_bundle_id(self, bundle_id):
        """"""
        if self.dic.has_key("User"):
            if self.dic["User"].has_key(bundle_id):
                if self.dic["User"][bundle_id].has_key("Container"):
                    return self.dic["User"][bundle_id]["Container"]
        return ""
       
        
    #----------------------------------------------------------------------
    def entitlements_by_bundle_id(self, bundle_id):
        """"""
        if self.dic.has_key("User"):
            if self.dic["User"].has_key(bundle_id):
                if self.dic["User"][bundle_id].has_key("Entitlements"):
                    return self.dic["User"][bundle_id]["Entitlements"]
        return {}
    
    
    #----------------------------------------------------------------------
    def keychain_access_groups_by_bundle_id(self, bundle_id):
        """"""
        if self.dic.has_key("User"):
            if self.dic["User"].has_key(bundle_id):
                if self.dic["User"][bundle_id].has_key("Entitlements"):
                    if self.dic["User"][bundle_id]["Entitlements"].has_key("keychain-access-groups"):
                        return self.dic["User"][bundle_id]["Entitlements"]["keychain-access-groups"]
        return ""