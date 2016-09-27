
#author: june
import os
import errno
import subprocess


########################################################################
class Tool(object):
    """"""

    

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.tool_path = {}
        self.tool_path['pbwatcher'] = "/var/root/pbwatcher"
        self.tool_path['Clutch'] = "/var/root/Clutch"
        self.tool_path['su'] = "/bin/su"
        self.tool_path['appinst'] = "/var/root/appinst"
        self.tool_path['open'] = "/usr/bin/open"
        self.tool_path['openurl'] = "/usr/bin/openurl"
        self.tool_path['uiopen'] = "/usr/bin/uiopen"
        self.tool_path['openURL'] = "/usr/bin/openURL"
        self.tool_path['cycript'] = "/usr/bin/cycript"
        self.tool_path['keychaineditor'] = "/var/root/keychaineditor"
        self.tool_path['dumpdecrypted_armv6.dylib'] = "/var/root/dumpdecrypted_armv6.dylib"
        self.tool_path['dumpdecrypted_armv7.dylib'] = "/var/root/dumpdecrypted_armv7.dylib"
        self.tool_path['tar'] = '/usr/bin/tar'
        self.tool_path['gzip'] = '/bin/gzip'
        self.tool_path['logtool'] = '/var/root/logtool'
        self.tool_path['debugserver61'] = '/var/root/debugserver'
        self.tool_path['debugserver84'] = '/var/root/debugserver'
        
        
        self.cmd_app_list = "Clutch -i" 
        self.cmd_refresh_uicache = "/bin/su mobile -c /usr/bin/uicache"
        
    #----------------------------------------------------------------------
    def list2str(self, l):
        """"""
        s = ''
        for element in l:  
            s += element 
       
        return s
    
    #----------------------------------------------------------------------
    def tmp_path(self):
        """"""
        return os.environ['HOME'] + "/.ihack/"
    
    
    #----------------------------------------------------------------------
    def mkdir_p(self, path):
        """"""
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
    
    
    #----------------------------------------------------------------------
    def exec_shell(self, cmd):
        """"""
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    
    
    #----------------------------------------------------------------------
    def cmd_which(self, cmd):
        """"""
        exts = os.environ['PATHEXT'] if os.environ.has_key('PATHEXT') else ['']
        
        for path in os.environ['PATH'].split(os.pathsep):
            for ext in exts:
                exe = os.path.join(path, "{}{}".format(cmd, ext))
                if os.access(exe, os.X_OK):
                    return True 
                
        return False

    
    #----------------------------------------------------------------------
    def exec_shell_last(self, cmd):
        """"""
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return p.stdout
        #while l:
        #    print l
        #    l = p.stdout.readline()
        
        
    #----------------------------------------------------------------------
    def local_file_exists(self, path):
        """"""
        return os.path.isfile(path)