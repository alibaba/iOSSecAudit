

'''
#function: system application wrapper
#author: june
'''

import os
import re
#import time

from abstracttool import Tool
from InfoPlistUtil import InfoPlistUtil
from locaUtil import LocalUtils
import globals as G


########################################################################
class SysApp(Tool):
    """
    actually, That App class in application.py should better to inherit SysApp
    which will make so many codes reused
    or we can design a third class Application, App class in application.py and SysApp class in this file inherit from Application
    but, when i wrote application.py, i don't realize this tool needs to handle system applications
    of course, u don't realized too
    so, if u don't agree what i did, what i wrote
    bit me :)
    """

    #----------------------------------------------------------------------
    def __init__(self, basename, device):
        """Constructor"""
        super(self.__class__, self).__init__()
        self.basename = basename
        self.device = device
        self.cache_dir = os.path.join(self.tmp_path(), basename[:basename.rfind('.app')])
        self.app_dir = os.path.join(self.device.sys_apps_dir, basename)
        
        info_plist_remote_path = os.path.join(self.app_dir, 'Info.plist')
        if not self.device.file_exists(info_plist_remote_path):
            self.binary_name = None
            return
        #download Info.plist and return local path
        info_plist_local_path = self.cache_file(info_plist_remote_path)        
        #turn plist to dictionary
        self.info_plist_util = InfoPlistUtil(info_plist_local_path)
        self.binary_name = self.info_plist_util.get_property("CFBundleExecutable")
        self.bundle_identifier = self.info_plist_util.get_property("CFBundleIdentifier")
        self.display_name = None
        self.get_display_name()
        self.binary_path_remote = os.path.join(self.app_dir, self.binary_name)
        if not self.device.file_exists(self.binary_path_remote):
            self.binary_name = None
            return

        
    #----------------------------------------------------------------------
    def remote2cache_path(self, path):
        """"""
        
        #clutch binary dump path 
        '''
        #can't dump system app
        if path.find("/var/tmp/clutch/") != -1 and path.find(self.bundle_identifier) != -1 and path.find(self.binary_name) != -1:
            tmp = self.binary_path()
            if tmp is None:
                return None
            path = tmp + ".decrypt"
        
        
        #clutch ipa dump path
        if path.find("/private/var/mobile/Documents/Dumped/") != -1 and path.find("ipa") != -1:
            path = os.path.sep + self.bundle_identifier + '.ipa'
        '''
        
        
        #local_path = self.cache_dir + re.sub("/private/var/mobile/Applications", "", re.sub("/private/var/mobile/Containers/Data/Application", "", re.sub(self.app_dir, "", path)))# os.path.basename(path)#os.path.dirname(tmp_path)
        #local_path = re.sub(".app", "_app", local_cache_dir)
        local_path = self.cache_dir + re.sub(self.device.sys_apps_dir, "", path)
        
        return local_path
    
    
    #----------------------------------------------------------------------
    def cache_file(self, remote_path):
        """"""
        local_path = self.remote2cache_path(remote_path)
        if local_path is None:
            return None
        
        #local_path = re.sub(".app", "_app", path)
        
        self.mkdir_p(local_path[:local_path.rfind("/")])
        
        p = os.path.realpath(local_path.encode("utf-8").strip())
        
        #cmd = 'chmod 666 \'{}\''.format(remote_path.encode("utf-8").strip())
        #rtn = self.device.sshopt.ssh_exec(cmd)
        #rtn = self.device.minisftp.chmod(remote_path, 766)
        
        #if not rtn:
            #return None
        
        if not os.path.exists(local_path):
            self.device.minisftp.getfile(remote_path, local_path, None)
            #os.chmod(p, 666)
        
        return p
    
    
    #----------------------------------------------------------------------
    def get_display_name(self):
        """"""
        if self.display_name is None:
            self.display_name = self.info_plist_util.get_property("CFBundleDisplayName")
            if self.display_name is None:
                self.display_name = self.binary_name 
        
        return self.display_name
    
    
    #----------------------------------------------------------------------
    def debugserver(self, port=G.DEFAULT_DEBUG_PORT):
        """"""
        pid = self.get_pid()
        
        if pid == str(0):
            _, _, pid = self.device.launch_app(self.bundle_identifier)
            if pid == str(0):
                G.log(G.INFO, 'Launch app failed.')
                return False
        
        if self.device.ios_version == 8:
            debugserver = 'debugserver84'#self.tool_path['debugserver84']
        else:
            debugserver = 'debugserver61'#self.tool_path['debugserver61']
            
        if not self.device.tool_installed(debugserver):
            G.log(G.INFO, 'debugserver not installed.')
            return False
        
        #mapping port first 
        LocalUtils().mapping_port(port, port)
        
        #debugserver *:123456 -a 'MobileSafari'
        cmd = '{} *:{} -a \'{}\''.format(self.tool_path[debugserver], str(port), self.binary_name)
        #self.device.sshopt.ssh_exec(cmd)
        
        #sleep here, waiting for application finish launch 
        #time.sleep(1)
        
        
        import threading
        #t_stop = threading.Event()
        t = threading.Thread(target=self.device.sshopt.ssh_exec, args=(cmd, ))
        t.start()
        
        G.log(G.INFO, 'debugserver attach \'%s\' on \'%s\'.' % (self.binary_name, port))
        
        return True
    

    #----------------------------------------------------------------------
    def get_pid(self):
        """"""
        '''
        two ways to get pid:
        1.shell cmd
        2.sysctl
        i chiose shell cmd to get pid here, cause sysctl can be different on different ios version.
        '''
        self.pid = str(0)
        #cmd = ps aux| grep UUID | grep binary_name
        cmd = 'ps aux| grep {} | grep {}'.format(self.basename, self.binary_name)
        
        l =  self.device.sshopt.ssh_exec(cmd)
        
        if l == -1:
            G.log(G.INFO, 'Execute remote command error.')
            return str(0)
        
        path = self.binary_path_remote
        for e in l:
            if path in e:
                r = filter(None, e.split(' '))
                if len(r) > 1:
                    #USER PID %CPU %MEM VSZ RSS TT STAT STARTED TIME COMMAND
                    self.pid = r[1]
                
                break
        
        return self.pid