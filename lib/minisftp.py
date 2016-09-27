
#author:june
import paramiko 
import os
import sys
import stat
import errno
from stat import S_ISDIR
import globals as G


########################################################################
class Minisftp:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, ssh):
        """Constructor"""
        self.sftp = ssh.open_sftp()
        

    '''
    #----------------------------------------------------------------------
    def __init__(self, host, port, username, password):
        """Constructor"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
    '''
    
    #----------------------------------------------------------------------
    def sftp_conn(self):
        """"""
        try:
            self.transport = paramiko.Transport((self.host, self.port)) 
            self.transport.connect(username = self.username, password = self.password) 
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            return True
        except paramiko.AuthenticationException:
            G.log(G.ERROR, "SFTP Authentication failed when connecting to %s" % self.host)
            return False
        except:
            G.log(G.ERROR, "SFTP Could not SSH to %s, waiting for it to start" % self.host)
            return False

    
    #----------------------------------------------------------------------
    def getfile(self, remotefile, localfile, callback):
        """"""
        try:
            return self.sftp.get(remotefile, localfile, callback) 
        except:
            G.log(G.ERROR, 'Access to \'{}\' Permission denied.'.format(remotefile))
            return False
        
    
    #----------------------------------------------------------------------
    def putfile(self, remotefile, localfile, callback):
        """""" 
        try :
            return self.sftp.put(localfile, remotefile, callback)
        except:
            G.log(G.ERROR, 'Access to \'{}\' Permission denied.'.format(remotefile))
            return None        
        
    #----------------------------------------------------------------------
    def file_exists(self, path):
        """"""
        try:
            stat = self.sftp.stat(path)
        except IOError, e:
            if e.errno == errno.ENOENT:
                return False
        else:
            return True
    
    #----------------------------------------------------------------------
    def list_dir(self, path):
        """"""
        #self.sftp.
        if self.file_exists(path):
            return self.sftp.listdir(path)
        else:
            return None

    #----------------------------------------------------------------------
    def sftp_close(self):
        """"""
        G.log(G.INFO, 'close sftp connection')
        self.sftp.close()
        #self.transport.close()

    
    #----------------------------------------------------------------------
    def glob(self, path, pattern=".*"):
        """"""
        l = self.sftp.listdir(path)
        return l
    
    
    #----------------------------------------------------------------------
    def chmod(self, remote_path, permisson):
        """"""
        try:
            self.sftp.chmod(remote_path, permisson)
            return True
        except:
            G.log(G.INFO, 'Access to \'{}\' Permission denied.'.format(remote_path))
            return False
    
    '''
    #this is just a wrong way to check a remote path is a dir or a file
    #----------------------------------------------------------------------
    def isdir(self, path):
        """"""
        try:
            for fileattr in self.sftp.listdir_attr(path):
                if stat.S_ISDIR(fileattr.st_mode):
                    return True
        except:
            pass
            
        return False
    '''
    
    #----------------------------------------------------------------------
    def isdir(self, path):
        try:
            return S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:
            #Path does not exist, so by definition not a directory
            return False    
