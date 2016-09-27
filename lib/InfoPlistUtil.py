

#author: june


from PlistUtil import *




########################################################################
class InfoPlistUtil(PlistUtil):
    """"""

    #----------------------------------------------------------------------
    #def __init__(self):
    #    """Constructor"""
    
    
    #----------------------------------------------------------------------
    def url_handler(self):
        """"""
        url_schemas = list()
        if (self.dic is not None) and ("CFBundleURLTypes" in self.dic):
            for url_type in self.dic["CFBundleURLTypes"]:
                if url_type is not None:
                    #for type_dic in url_type:
                    if "CFBundleURLSchemes" in url_type:
                        url_schemas.append(url_type["CFBundleURLSchemes"][0]) 

        return url_schemas