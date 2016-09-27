

#author: june

import os
import globals as G


########################################################################
class WeakClassDump:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, app):
        """Constructor"""
        self.app = app
        self.remote_header_dir_base = "/tmp/weak_class_dump_"
        self.remote_header_dir = "{}{}".format(self.remote_header_dir_base, self.app.uuid)
        
    
    #----------------------------------------------------------------------
    def execute_dump(self):
        """"""
        app = self.app
        
        #check cycript installed
        G.log(G.INFO, 'Check cycript installed...')
        device = app.device
        if device.cycript_installed() == False:
            G.log(G.INFO, 'Cycript not installed, please install cycript first.')
            return 
        
        #use weak_classdump.cy
        #from https://github.com/limneos/weak_classdump
        G.log(G.INFO, 'Upload script files...')
        cy_path = "/var/root/weak_classdump.cy"
        if device.file_exists(cy_path) == False:
            #get current path:
            #1.os.path.abspath(os.curdir)
            #2.os.path.abspath('.')
            #3.os.getcwd()
            
            #upload weak_classdump.cy
            exec_path = os.path.split(os.path.realpath(__file__))[0]
            index = exec_path.rfind(os.path.sep) + 1
            device.minisftp.putfile(cy_path, "{}bin/weak_classdump.cy".format(exec_path[:index]), None)
        
        
        #cmd: cycript -p tiaomabijia weak_classdump.cy; cycript -p tiaomabijia
        #cmd: weak_classdump_bundle([NSBundle mainBundle],"/tmp/tiaomabijia")
        local_ins_path = "{}/weak_classdump_bundle.cy".format(app.cache_dir)
        remote_ins_path = "/var/root/weak_classdump_bundle.cy"
        f = open(local_ins_path, "w")
        f.write("weak_classdump_bundle([NSBundle mainBundle],\"{}\");".format(self.remote_header_dir))
        f.close()
        
        #upload weak_classdump_bundle.cy
        if device.file_exists(remote_ins_path) == True:
            device.sshopt.ssh_exec("rm {}".format(remote_ins_path))
        device.minisftp.putfile(remote_ins_path, local_ins_path, None)
        
        #launch app
        G.log(G.INFO, 'Launch target application...')
        device.launch_app(app.bundle_identifier)
        
        #inject weak_classdump.cy
        G.log(G.INFO, 'Inject script file...')
        cmd = "cycript -p {} {}".format(app.binary_name, cy_path)
        l = device.sshopt.ssh_exec(cmd)
        
        #run
        G.log(G.INFO, 'Start dump headers...')
        G.log(G.INFO, 'This may take some time...')
        cmd = "cycript -p {} {}".format(app.binary_name, remote_ins_path)
        l = device.sshopt._ssh_exec(cmd)
        #l = device.sshopt.ssh_exec(cmd)
        
        return self.remote_header_dir
    
    
    #----------------------------------------------------------------------
    def dumpclz_download_result(self, path):
        """"""
        '''
        class dump time
        this may take some time which depends on the binary size,
        it looks like weak_classdump_bundle does not work on ios 8/9,
        it will cause an error: 'Application received signal SIGSEGV',
        and i have not figure it out
        '''
        remote_res_path = self.execute_dump()
        
        #gzip
        #remote_res_path = '/tmp/weak_class_dump_6A3A7DF0-E723-40FA-9918-7DCB0832AACF'
        tar_name = '/var/root/{}_clzdump.tar'.format(self.app.uuid)
        gz_name = '{}.gz'.format(tar_name)
        
        if self.app.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.app.device.sshopt.ssh_exec(cmd)
    
        if self.app.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.app.device.sshopt.ssh_exec(cmd)        
        
        G.log(G.INFO, 'Package result...')
        index = remote_res_path.rfind(os.path.sep)
        tmp_dir = remote_res_path[:index]
        target_dir = remote_res_path[index + 1:]
        cmd = 'cd \'{}\' && tar cvf \'{}\' \'{}\''.format(tmp_dir, tar_name, target_dir)
        self.app.device.sshopt._ssh_exec(cmd)
        
        G.log(G.INFO, 'Gzip package...')
        cmd = 'cd ~ && gzip \'{}\''.format(tar_name)
        self.app.device.sshopt._ssh_exec(cmd)
    
        #download
        G.log(G.INFO, 'Download result...')
        self.app.device.minisftp.getfile(gz_name, path, None)
        
        #clear cache
        G.log(G.INFO, 'Do clear job...')
        if self.app.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.app.device.sshopt.ssh_exec(cmd)
            
        if self.app.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.app.device.sshopt.ssh_exec(cmd) 
            
        return path


    