import pexpect
import sys
import tempfile



########################################################################
class Device_():
    """"""
    
    ios_version = 8.0
    apps_dir_ios_pre8 = '/private/var/mobile/Applications'
    apps_dir_ios_8 = '/private/var/mobile/Containers/Bundle/Application'
    data_dir_ios_8 = '/private/var/mobile/Containers/Data/Application'    

    tool_path = {"rsync":"/usr/bin/rsync",
                 "cycript":"/usr/bin/cycript",
                 "clutch":"/usr/bin/Clutch"}

    #----------------------------------------------------------------------
    def __init__(self, host, user, password, timeout=30, bg_run=False):
        self.host = host
        self.user = user
        self.password = password
        self.timeout = timeout
        self.bg_run = bg_run
        
        
    
    def ssh_exec(self, cmd, timeout=30, bg_run=False):                                                                                                 
        """SSH'es to a host using the supplied credentials and executes a command.                                                                                                 
        Throws an exception if the command doesn't return 0.                                                                                                                       
        bgrun: run command in the background"""                                                                                                                                    
    
        fname = tempfile.mktemp()                                                                                                                                                  
        fout = open(fname, 'w')                                                                                                                                                    
    
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'                                                                         
        if bg_run:                                                                                                                                                         
            options += ' -f'                                                                                                                                                       
        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.user, self.host, options, cmd)                                                                                                                 
        child = pexpect.spawn(ssh_cmd, timeout=timeout)                                                                                                                            
        child.expect(['password: '])                                                                                                                                                                                                                                                                                               
        child.sendline(self.password)                                                                                                                                                   
        child.logfile = fout                                                                                                         
        child.expect(pexpect.EOF)                                                                            
        child.close()                                                                                                                                                              
        fout.close()                                                                                                                                                               
    
        fin = open(fname, 'r')                                                                                                                                                     
        stdout = fin.read()                                                                                                                                                        
        fin.close()                                                                                                                                                                
    
        if 0 != child.exitstatus:                                                                                                                                                  
            raise Exception(stdout)                                                                                                                                                
    
        return stdout    