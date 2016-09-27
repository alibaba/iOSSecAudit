

#author: june
from pyusbmuxd import *
import globals as G


########################################################################
class USBMuxdUtil:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, rport=22, lport=2222):
        """Constructor"""
        self.rport = rport
        self.lport = lport
    
     
    #----------------------------------------------------------------------
    def test(self):
        """"""
        
        
    #----------------------------------------------------------------------
    def active_usbmuxd(self, localutil, port):
        """"""
        if localutil.is_port_in_use(port):
            G.log(G.INFO, "port: {} is in use.".format(port))
            return False
        
        path = "{}{}".format(os.path.split(os.path.realpath(__file__))[0], "/pyusbmuxd/tcprelay.py")

        cmd = [os.path.abspath(os.path.expanduser(path)), "-t", "22:{}".format(port)]
        
        localutil.run_process_in_background(cmd)
        return True    
    