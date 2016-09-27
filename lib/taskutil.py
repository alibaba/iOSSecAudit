
#author: june

import re
import os
import shutil
import json
import errno
from device import *
from locaUtil import LocalUtils
from weak_classdump import WeakClassDump
from cycriptUtil import CycriptUtil
import globals as G


########################################################################
class TaskUtil:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, host, user, password, sftp_port, mode):
        """Constructor"""
        self.thread_dict = {}
        if mode == 'lan':
            pass#self.device = Device(host, user, password, sftp_port)
        elif mode == 'usb':
            if LocalUtils().active_usbmuxd(sftp_port) == False:
                G.log(G.INFO, 'Connect failed.')
        #self.device.ssh_conn()
        #self.device.install_app_list()
        self.device = Device(host, user, password, sftp_port)
        if self.device.ssh is None:
            self.device = None
            G.log(G.INFO, 'Connect failed.')
        else:
            G.log(G.INFO, 'Connect success.')
    
    
    #----------------------------------------------------------------------
    def list_app(self):
        """"""
        self.device.install_app_list()
        i = 0
        G.log(G.INFO, "All installed Applications:")
        for e in self.device.applist:
            echo_str = "{}>.{}({})".format(i, e.display_name.encode('utf-8').strip(), e.bundle_identifier.encode('utf-8').strip())
            print echo_str
            i += 1
        #print ""


    #----------------------------------------------------------------------
    def app_detail_info(self, bundle_id):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO,  echo_str)
            return
        
        echo_str = "{} Detail Info:".format(app.display_name.encode('utf-8').strip())
        G.log(G.INFO, echo_str)
        print "Bundle ID       :", app.bundle_identifier.encode('utf-8').strip()
        print "UUID            :", app.uuid
        print "binary name     :", app.binary_name
        print "Platform Version:", app.platform_version()
        print "SDK Version     :", app.sdk_version()
        print "Mini OS         :", app.mini_os_version()
        print "Data Directory  :", re.sub("/private/var/mobile/Applications/", "", re.sub("/private/var/mobile/Containers/Data/Application/", "", app.data_directory()))
        handlers = ""    
        for e in app.url_handler():
            handlers += e
            handlers += "\n                  "
        #delete the last ==> "\n"
        handlers = handlers[0:handlers.rfind("\n                  ")]
        print "URL Hnadlers    :", handlers 
        print "Entitlements    :"
        if app.entitlement is None:
            print "\tget-task-allow:", ''
            print "\tbeta-reports-active:", ''
            print "\taps-environment:", ''
            print "\tapplication-identifier:", ''
            print "\tcom.apple.developer.team-identifier:", ''
            print "\tcom.apple.security.application-groups:", ''
        else:
            print "\tget-task-allow:", app.entitlement['get-task-allow'] if app.entitlement.has_key('get-task-allow') else ''
            print "\tbeta-reports-active:", app.entitlement['beta-reports-active'] if app.entitlement.has_key('beta-reports-active') else ''
            print "\taps-environment:", app.entitlement['aps-environment'] if app.entitlement.has_key('aps-environment') else ''
            print "\tapplication-identifier:", app.entitlement['application-identifier'] if app.entitlement.has_key('application-identifier') else ''
            print "\tcom.apple.developer.team-identifier:", app.entitlement['com.apple.developer.team-identifier'] if app.entitlement.has_key('com.apple.developer.team-identifier') else ''
            print "\tcom.apple.security.application-groups:", app.entitlement['com.apple.security.application-groups'] if app.entitlement.has_key('com.apple.security.application-groups') else ''            
        
        #print " "
    
    
        
    #----------------------------------------------------------------------
    def analyze_binary(self, bundle_id):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        if app.analyze_binary() == False:
            G.log(G.INFO, 'Decrypt binary failed.')
            return
        
        echo_str = "{} Binary Info:".format(app.display_name.encode('utf-8').strip())
        G.log(G.INFO, echo_str)
        print "Encrypt         :", "True" if app.app_binary.is_encrypt() else "False"
        print "Cryptid         :", app.app_binary.get_cryptid()
        print "PIE             :", "True" if app.app_binary.is_PIE_set() else "False"
        print "ARC             :", "True" if app.app_binary.is_ARC_set() else "False"
        print "Stack Canaries  :", "True" if app.app_binary.is_stack_canaries_set() else "False"
        #print "\n"
        
    
    #----------------------------------------------------------------------
    def dump_binary(self, bundle_id, path):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
    
        src = app.dump_binary()
        if src is None:
            G.log(G.INFO, 'Dump binary failed.')
            return
        dst = os.path.abspath(os.path.expanduser(path))
        '''
        if os.path.isdir(path) is True:
            if str(path).endswith(os.pathsep):
                save_path =  path + os.path.basename(app.app_binary.local_path)
            else:
                save_path =  path + os.pathsep + os.path.basename(app.app_binary.local_path)
        '''
        
        #python mv file
        #os.rename("path/to/current/file.foo", "path/to/new/desination/for/file.foo")
        #shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
        
        dest_tmp = None
        try:
            shutil.copy2(src, dst)
            if os.path.isdir(dst):
                dest_tmp = os.path.join(dst, os.path.basename(src))
                #print "Binary dump complete.Dump file:{}".format(os.path.join(dst, os.path.basename(src)))
            else:
                dest_tmp = dst
                #print "Binary dump complete.Dump file:{}".format(dst)
        except IOError as err:
            G.log(G.ERROR, "No such file or dic:\'{}.\'".format(path))
            return 
        
        G.log(G.INFO, "Dump binary to \'{}\' success.'".format(dest_tmp))
        
        if dest_tmp is not None:
            G.log(G.INFO, "Trying to non-Fat binary....")
            LocalUtils().nonFat(dest_tmp, None)


    #----------------------------------------------------------------------
    def dump_ipa(self, bundle_id, path):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
            
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        src = app.dump_ipa()
        if src is None:
            G.log(G.INFO, "Dump ipa failed.\n")
            return 
        
        dst = os.path.abspath(os.path.expanduser(path))
        try:
            shutil.copy2(src, dst)
            if os.path.isdir(dst):
                G.log(G.INFO, "Dump to \'{}\' success.".format(os.path.join(dst, os.path.basename(src))))
            else:
                G.log(G.INFO, "Dump to \'{}\' success.".format(dst))
        except IOError as err:
            G.log(G.ERROR, "No such file or dic \'{}\'".format(path))
        

    #----------------------------------------------------------------------
    def list_starage_by_bundle_id(self, bundle_id):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        storages = app.find_all_storages()
        all_plists = storages["all_plists"]
        all_sqlites = storages["all_sqlites"]
        
        if all_plists is not None:
            echo_str = "{}'s All plists:".format(app.display_name.encode('utf-8').strip())
            G.log(G.INFO, echo_str)
            for p in all_plists:
                if p.startswith(app.app_dir):
                    tmp = re.sub(app.app_dir, "[APP BUNDLE]", p[:-1])
                elif p.startswith(app.data_dir):
                    tmp = re.sub(app.data_dir, "[APP DATA]", p[:-1])
                print tmp
        else:
            echo_str = "{} has no plist file.".format(app.display_name.encode('utf-8').strip())
            G.log(G.INFO, echo_str)
    
        if all_sqlites is not None:
            echo_str = "{}'s All sqlite:".format(app.display_name.encode('utf-8').strip())
            G.log(G.INFO, echo_str)
            for p in all_sqlites:
                if p.startswith(app.app_dir):
                    tmp = re.sub(app.app_dir, "[APP BUNDLE]", p[:-1])
                elif p.startswith(app.data_dir):
                    tmp = re.sub(app.data_dir, "[APP DATA]", p[:-1])
                print tmp
        else:
            echo_str = "{} has no sqlite file.".format(app.display_name.encode('utf-8').strip())
            G.log(G.INFO, echo_str)
    

    #----------------------------------------------------------------------
    def view_plist_by_filename(self, bundle_id, filename):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        p = app.view_plist_by_filename(filename)
        if p is None:
            G.log(G.INFO, "This plist has no content.")
            return
        
        print json.dumps(p, indent=4)
        #print "\n"
    

    #----------------------------------------------------------------------
    def grep_storage_by_pattern(self, bundle_id, pattern, path=None):
        """"""
        
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return        
    
        l = app.grep_pattern_in_storage(pattern, path)
        for e in l:
            print e
        print ""
        
    
    #----------------------------------------------------------------------
    def exit_safely(self):
        """"""
        if self.device is not None:
            self.device.sshopt.ssh_close()
    

    
    #----------------------------------------------------------------------
    def view_sqlite_by_filename(self, bundle_id, filename):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        r = app.view_sqlite_by_filename(filename)
        for line in r:
            print line
            
            
    
    #----------------------------------------------------------------------
    def list_tablename_by_dbpath(self, bundle_id, dbpath):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        l = app.list_tables_by_dbpath(dbpath)
        echo_str = "All tables in {}:".format(dbpath)
        G.log(G.INFO, echo_str)
        echo_str = ""
        for e in l:
            echo_str += e[0]
            echo_str += "\n"
            
        print echo_str
        
        
    #----------------------------------------------------------------------
    def select_all_from_tablename(self, bundle_id, dbpath, tablename):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return        
        
        l = app.view_content_by_tablename(dbpath, tablename)
        echo_str = "All content in {}:".format(tablename)
        G.log(G.INFO, echo_str)
        for e in l:
            print e
        print ""
    
    
    #----------------------------------------------------------------------
    def grep_pattern_in_tablename(self, bundle_id, dbpath, tablename, pattern):
        """"""
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return        
    
        l = app.view_content_by_tablename(dbpath, tablename)
        echo_str = "\'{}\' match result:".format(pattern)
        G.log(G.INFO, echo_str)
        for e in l:
            if str(e).find(pattern) != -1:
                print e
        
        print ""
        
        
    
    #----------------------------------------------------------------------
    def grep_pattern_in_sqlite(self, bundle_id, pattern):
        """"""
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        app.grep_sqlite(pattern)
                        
        print ""
        
    
    #----------------------------------------------------------------------
    def grep_pattern_in_one_sqlite(self, bundle_id, pattern, sel_dbpath):
        """"""
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        #find all db 
        db_list = app.find_all_sqlite()
        
        if db_list is None:
            print "NO DB FILE FOUND."
            return 
        
        echo_str = "\'{}\' match result:".format(pattern)
        G.log(G.INFO, echo_str)
        
        for dbpath in db_list:
            if dbpath.find(sel_dbpath) != -1:
                table_list = app.list_tables_by_dbpath(dbpath)
                for tn in table_list:
                    l = app.view_content_by_tablename(dbpath, tn[0])
                    for e in l:
                        if str(e).find(pattern) != -1:
                            print dbpath, '=>\n', tn[0], '=>', e
                        
        print ""    
        
        
    #----------------------------------------------------------------------
    def read_binary_cookie(self, bundle_id=None):
        """"""
        if bundle_id is None:
            self.device.read_binary_cookie()
        else:
            #find app
            app = self.device.app_by_bundle_id(bundle_id)
        
            if app is None:
                echo_str = "Application {} not found.\n".format(bundle_id)
                G.log(G.INFO, echo_str)
                return 
        
            app.read_binary_cookie()
        
        print ''
        
        
    #----------------------------------------------------------------------
    def read_keyboard_cache(self, pattern=None):
        """"""        
        res = ''
        s = self.device.read_keyboard_cache()
        if pattern is None:
            G.log(G.INFO, "KeyBoard cache:")
            res = s
        else:
            print "\'{}\' found in KeyBoard cache:".format(pattern)
            #l = s.split(' ')
            l = filter(None, s.split(' '))
            for e in l:
                if str(e).find(pattern) != -1:
                    res += e
                    res += "\t"
                    
        print res, '\n'
        


    #----------------------------------------------------------------------
    def get_shared_libraries(self, bundle_id):
        """"""
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return

        if app.app_binary is None:
            if app.analyze_binary() == False:
                G.log(G.INFO, 'Can not find binary file.')
                return
        
        l = app.app_binary.otool.shared_library
        
        if l is None:
            G.log(G.INFO, "NO SHARED LIBRARY FOUND.")
            return 
        
        G.log(G.INFO, bundle_id + " shared libraries:")
        for e in l:
            print e
            
        print ""
        
    
    
    #----------------------------------------------------------------------
    def get_all_strings(self, bundle_id, pattern=None):
        """"""
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        if app.app_binary is None:
            if app.analyze_binary() == False:
                G.log(G.INFO, 'Can not find binary file.')
                return        
    
        s = app.app_binary.all_strings()
        if pattern is None:
            G.log(G.INFO, bundle_id + " strings:")
            print s, '\n'
        else:
            print "\'{}\' found in strings:".format(pattern)
            l = s.split('\n')
            for e in l:
                if str(e).find(pattern) != -1:
                    print str(e)
            print ''
            
    #----------------------------------------------------------------------
    def stop_thread_by_key(self, key):
        """"""
        if self.thread_dict == {} or not self.thread_dict.has_key(key):
            G.log(G.INFO, 'No thread to stop.')
        else:
            t_stop = self.thread_dict[key]
            t_stop.set()
            G.log(G.INFO, 'Success to stop thread \'{}\'.'.format(key))
        
    
    #----------------------------------------------------------------------
    def logging(self, _filter=None):
        """"""
        #import thread
        #thread.start_new(self.device.logging, (_filter,))
        
                
        import threading
        t_stop = threading.Event()
        t=threading.Thread(target=self.device.logging, args=(t_stop, _filter))
        t.start()
        
        self.thread_dict[G.LOG_THREAD] = t_stop
        #t_stop.set()
        G.log(G.INFO, 'Log thread is on. Thread name is: \'{}\''.format(G.LOG_THREAD))
        
        
        '''
        from threadutil import StoppableThread
        t = StoppableThread(target=self.device.logging, args=(_filter,))
        t.start()
        import time 
        time.sleep(10)
        t.stop()
        '''
        
        #self.device.logging(_filter)
        
    
    
    #----------------------------------------------------------------------
    def watch_pasteboard(self):
        """"""
        G.log(G.INFO, "init watcher...")
        self.device.watch_pasteboard()
        
        
        
    #----------------------------------------------------------------------
    def install_ipa(self, ipa_path):
        """"""
        
        r = self.device.install_ipa(os.path.abspath(os.path.expanduser(ipa_path)))
        
        if r == True:
            G.log(G.INFO, 'Install \'%s\' success.' % ipa_path)
        else:
            G.log(G.INFO, 'Install \'%s\' failed.' % ipa_path)
            
            
    
    #----------------------------------------------------------------------
    def launch_app(self, bundle_id):
        """"""
        flag, reason, pid = self.device.launch_app(bundle_id)
        
        if flag == True:
            G.log(G.INFO, 'Launch \'{}\' success.'.format(bundle_id))
            if pid == str(0):
                G.log(G.INFO, 'get pid failed.'.format(pid))
            else: 
                G.log(G.INFO, 'pid is {}.'.format(pid))
        else:
            G.log(G.INFO, reason)
            
        
    #----------------------------------------------------------------------
    def keychain_dump(self):
        """"""
        l = self.device.dump_keychain()
        if l is None:
            G.log(G.INFO, "Dump keychain error.\nPlease unlock your iPhone first.")
        else:
            print l
        
    
    
    #----------------------------------------------------------------------
    def keychain_edit(self, dataID, newData, with_base64=False):
        """"""
        r = self.device.edit_keychain(dataID, newData, with_base64)
        
        if r == True:
            G.log(G.INFO, "Edit keychain success.")
        else:
            G.log(G.INFO, "Edit keychain error.\nPlease unlock your iPhone first.")
            
    
    
    #----------------------------------------------------------------------
    def keychain_delete(self, dataID):
        """"""
        r = self.device.delete_keychain(dataID)
        
        if r == True:
            G.log(G.INFO, "Delete keychain success.")
        else:
            G.log(G.INFO, "Delete keychain error.\nPlease unlock your iPhone first.")
    
    
    
    #----------------------------------------------------------------------
    def keychain_grep(self, pattern):
        """"""
        r = self.device.grep_keychain(pattern)
        
        if r is None:
            G.log(G.INFO, "Search keychain failed.\nPlease unlock your iPhone first.")
        else:
            print r
        
        
    #----------------------------------------------------------------------
    def install_burp_cert(self):
        """"""
        G.log(G.INFO, 'Before install you may need to do as bellow:')
        print '1.Start burp suite on pc'
        print '2.Start proxy and choose \'All interface\''
        print '3.Proxy device to pc\n'
        
        r = self.device.CA_install_burp()
        
        if r == False:
            G.log(G.INFO, 'Install Failed.\nThe device os seems to be broken.')
        else:
            G.log(G.INFO, 'Go to device and press \'install\'')
            
            
    #----------------------------------------------------------------------
    def list_all_certs(self):
        """"""
        
        l = self.device.CA_list_cert()
        
        if l is None:
            G.log(G.INFO, 'List cert failed.')
        else:
            print l
        
        
    #----------------------------------------------------------------------
    def delete_cert_by_id(self, cert_id):
        """"""
        r = self.device.CA_delete_cert(cert_id)
        
        if r == True:
            G.log(G.INFO, 'Delete success.')
        else:
            G.log(G.INFO, 'Delete failed.')
            
            
    #----------------------------------------------------------------------
    def add_cert_by_path(self, path):
        """"""

        r = self.device.CA_add_cert(os.path.expanduser(path))
        
        if r == True:
            G.log(G.INFO, 'Import certificate success.')
        else:
            G.log(G.INFO, 'Import certificate failed.')
            
    
    #----------------------------------------------------------------------
    def export_cert(self, path):
        """"""
        r = self.device.CA_export_cert(os.path.abspath(os.path.expanduser(path)))
            
            
    #----------------------------------------------------------------------
    def fuzz_url_schema(self, bundle_id, template):
        """"""
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        app.fuzz_url_schema(template)
        
    
    #----------------------------------------------------------------------
    def check_env(self):
        """"""
        self.device.check_env()
        
        
    #----------------------------------------------------------------------
    def upload_file(self, local_path, remote_path):
        """"""
        '''
        if os.path.isdir(os.path.abspath(os.path.expanduser(remote_path))):
            if remote_path.endswith(os.path.sep):
                remote_path = "{}{}".format(remote_path, os.path.basename(local_path))
            else:
                remote_path = "{}{}{}".format(remote_path, os.path.sep, os.path.basename(local_path))        
        '''
        
        
        if self.device.minisftp.isdir(remote_path):
            '''
            #fix this stupid way to join path
            #just leave thease code to remind myself            
            if remote_path.endswith(os.path.sep):
                remote_path = "{}{}".format(remote_path, os.path.basename(local_path))
            else:
                remote_path = "{}{}{}".format(remote_path, os.path.sep, os.path.basename(local_path)) 
            '''
            remote_path = os.path.join(remote_path, os.path.basename(local_path))
        
        
        #check remote_file exists or not 
        #if exists, change remote file name until file not exists        
        idx = 0
        _remote_path = remote_path
        while self.device.minisftp.file_exists(_remote_path):
            tmp = _remote_path
            _remote_path = '_'.join([remote_path, str(idx)])
            idx += 1
            G.log(G.INFO, 'File \'{}\' already exists, try name: \'{}\'.'.format(tmp, _remote_path))
            
        r = self.device.minisftp.putfile(_remote_path, os.path.abspath(os.path.expanduser(local_path)), None)
        
        if r is not None:
            G.log(G.INFO, 'Upload file to \'{}\' success.'.format(_remote_path))
        else:
            G.log(G.INFO, 'Fail to upload file.')
    
    
    #----------------------------------------------------------------------
    def download_file(self, local_path, remote_path):
        """"""

        r = False
        
        if self.device.minisftp.isdir(remote_path):
            #G.log(G.INFO, 'Path \'{}\' is a dir, dir download is not support for now.'.format(remote_path))
            #G.log(G.INFO, 'Fail to download file.')
            path, r = self.download_dir(remote_path, local_path)
            return r
        
        if os.path.isdir(os.path.abspath(os.path.expanduser(local_path))):
            '''
            #fix this stupid way to join path
            #just leave thease code to remind myself
            if local_path.endswith(os.path.sep):
                local_path = "{}{}".format(local_path, os.path.basename(remote_path))
            else:
                local_path = "{}{}{}".format(local_path, os.path.sep, os.path.basename(remote_path))
            '''
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        
        #check local_file exists
        idx = 0
        _local_path = local_path
        while os.path.exists(_local_path):
            tmp = _local_path
            _local_path = '_'.join([local_path, str(idx)])
            idx += 1
            G.log(G.INFO, 'File \'{}\' already exists, try path: \'{}\'.'.format(tmp, _local_path))
        
        #check remote_file exists
        if not self.device.minisftp.file_exists(remote_path):
            G.log(G.INFO, 'File \'{}\' not exists.'.format(remote_path))
            r = False
        else:
            r = self.device.minisftp.getfile(remote_path, os.path.abspath(os.path.expanduser(_local_path)), None)
        
        if r is None:
            G.log(G.INFO, 'Download file to \'{}\' success.'.format(_local_path))
        else:
            G.log(G.INFO, 'Fail to download file.')
        
        return r
    
    
    #----------------------------------------------------------------------
    def get_panic_log(self, local_path, clearAfter=False, clearFirst=False):
        """"""
        #panic log path: /var/logs/CrashReporter/Panics/
        panic_path = '/var/logs/CrashReporter/Panics'
        if clearFirst:
            cmd = 'rm {}'.format(os.path.join(panic_path, '*.panic.ips'))
            self.device.sshopt.ssh_exec(cmd)
        '''
        #this way can download .panic.ips file one by one
        #not most effcient way
        #so we just download the whole dir of panic log 
        #as a zip file to local
        cmd = 'find {} -name \"{}\"'.format('/var/logs/CrashReporter/Panics/', '*.panic.ips')
        l = self.device.sshopt.ssh_exec(cmd)
        
        if l is None:
            G.log(G.INFO, 'NO panic log found.')
            return 
        
        for e in l:
            remote_path = e[:-1]
            x = os.path.basename(remote_path)
            local_path = os.path.join(local_path, x)
            
            self.device.minisftp.getfile(remote_path, local_path, None)
            G.log(G.INFO, 'Download panic log to \'{}\'.'.format(local_path))
        '''
        
        #download panic log dir 
        #as a zip file 
        #to local
        _local_path, r = self.device.download_dir(panic_path, os.path.expanduser(local_path), clearFirst=True, 
                                        clearAfter=True)
        
        if r is None:
            G.log(G.INFO, 'Success to get panic log to file \'%s\'' % _local_path)
        
        if clearAfter:
            cmd = 'rm {}'.format(os.path.join(panic_path, '*.panic.ips'))
            self.device.sshopt.ssh_exec(cmd)
        
        return True


    #----------------------------------------------------------------------
    def download_app_dict(self, bundle_id, dest_dict):
        """"""
        if dest_dict is None:
            G.log(G.INFO, 'Dest path is None.') 
            return 
        
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return 
        
        rtn = app.download_dict(os.path.expanduser(dest_dict))
        if rtn is None:
            G.log(G.INFO, 'Failed to download application:\'{}\'.'.format(bundle_id))
        else:
            G.log(G.INFO, 'Success to download application:\'{}\'.\nFile path: {}'.format(bundle_id, rtn))
    
    
    #----------------------------------------------------------------------
    def download_app_storage(self, bundle_id, dest_dict):
        """"""
        if dest_dict is None:
            G.log(G.INFO, 'Dest path is None.')
            return 
        
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return 
        
        rtn = app.download_storage(os.path.expanduser(dest_dict))
        if rtn is None:
            G.log(G.INFO, 'Failed to download storage of application:\'{}\'.'.format(bundle_id))
        else:
            G.log(G.INFO, 'Success to download storage of application:\'{}\'.\nFile path: {}'.format(bundle_id, rtn))
            
    
    #----------------------------------------------------------------------
    def crack_ipa_inpath(self, path, save_path):
        """"""
        #check check check
        if path is None:
            return None
        
        abpath = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(abpath):
            G.log(G.INFO, 'File \'{}\' not exist.')
            return None

        ipa_path_list = []
        
        #get ipa paths
        G.log(G.INFO, 'list each ipa paths.')
        if os.path.isdir(abpath):
            for f in os.listdir(abpath):
                fname = os.path.join(abpath, f)
                file_only = os.path.basename(fname)
                name_ext = os.path.splitext(file_only)
                #check extension for now
                #really need a new rigorous way to check ipa file
                #and this way have to be efficient
                if len(name_ext) == 2:
                    base_name = name_ext[0] 
                    file_ext = name_ext[1]
                    #only append .ipa files
                    if file_ext == '.ipa':
                        ipa_path_list.append(fname)
        elif os.path.isfile(abpath):
            ipa_path_list.append(abpath)
        else:
            pass

        if len(ipa_path_list) == 0:
            return None

        #cause we dont know the bundle_id of the newly installed ipa
        #we need get bundle_ids before and after installed 
        #so we can compare them to find out the newly installed bundle_ids
        #but list app opration need to refresh iOS uicache
        #it takes nearly 10 sec, sad T.T
        #hope to find out a much more efficient way
        
        #1.get bundle_ids before install
        G.log(G.INFO, 'list bundle_ids before installation.')
        app_list_before = self.device.install_app_list()
        app_bundleid_list_before = []
        for app in app_list_before:
            app_bundleid_list_before.append(app.bundle_identifier)
        
        #2.install ipas
        G.log(G.INFO, 'start installation.')
        for e in ipa_path_list:
            self.install_ipa(e)
        
        #3.get bundle_ids after install
        G.log(G.INFO, 'list bundle_ids after installation.')
        app_list_after = self.device.install_app_list()

        #4.get newly installed bundle_ids
        #5.dump ipa and binary
        #newly_bundle_ids = []
        G.log(G.INFO, 'get newly installed bundle_ids and dump it.')
        for app in app_list_after:
            if app.bundle_identifier not in app_bundleid_list_before:
                #newly_bundle_ids.append(bundle)
                self.dump_binary(app.bundle_identifier, save_path)
                self.dump_ipa(app.bundle_identifier, save_path)
                
        #done
        
        
    #----------------------------------------------------------------------
    def clear_cache(self):
        """"""
        #import shutil
        path = os.environ['HOME'] + "/.ihack/"
        if os.path.exists(path):
            shutil.rmtree(path)
        
        G.log(G.INFO, 'Clear cache complete.')
        
    
    #----------------------------------------------------------------------
    def clzdp(self, bundle_id, path):
        """"""
        #find app
        G.log(G.INFO, 'Check application exists...')
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        G.log(G.INFO, 'Dump binary...')
        binary_path = app.dump_binary()
        
        if os.path.isdir(os.path.abspath(os.path.expanduser(path))):
            if path.endswith(os.path.sep):
                path = "{}{}".format(path, bundle_id)
            else:
                path = "{}{}{}".format(path, os.path.sep, bundle_id)
                
        save_path = '{}.txt'.format(path)
        
        exec_path = os.path.split(os.path.realpath(__file__))[0]
        index = exec_path.rfind(os.path.sep) + 1
        
        class_dump = '{}bin{}class-dump'.format(exec_path[:index], os.path.sep)
        
        #cmd = '{} {} > {}'.format(class_dump, binary_path, os.path.abspath(os.path.expanduser(save_path)))
        G.log(G.INFO, 'Dump class...')
        cmd = [class_dump, binary_path]
        file_out = LocalUtils().run_process_in_background(cmd)
        
        stdout = file_out.communicate()[0]  #get output
        
        file_out.wait() #waitint for sub process over
        
        G.log(G.INFO, 'Save result...')
        try:
            with open(os.path.abspath(os.path.expanduser(save_path)), 'w+') as f:
                f.write(stdout)
            G.log(G.INFO, 'Class dump sucess and save to \'{}\''.format(save_path))
        except:
            G.log(G.ERROR, 'Save result error.')
            
        

        '''
        #waitint for sub process over
        import subprocess 
        while True:
            #line = file_out.stdout.readline()
            #print(line)
            if subprocess.Popen.poll(file_out)==0: #check sub thread over
                print 'sub process over'  
                break
        '''
    
    
    #----------------------------------------------------------------------
    def weak_classdump(self, bundle_id, path):
        """"""
        #find app
        G.log(G.INFO, 'Check application exists...')
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return        
        
        if os.path.isdir(os.path.abspath(os.path.expanduser(path))):
            if path.endswith(os.path.sep):
                path = "{}{}".format(path, bundle_id)
            else:
                path = "{}{}{}".format(path, os.path.sep, bundle_id)
        
        path = '{}_clz_dump.tar.gz'.format(path)
        res_path = WeakClassDump(app).dumpclz_download_result(os.path.abspath(os.path.expanduser(path)))
        
        G.log(G.INFO, 'Class dump sccess and check result at \'{}\'.'.format(path))
    
    
    #----------------------------------------------------------------------
    def get_pid_by_bundle_id(self, bundle_id):
        """"""
        #find app
        G.log(G.INFO, 'Check application exists...')
        app = self.device.app_by_bundle_id(bundle_id)
    
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            return
        
        pid = app.get_pid()
        
        if pid == str(0):
            G.log(G.INFO, 'Get pid failed, try \'lapp {}\' first.'.format(bundle_id))
        else:
            G.log(G.INFO, 'Get pid success, pid of \'{}\': {}'.format(bundle_id, pid))
            
            
    #----------------------------------------------------------------------
    def download_dir(self, remote_path, local_path, clearFirst=True, clearAfter=True):
        """"""
        #default to set clearFirst and clearAfter to True
        #maybe one day we need to change it with some conditions
        cf = clearFirst
        ca = clearAfter
        
        save_path, r = self.device.download_dir(remote_path, os.path.abspath(os.path.expanduser(local_path)), cf, ca)
        
        if r is not False:
            G.log(G.INFO, 'Successed download \'{}\' to \'{}\'.'.format(remote_path, save_path))
        else:
            G.log(G.INFO, 'Failed download \'{}\'.'.format(remote_path))
        
        return save_path, r
    
    
    #----------------------------------------------------------------------
    def cycript_file(self, bundle_id, cy_file):
        """"""
        if not os.path.exists(cy_file):
            G.log(G.INFO, 'Local file \'{}\' not exists.'.format(cy_file))
            return False
        
        if not os.path.isfile(cy_file):
            G.log(G.INFO, 'Local file \'{}\' is not a file.'.format(cy_file))
            return False
        
        #find app
        app = self.device.app_by_bundle_id(bundle_id)
        
        if app is None:
            echo_str = "Application {} not found.\n".format(bundle_id)
            G.log(G.INFO, echo_str)
            
        #launch application first anyway
        #to keep it at the top of system stack
        self.launch_app(bundle_id)
        pid = app.get_pid()
        
        r = CycriptUtil().run_cyfile(self.device, pid, cy_file)
        
        G.log(G.INFO, 'Success to run cy file \'{}\''.format(cy_file))
        
        return r
    
    
    #----------------------------------------------------------------------
    def find_application(self, pattern):
        """"""
        
        app = self.device.find_app_by_pattern(pattern)
        
        
        return app
    
    
    
    #----------------------------------------------------------------------
    def debugserver(self, pattern):
        """"""
        
        app = self.device.find_app_by_pattern(pattern)
        
        if app is None:
            G.log(G.INFO, 'Fail to find app \'%s\'.' % pattern)
            return False
        
        return app.debugserver()
        
        #return True
        
    
    
    #----------------------------------------------------------------------
    def resign(self, ipa_path):
        """"""
        pass
    
    
    #----------------------------------------------------------------------
    def resign_ipa(self, ipa_path, entitlements_path, mobileprovision_path, identity, sign_file=None):
        """"""
        G.log(G.INFO, 'Starting resign ipa file')
        
        new_ipa_path = LocalUtils().resign_ipa(os.path.abspath(os.path.expanduser(ipa_path)), 
                                            os.path.abspath(os.path.expanduser(entitlements_path)), 
                                            os.path.abspath(os.path.expanduser(mobileprovision_path)), 
                                            identity, 
                                            sign_file=None)
        
        if new_ipa_path is not None:
            G.log(G.INFO, 'Resign success, new ipa file: %s' % new_ipa_path)
            G.log(G.INFO, 'Try cmd: \'iipa\' to install new ipa file')
        else:
            G.log(G.INFO, 'Resign failed')
    
    
    #----------------------------------------------------------------------
    def inject_dylib_resign_install_ipa(self, ipa_path, entitlements_path, mobileprovision_path, identity, dylib):
        """
        1.inject dylib into an ipa
        2.resign ipa
        3.install ipa
        """
        new_ipa_path = LocalUtils().resign_ipa(ipa_path, entitlements_path, mobileprovision_path, identity, [dylib])
        
        if new_ipa_path is None:
            G.log(G.INFO, 'inject or resigin ipa file failed')
            return None
        else:
            self.install_ipa(new_ipa_path)
            return True
        
    
