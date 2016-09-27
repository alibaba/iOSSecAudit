

#author: june

import os
import select
import paramiko
from abstracttool import Tool
from minisftp import Minisftp
import globals as G


########################################################################
class SSHOptionUtil(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, host, usr, psw, sftp_port):
        """Constructor"""
        self.host = host
        self.username = usr
        self.password = psw
        self.sftp_port = sftp_port
        #self.minisftp = Minisftp(self.host, self.sftp_port, self.username, self.password)
        #if not self.minisftp.sftp_conn():
        #    self.minisftp = None
        if not self.ssh_conn():
            self.ssh = None
            return
        if self.ssh is not None:
            self.minisftp = Minisftp(self.ssh)#self.ssh.open_sftp()
        else:
            self.minisftp = None
        #self.minisftp.put('/Users/june/tmp/mail.py', '/var/root/x.py', None) 
        #print '123'
    
    #----------------------------------------------------------------------
    def ssh_conn(self):
        """"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.host, port=self.sftp_port, username=self.username, password=self.password)
            return True
        except paramiko.AuthenticationException:
            G.log(G.ERROR, "SSH Authentication failed when connecting to host")
            return False
        except:
            G.log(G.ERROR, "SSH Could not SSH to %s, waiting for it to start host" % self.host)
            return False

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
        G.log(G.INFO, 'close ssh connection')
        self.ssh.close()
        
    
    #----------------------------------------------------------------------
    def file_exists(self, remote_path):
        """"""
        return self.minisftp.file_exists(remote_path) 
    
    
    #----------------------------------------------------------------------
    def cache_file(self, remote_path, local_path):
        """"""
        
        self.mkdir_p(local_path[:local_path.rfind("/")])
         
        if not self.file_exists(remote_path):
            return None
        
        if not os.path.exists(local_path):
            self.minisftp.getfile(remote_path, local_path, None)

        
        return os.path.realpath(local_path.encode("utf-8").strip())
    
    
    #----------------------------------------------------------------------
    def glob(self, path, pattern=".*"):
        """"""
        return self.minisftp.glob(path, pattern)
    
    
    def _ssh_exec(self, cmd, print_flag=None, end_flag=None):
        """"""
        #import time
        if cmd is None:
            G.log(G.INFO, 'Shell command is None.')
    
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
                l = channel.recv(1024)
                if print_flag is not None and l.find(print_flag) != None:
                    print l
                else:
                    #print '.',
                    pass
            #elif len(rl) == 0:
                #print '.',
                #time.sleep(3)
                #if end_flag is not None:
                #    pass