

#author: june

import re
import os
import numpy
import select
import paramiko
from abstracttool import Tool
from minisftp import Minisftp
from application import App
from sysapp import SysApp
from BinaryCookieReader import BinaryUtil
from KeychainUtil import KeychainUtil
from SshUtil import SSHOptionUtil
from CerticateUtil import CertficateUtil
from prettytable import PrettyTable
import globals as G



########################################################################
class Device(Tool):
    """"""
    
    apps_dir_ios_pre8 = '/private/var/mobile/Applications'
    apps_dir_ios_8 = '/private/var/mobile/Containers/Bundle/Application'
    data_dir_ios_8 = '/private/var/mobile/Containers/Data/Application'
    

    #----------------------------------------------------------------------
    def __init__(self, host, username, password, sftp_port):
        """Constructor"""
        super(self.__class__, self).__init__()
        self.host = host
        self.username = username
        self.password = password
        self.sftp_port = sftp_port
        self.sshopt = SSHOptionUtil(self.host, self.username, self.password, self.sftp_port)
        self.ssh = self.sshopt.ssh
        if self.sshopt.ssh is None:
            return 
        #connect sftp
        self.minisftp = self.sshopt.minisftp#Minisftp(self.host, self.sftp_port, self.username, self.password)
        #self.minisftp.sftp_conn()
        if self.sshopt.minisftp is None:
            return         
        #check ios version
        stat = self.minisftp.file_exists(self.apps_dir_ios_8)
        self.cache_dir = self.tmp_path()
        self.applist = []
        self.sysapplist = []
        self.keychaineditor = None
        self.cert = None
        if not stat:
            self.ios_version = 7
            self.apps_dir = self.apps_dir_ios_pre8
            self.data_dir = self.apps_dir_ios_pre8
        else:
            self.ios_version = 8
            self.apps_dir = self.apps_dir_ios_8
            self.data_dir = self.data_dir_ios_8 
        
        self.sys_apps_dir = '/Applications'
        
        
            
    '''
    #----------------------------------------------------------------------
    def ssh_conn(self):
        """"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, username=self.username, password=self.password)
    
        
    #----------------------------------------------------------------------    
    def ssh_exec(self, cmd, buffsize=-1, timeout=None, get_pty=False):
        """"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, buffsize, timeout, get_pty)
            return stdout.readlines()
        except paramiko.SSHException:
            return -1
    
    #----------------------------------------------------------------------    
    def ssh_exec_last(self, cmd, buffsize=-1, timeout=None, get_pty=False):
        """"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, buffsize, timeout, get_pty)
            return stdout
        except paramiko.SSHException:
            return -1 
    
    #----------------------------------------------------------------------
    def ssh_close(self):
        """"""
        self.minisftp.sftp_close()
        self.ssh.close()
    '''

    #----------------------------------------------------------------------
    def list_all_applications(self):
        """"""
        #third party app list
        self.applist = self.install_app_list()
        #system app list
        self.sysapplist = self.system_app_list()
    
    
    #----------------------------------------------------------------------
    def find_app_by_pattern(self, pattern):
        """
        function: find app(including third party app and system app)
        """
        
        app = self.find_sysapp_by_pattern(pattern)
        
        if app is None:
            app = self.app_by_bundle_id(pattern)
            
        return app

    #---------------------------------------------------------------------- 
    def find_sysapp_by_pattern(self, pattern):
        """
        function: find sysapp
        """
        #find sysapp list first
        self.sysapplist = self.system_app_list()
        
        for sysapp in self.sysapplist:
            if pattern == sysapp.basename[:sysapp.basename.rfind('.app')] or pattern == sysapp.bundle_identifier:
                return sysapp
        
        return None
    
        
    #----------------------------------------------------------------------
    def system_app_list(self):
        """"""
        if self.sysapplist != []:
            return self.sysapplist
        
        #get system application dir list
        l = self.minisftp.list_dir(self.sys_apps_dir)
        if l is None:
            G.log(G.INFO, "No applications found.")
            return None
        
        for basename in l:
            sysapp = SysApp(basename, self)
            if sysapp.binary_name is None:
                continue
            
            self.sysapplist.append(sysapp)
        
        return self.sysapplist
    
    
    #----------------------------------------------------------------------
    def install_app_list(self):
        """"""
        #if self.applist != []:
        #    return self.applist
        if self.ios_version == 8:
            # need to refresh iOS uicache in case app was installed after last reboot.
            # Otherwise the /var/mobile/Library/MobileInstallation/LastLaunchServicesMap.plist will be out of date 
            G.log(G.INFO, 'Refresh LastLaunchServicesMap...')
            self.sshopt.ssh_exec(self.cmd_refresh_uicache)
        
        #get uuid list
        l = self.minisftp.list_dir(self.apps_dir)
        if l is None:
            G.log(G.INFO, "No applications found.")
            return None
        
        #add who
        for uuid in l:
            app = App(uuid, self)
            if app.binary_name is None:
                continue
            self.applist.append(app)
            
        return self.applist
    
    
    #----------------------------------------------------------------------
    def app_by_bundle_id(self, bundle_id):
        """
        function : find third party application
        """
        
        res = None
        refresh_flag = False
        
        if self.applist is None:
            refresh_flag = True
            
            self.applist = self.install_app_list()
            
            if self.applist is None:
                G.log(G.INFO, 'Faild to find any application.')
                res = None
        
        for e in self.applist:
            if e.bundle_identifier == bundle_id:
                res = e
                break
        
        if not refresh_flag and res is None:
            self.applist = self.install_app_list()
            
            if self.applist is None:
                G.log(G.INFO, 'Faild to find any application.')
                res = None
        
            for e in self.applist:
                if e.bundle_identifier == bundle_id:
                    res = e
                    break            
        
        return res
    
    #----------------------------------------------------------------------
    def _remote2cache_path(self, path):
        """"""

        local_path = self.cache_dir + re.sub("/private/var/mobile/Applications", "", re.sub("/private/var/mobile/Containers/Data/Application", "", re.sub(self.apps_dir, "", path)))# os.path.basename(path)#os.path.dirname(tmp_path)
        #local_path = re.sub(".app", "_app", local_cache_dir)
        return local_path
    
    
    #----------------------------------------------------------------------
    def _cache_file(self, remote_path):
        """"""
        local_path = self._remote2cache_path(remote_path)
        
        #local_path = re.sub(".app", "_app", path)

        self.mkdir_p(local_path[:local_path.rfind("/")])
        if not os.path.exists(local_path):
            self.minisftp.getfile(remote_path, local_path, None)
        
        return os.path.realpath(local_path.encode("utf-8").strip())
    
    
    #----------------------------------------------------------------------
    def read_binary_cookie(self):
        """"""
        binary_cookie_remote_path = "/private/var/mobile/Library/Cookies/Cookies.binarycookies"
        binary_cookie_path = self._cache_file(binary_cookie_remote_path)
        binary_cookie = BinaryUtil(binary_cookie_path)
        binary_cookie.read_binary_cookie()
        
        
    #----------------------------------------------------------------------
    def read_keyboard_cache(self):
        """"""
        keyboard_cache_remote_file = '/private/var/mobile/Library/Keyboard/dynamic-text.dat'
        keyboard_cache_file = self._cache_file(keyboard_cache_remote_file)
        #myarray = numpy.fromfile(keyboard_cache_file, dtype=float)
        #f = open(keyboard_cache_file, "rb")
        res = ""
        with open(keyboard_cache_file, "rb") as f:
            byte = f.read(1)
            while byte:
                #ASCII printable
                if ord(byte) >= 0x20 and ord(byte) <= 0x7E:
                    res += byte
                else:
                    res += ' '
                byte = f.read(1)
                
        return res
    
    
    #----------------------------------------------------------------------
    def logging(self, stop_event, _filter=None):
        """"""
        
        if not self.tool_installed('logtool'):
            G.log(G.INFO, 'logtool not installed, try \'chenv\' first.')
        
        cmd = self.tool_path['logtool']
        
        transport = self.ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command(cmd)
        self.content = ''
        while True:
            if stop_event.is_set():
                break
            if channel.exit_status_ready():
                break
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                l =  channel.recv(1024)
                if _filter is not None and _filter in str(l).decode("utf-8").strip():
                    print l,
                else:
                    print l,
                self.content += l
        
        '''
        if _filter is None:
            cmd = "idevicesyslog"
        else:
            cmd = 'idevicesyslog | awk -F\'{}\[[0-9]+\] *\' \'/{}\[[0-9]+\]/{}\''.format(_filter, _filter, '{print $2}')
            #cmd = 'idevicesyslog | grep \'{}\''.format(_filter)
        
        
        stdout_ = self.exec_shell_last(cmd)
        
        l = stdout_.readline()
        while l:
            print l,
            l = stdout_.readline()
        '''

    #----------------------------------------------------------------------
    #pb_names pb_names should be split by space, e.g."a b c d e"
    def watch_pasteboard(self, pb_names=None):
        """"""
        if pb_names is None:
            cmd = "{} 1".format(self.tool_path['pbwatcher']) 
            #cmd = "ls"
        else:
            cmd = "{} 1 {}".format(self.tool_path['pbwatcher'], pb_names)
                
        transport = self.ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command(cmd)
        content = ''
        while True:
            if channel.exit_status_ready():
                break
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                l =  channel.recv(1024).split(" ")
                date = l[0]
                time = l[1]
                irange = l[2]
                #do print when pastedboard changed
                if content != l[3]:
                    content = l[3]
                    print date, time, content,
        
        
    #----------------------------------------------------------------------
    def install_ipa(self, ipa_path):
        """"""
        filename, file_extension = os.path.splitext(ipa_path)
        
        if os.path.isfile(ipa_path) is not True:
            return False
        
        if file_extension != '.ipa' and file_extension != '.IPA':
            return False

        #best check if bundle_id has been installed or not
        #but first should read ipa file with python to get bundle_id, so let it go
        
        #get remote file full path
        remote_path = '/var/root/sec_audit_install.ipa' #+ os.path.basename(ipa_path)
        
        #should check if remotefile exits
        cmd_clear_ipa = "rm {}".format(remote_path)
        if self.minisftp.file_exists(remote_path):
            #if exists, rm remote file
            r = self.sshopt.ssh_exec(cmd_clear_ipa)
        
        #upload ipa file
        attr = self.minisftp.putfile(remote_path, ipa_path, None)
        
        #exec install
        cmd = "{} {}".format(self.tool_path['appinst'], remote_path)
        transport = self.ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command(cmd)
        while True:
            if channel.exit_status_ready():
                break
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                l =  channel.recv(4096).split(" ")
                r = ' '.join(l).split('\n')
                for e in r:
                    #best to check (if ' installed bundle_id' in e: )
                    #but first should read ipa file with python to get bundle_id, so let it go
                    if ' installed ' in e and 'have installed appinst' not in e:
                        #clear ipa file
                        r = self.sshopt.ssh_exec(cmd_clear_ipa)
                        return True
                    if 'not exist' in e or 'failed to' in e or 'cannot read ipa file entry' in e:
                        G.log(G.INFO, e)
        
        #clear ipa file
        r = self.sshopt.ssh_exec(cmd_clear_ipa)
        
        return False

    
    
    #----------------------------------------------------------------------
    def launch_app(self, bundle_id):
        """"""
        pid = str(0)
        
        cmd = "{} {}".format(self.tool_path['open'], bundle_id)
        
        transport = self.ssh.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command(cmd)
        while True:
            if channel.exit_status_ready():
                break
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                l =  channel.recv(1024).split(" ")
                r = ' '.join(l)#.split('\n')
                return False, r, pid
        
        #get pid
        app = self.find_app_by_pattern(bundle_id)
        
        if app is None:
            return False, '', str(0)
        
        pid = app.get_pid()
                
        return True, '', pid
    
    
    #----------------------------------------------------------------------
    def tool_installed(self, tool):
        """"""
        
        if self.tool_path.has_key(tool):
            return self.minisftp.file_exists(self.tool_path[tool])
        else:
            return False
        
    
    #----------------------------------------------------------------------
    def cache_file(self, remote_path, local_path):
        """"""
        
        self.mkdir_p(local_path[:local_path.rfind("/")])
        
        if not os.path.exists(local_path):
            self.minisftp.getfile(remote_path, local_path, None)
        
        return os.path.realpath(local_path.encode("utf-8").strip())
    
    
    #----------------------------------------------------------------------
    def cycript_installed(self):
        """"""
        return self.tool_installed('cycript')
    
    
    #----------------------------------------------------------------------
    def file_exists(self, remote_path):
        """"""
        return self.minisftp.file_exists(remote_path)
    
    
    #----------------------------------------------------------------------
    def dump_keychain(self):
        """"""
        #if self.keychaineditor is None:
        #    self.keychaineditor = KeychainUtil(self.sshopt)
        self.keychaineditor = KeychainUtil(self.sshopt)
            
        return self.keychaineditor.parse()
    
    
    #----------------------------------------------------------------------
    def edit_keychain(self, dataID, newData, with_base64):
        """"""
        #if self.keychaineditor is None:
        self.keychaineditor = KeychainUtil(self.sshopt)

        return self.keychaineditor.edit_by_id(dataID, newData, with_base64)
    
    
    #----------------------------------------------------------------------
    def delete_keychain(self, dataID):
        """"""
        #if self.keychaineditor is None:
        self.keychaineditor = KeychainUtil(self.sshopt)
        
        return self.keychaineditor.delete_by_ID(dataID)
        
    
    #----------------------------------------------------------------------
    def grep_keychain(self, pattern):
        """"""
        #if self.keychaineditor is None:
        self.keychaineditor = KeychainUtil(self.sshopt)
            
        return self.keychaineditor.grep_keychain(pattern)
    
    
    #----------------------------------------------------------------------
    def CA_install_burp(self):
        """"""
        if self.cert is None:
            self.cert = CertficateUtil(self.sshopt)
            
        return self.cert.install_burp_cert()
    
    #----------------------------------------------------------------------
    def CA_list_cert(self):
        """"""
        if self.cert is None:
            self.cert = CertficateUtil(self.sshopt)
            
        return self.cert.list_certs()
    
    
    #----------------------------------------------------------------------
    def CA_delete_cert(self, cert_id):
        """"""
        if self.cert is None:
            self.cert = CertficateUtil(self.sshopt)
        
        return self.cert.delete_cert(cert_id)
    
    
    #----------------------------------------------------------------------
    def CA_add_cert(self, cert_path):
        """"""
        if self.cert is None:
            self.cert = CertficateUtil(self.sshopt)
            
        if not self.local_file_exists(cert_path):
            G.log(G.INFO, 'File \'{}\' not exists.'.format(cert_path))
            return False

        return self.cert.add_cert(cert_path)
    
    
    #----------------------------------------------------------------------
    def CA_export_cert(self, path):
        """"""
        if self.cert is None:
            self.cert = CertficateUtil(self.sshopt)
        
        return self.cert.export_cert(path)
        
        
    #----------------------------------------------------------------------
    def open_url(self, url):
        """"""
        if self.tool_installed('uiopen'):
            cmd = "{} {}".format(self.tool_path['uiopen'], url)
            self.sshopt.ssh_exec(cmd)
            
            
    #----------------------------------------------------------------------
    def kill_by_name(self, name):
        """"""
        cmd = "killall -9 {}".format(name)
        
        self.sshopt.ssh_exec(cmd)
    
    
    #----------------------------------------------------------------------
    def install_tool(self, tool, remote_path):
        """"""
        #----get current directory path-----
        #print os.getcwd()
        #print os.path.abspath(os.curdir)
        #print os.path.abspath('.')
        p = os.path.split(os.path.realpath(__file__))[0]
        index = p.rfind('/')
        path = p[0:index]
        
        local_path = path + os.sep + 'bin' + os.sep + tool
        self.minisftp.putfile(remote_path, local_path, None)
        cmd = "chmod a+x {}".format(remote_path)
        self.sshopt.ssh_exec(cmd)
        #print local_path
     
    #----------------------------------------------------------------------
    def check_env(self):
        """"""
        G.log(G.INFO, 'Checking enviroment...')
        keys = self.tool_path.keys()
        
        '''
        for key in keys:
            if not self.tool_installed(key):
                print "\'{}\' => NO".format(key),
                if str(self.tool_path[key]).find('/var/root/') != -1:
                    print "=> installing \'{}\'...".format(key),
                    self.install_tool(key, str(self.tool_path[key]))
                    print "=> complete."
                else:
                    print "=> Please install it in Cydia."
            else:
                print "\'{}\' => YES ".format(key)
        '''      
                
        result = PrettyTable(["Tool", "Status", "Solution"])
        result.align["Solution"] = "l"
        result.align["Tool"] = "l"
        
        tool = 'None'
        status = 'NO'
        solution = 'None'
        for key in keys:
            tool = key
            if not self.tool_installed(key):
                if str(self.tool_path[key]).find('/var/root/') != -1:
                    self.install_tool(key, str(self.tool_path[key]))
                    status = 'Ready'
                    solution = 'None'
                else:
                    status = 'NOT Ready'
                    solution = 'Install in Cydia'
            else:
                status = 'Ready'
                solution = 'None'
                
            result.add_row([tool, status, solution])
            
        print result


    #----------------------------------------------------------------------
    def download_dir(self, remote_dir, save_path, clearFirst=True, clearAfter=True):
        """"""
        
        #check remote file exists
        if not self.file_exists(remote_dir):
            G.log(G.INFO, 'Dir \'{}\' not exists.'.format(remote_dir))
            return False
        
        #check remote path is dir
        if not self.minisftp.isdir(remote_dir):
            G.log(G.INFO, '\'{}\' is not dir.'.format(remote_dir))
            return False
        
        #make tar and gzip package name
        #gz_name is the final download file
        tar_name = '/var/root/_tmp_iSecAudit_dir_download.tar'
        gz_name = '{}.gz'.format(tar_name)
        
        
        if os.path.isdir(os.path.abspath(os.path.expanduser(save_path))):
            save_path = os.path.join(save_path, os.path.basename(gz_name))        
        
        #mkdir_p 
        self.mkdir_p(os.path.abspath(os.path.expanduser(os.path.dirname(save_path))))

        #check local file exists
        idx = 0
        _local_path = save_path
        while os.path.exists(_local_path):
            tmp = _local_path
            _local_path = '_'.join([save_path, str(idx)])
            idx += 1
            G.log(G.INFO, 'Local file \'{}\' already exists, try path: \'{}\'.'.format(tmp, _local_path))
        
        #clear first
        if clearFirst:
            G.log(G.INFO, 'Do clear job at beginning...')
            if self.file_exists(tar_name):
                cmd = 'rm {}'.format(tar_name)
                self.sshopt.ssh_exec(cmd)
        
            if self.file_exists(gz_name):
                cmd = 'rm {}'.format(gz_name)
                self.sshopt.ssh_exec(cmd) 
            
        
        G.log(G.INFO, 'Package result...')
        if remote_dir.endswith(os.path.sep):
            remote_res_path = remote_dir[:-1]
        else:
            remote_res_path = remote_dir
        
        #tar target dir
        index = remote_res_path.rfind(os.path.sep)
        tmp_dir = remote_res_path[:index]
        target_dir = remote_res_path[index + 1:]
        cmd = 'cd \'{}\' && tar cvf \'{}\' \'{}\''.format(tmp_dir, tar_name, target_dir)
        self.sshopt.ssh_exec(cmd)
        
        #gzip target tar
        G.log(G.INFO, 'Gzip package...')
        cmd = 'cd ~ && gzip \'{}\''.format(tar_name)
        self.sshopt._ssh_exec(cmd)

        #download zip file
        G.log(G.INFO, 'Download result...')
        r = False
        r = self.minisftp.getfile(gz_name, _local_path, None)
        
        if r == False:
            G.log(G.INFO, 'Target dir maybe an empty dir...')
        
        #clear after
        if clearAfter:
            G.log(G.INFO, 'Do clear job at last...')
            if self.file_exists(tar_name):
                cmd = 'rm {}'.format(tar_name)
                self.sshopt.ssh_exec(cmd)
        
            if self.file_exists(gz_name):
                cmd = 'rm {}'.format(gz_name)
                self.sshopt.ssh_exec(cmd)         
        
        return _local_path, r