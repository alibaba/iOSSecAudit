

'''
author: june
function: cycript helper
'''

import os


########################################################################
class CycriptUtil:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        #self.device = device
    
    
    #----------------------------------------------------------------------
    def run_cyfile(self, device, pid, cy_file):
        """"""
        #get remote cy_file path
        _remote_cy_file = os.path.basename(cy_file)
        
        #check remote cy_file exists
        G.log(G.INFO, 'Check remote cy file exists...')
        idx = 0
        remote_cy_file = _remote_cy_file
        while device.file_exists(remote_cy_file):
            tmp = remote_cy_file
            remote_cy_file = '_'.join([_remote_cy_file, str(idx)])
            idx += 1
            G.log(G.INFO, 'Remote file \'{}\' already exists, try path: \'{}\'.'.format(tmp, remote_cy_file))
        
        #upload cy_file
        G.log(G.INFO, 'Upload cy file to device...')
        if device.minisftp.putfile(remote_cy_file, cy_file) is None:
            G.log(G.INFO, 'Upload file \'{}\' failed.'.format(remote_cy_file))
            return False
    
        #run cy_file
        G.log(G.INFO, 'Inject script file...')
        cmd = "cycript -p {} \'{}\'".format(pid, remote_cy_file)
        l = device.sshopt.ssh_exec(cmd)
        
        return l
        