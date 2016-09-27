
#author: june
import sys
import os
import re
import time
from abstracttool import Tool
#from app import Application
from PlistUtil import PlistUtil
from InfoPlistUtil import InfoPlistUtil
from ios8ServicesMap import IOS8LastLaunchServicesMap
from appbinary import AppBinary
from sqlite3Util import Sqlite3Util
from BinaryCookieReader import BinaryUtil
from UrlSchemaFuzzer import UrlSchemaFuzzer
import globals as G


########################################################################
class App(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, uuid, device):
        """Constructor"""
        super(self.__class__, self).__init__()
        self.uuid = uuid
        self.cache_dir = self.tmp_path() + self.uuid
        #mkdir
        self.mkdir_p(self.cache_dir)
        self.device = device
        self.app_dir = self.device.apps_dir + "/" + self.uuid
        info_plist_remote_path = self.info_plist_path()
        if info_plist_remote_path is None:
            self.binary_name = None
            return
        #download Info.plist and return local path
        info_plist_local_path = self.cache_file(info_plist_remote_path)
        #turn plist to dictionary
        self.info_plist_util = InfoPlistUtil(info_plist_local_path)
        #self.info_plist_dic = self.info_plist_util.plist2dic()
        self.binary_name = self.info_plist_util.get_property("CFBundleExecutable")#self.info_plist_dic["CFBundleExecutable"]
        self.bundle_identifier = self.info_plist_util.get_property("CFBundleIdentifier")#self.info_plist_dic["CFBundleIdentifier"]
        self.display_name = None
        self.get_display_name()
        self.data_directory()
        #self.url_handler()
        
        #url schema list
        self.url_schemas = []
        #all plists remote path list
        self.all_plists = list()
        #all sqlite3 remote path list
        self.all_sqlites = list()
        #plist_remote_path => plistUtil obj
        self.plist_util_obj_dict = dict()
        #sqlite_remote_path => plistUtil obj
        self.sqlite_util_obj_dict = dict()
        #binary object
        self.app_binary = None
        #ipa local path
        self.ipa_path = ''
        self.binary_remote_path = ''
        self.storages = {}
        #self.find_all_storages()
        self.pid = str(0)

    
    #----------------------------------------------------------------------
    def info_plist_path(self):
        """"""
        cmd = "ls {}/*.app/Info.plist".format(self.app_dir)
        info_plist_list = self.device.sshopt.ssh_exec(cmd)
        #get list length
        list_len = len(info_plist_list)
        #one uuid dir must have and only have one app and one Info.plist
        if list_len != 1:
            return None
        #check file exist
        if self.device.minisftp.file_exists(info_plist_list[0][:-1]):
            return info_plist_list[0][:-1]
        else:
            return None
    
    
    #----------------------------------------------------------------------
    def remote2cache_path(self, path):
        """"""
        
        #clutch binary dump path 
        if path.find("/var/tmp/clutch/") != -1 and path.find(self.bundle_identifier) != -1 and path.find(self.binary_name) != -1:
            tmp = self.binary_path()
            if tmp is None:
                return None
            path = tmp + ".decrypt"
        
        #clutch ipa dump path
        if path.find("/private/var/mobile/Documents/Dumped/") != -1 and path.find("ipa") != -1:
            path = os.path.sep + self.bundle_identifier + '.ipa'

        local_path = self.cache_dir + re.sub("/private/var/mobile/Applications", "", re.sub("/private/var/mobile/Containers/Data/Application", "", re.sub(self.app_dir, "", path)))# os.path.basename(path)#os.path.dirname(tmp_path)
        #local_path = re.sub(".app", "_app", local_cache_dir)
        
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
    def platform_version(self):
        """"""
        self.platform_ver = self.info_plist_util.get_property("DTPlatformVersion")
        return self.platform_ver
    
    
    #----------------------------------------------------------------------
    def sdk_version(self):
        """"""
        self.sdk_ver = self.info_plist_util.get_property("DTSDKName")
        return self.sdk_ver
    
    
    #----------------------------------------------------------------------
    def mini_os_version(self):
        """"""
        self.mini_os_ver = self.info_plist_util.get_property("MinimumOSVersion")
        return self.mini_os_ver    
    
    
    #----------------------------------------------------------------------
    def get_display_name(self):
        """"""
        if self.display_name is None:
            self.display_name = self.info_plist_util.get_property("CFBundleDisplayName")
            if self.display_name is None:
                self.display_name = self.binary_name 
        
        return self.display_name

    
    #----------------------------------------------------------------------
    def url_handler(self):
        """"""
        if self.url_schemas == []:
            self.url_schemas = self.info_plist_util.url_handler()

        return self.url_schemas
    
    
    #----------------------------------------------------------------------
    def data_directory(self):
        """"""

        if self.device.ios_version == 8:
            remote_path = "/var/mobile/Library/MobileInstallation/LastLaunchServicesMap.plist"
            local_path = self.cache_file(remote_path)
            self.services_map = IOS8LastLaunchServicesMap(local_path)
            self.data_dir = self.services_map.data_dir_by_bundle_id(self.bundle_identifier)
            self.entitlement = self.services_map.entitlements_by_bundle_id(self.bundle_identifier)
        else:
            self.data_dir = self.app_dir
            self.entitlement = None
        
        return self.data_dir
    
    
    #----------------------------------------------------------------------
    def decrypt_binary_dylib(self):
        """"""
        #get remote binary path
        if self.binary_remote_path == '':
            if self.binary_path() is None:
                return None

        #DYLD_INSERT_LIBRARIES=dumpdecrypted_armv7.dylib binary_full_path=/private/var/mobile/Containers/Bundle/Application/BEB0E175-DAFF-4338-BCA6-A142321BBEE9/tiaomabijia.app/tiaomabijia
        cmd = 'DYLD_INSERT_LIBRARIES=dumpdecrypted_armv7.dylib {}'.format(self.binary_remote_path)
        remote_binary_decrypt_path = '/var/root/{}.decrypted'.format(self.binary_name)
        
        l = self.device.sshopt.ssh_exec(cmd)
        if  self.device.file_exists(remote_binary_decrypt_path) == False:
            cmd = 'DYLD_INSERT_LIBRARIES=dumpdecrypted_armv6.dylib {}'.format(self.binary_remote_path)
            l = self.device.sshopt.ssh_exec(cmd)
            if self.device.file_exists(remote_binary_decrypt_path) == False:
                return None
        
        return remote_binary_decrypt_path
        

    #----------------------------------------------------------------------
    def clutch_info(self):
        """"""
        cmd = '{} -i'.format(self.tool_path['Clutch'])
        r = self.device.sshopt.ssh_exec(cmd)
        
        if type(r) is list:
            for e in r:
                s = e[0:-1]
                #print isinstance(s, str)
                #print isinstance(s, unicode)
                #print s.encode('utf-8').strip()
                if s.encode('utf-8').strip().find(self.bundle_identifier) != -1:
                    return s.encode('utf-8').strip().split(':')[0]
        return None
    
    
    #----------------------------------------------------------------------
    def decrypt_binary_clutch(self, num):
        """"""
        #dump binary only: Clutch -b bundle_id
        cmd = "{} -b {}".format(self.tool_path['Clutch'], num)
    
        r = self.device.sshopt.ssh_exec(cmd)
        if type(r) is list:
            for e in r:
                s = e[0:-1]
                if s.encode('utf-8').strip().find('DONE: Finished dumping ') != -1:
                    if s.encode('utf-8').strip().find(self.bundle_identifier) != -1:
                        path = s[s.find('/'):]
                        remote_binary_decrypt_path = path + '/' + self.bundle_identifier + '/' + self.binary_name
                        return remote_binary_decrypt_path
            
        return None
    
    
    #----------------------------------------------------------------------
    def dump_binary(self):
        """"""
        '''
        #dump binary only: Clutch -b bundle_id
        cmd = "{} -b {}".format(self.tool_path['Clutch'], self.bundle_identifier)

        r = self.device.sshopt.ssh_exec(cmd)
        if type(r) is list:
            s = r[-1]
            if str(s).find('DONE: ') != -1 and str(s).find('/') != -1:
                path = str(s)[str(s).find('/'):-1]
                remote_binary_decrypt_path = path + '/' + self.bundle_identifier + '/' + self.binary_name
                self.decrypt_binary_path = self.cache_file(remote_binary_decrypt_path)
                return self.decrypt_binary_path
                '''
        
        num = self.clutch_info()
        
        if num is None:
            G.log(G.INFO, 'Application \'{}\' is not a encrypted app.'.format(self.bundle_identifier))
            return None
        
        remote_binary_decrypt_path = self.decrypt_binary_clutch(num)
        if remote_binary_decrypt_path is None:
            remote_binary_decrypt_path = self.decrypt_binary_dylib()
            if remote_binary_decrypt_path is None:
                return None
        
        self.decrypt_binary_path = self.cache_file(remote_binary_decrypt_path)
        
        return self.decrypt_binary_path



    #----------------------------------------------------------------------
    def dump_ipa(self):
        """"""
        if self.ipa_path != '':
            return self.ipa_path
        
        num = self.clutch_info()
                
        if num is None:
            G.log(G.INFO, 'Application \'{}\' is not a encrypt app.'.format(self.bundle_identifier))
            return None        
        
        #dump ipa: Clutch -d bundle_id
        cmd = "{} -d {}".format(self.tool_path['Clutch'], num)
        r = self.device.sshopt.ssh_exec(cmd)
        
        if type(r) is list:
            for e in r:
                s = e[0:-1]
                           
                if str(s).find('DONE: ') != -1 and str(s).find('/') != -1:
                    remote_ipa_path = str(s)[str(s).find('/'):]
                    self.ipa_path = self.cache_file(remote_ipa_path)
                    return self.ipa_path
        
        return None
        


    #----------------------------------------------------------------------
    def analyze_binary(self):
        """"""
        if self.app_binary is not None:
            return True
        
        if self.binary_path() is None:
            return False
    
        binary_local_path = self.cache_file(self.binary_remote_path)
        if binary_local_path is None:
            return False
        self.app_binary = AppBinary(binary_local_path)
    
        return True
    
    
    #----------------------------------------------------------------------
    def binary_path(self):
        """"""
        if self.binary_remote_path != '':
            return self.binary_remote_path
        
        cmd = "ls {}/*.app/{}".format(self.app_dir, self.binary_name.encode("utf-8").strip())
        binary_path_list = self.device.sshopt.ssh_exec(cmd)
        #get list length
        path_len = len(binary_path_list)
        #one uuid dir must have and only have one app and one Info.plist
        if path_len != 1:
            return None
        #check file exist
        self.binary_remote_path = binary_path_list[0][:-1]
        if self.device.minisftp.file_exists(self.binary_remote_path):
            return self.binary_remote_path
        else:
            return None
        

    #----------------------------------------------------------------------
    def find_all_storages(self):
        """"""
        if self.storages == {}:
            self.storages["all_plists"] = self.find_all_plists()
            self.storages["all_sqlites"] = self.find_all_sqlite()
        
        return self.storages
        
    
    def find_all_sqlite(self):
        self.all_sqlites = self.find_files_by_pattern("*.db")
        self.all_sqlites.extend(self.find_files_by_pattern("*.sqlite3"))
        return self.all_sqlites


    #----------------------------------------------------------------------
    def find_all_plists(self):
        """"""
        #list of all plist file path
        self.all_plists = self.find_files_by_pattern("*.plist")
        return self.all_plists
    
    
    #----------------------------------------------------------------------
    def find_files_by_pattern(self, pattern):
        """"""
        
        cmd = "find {} -name \"{}\"".format(self.app_dir, pattern)
        l = self.device.sshopt.ssh_exec(cmd)
        
        if self.device.ios_version == 8:
            cmd = "find {} -name \"{}\"".format(self.data_dir, pattern)
            l.extend(self.device.sshopt.ssh_exec(cmd))
        
        return l


    #----------------------------------------------------------------------
    def view_plist_by_filename(self, filename):
        """"""
        if self.storages == {}:
            self.find_all_storages()
        #if filename is not full name, process will just get the first match
        if self.all_plists is None:
            G.log(G.INFO, "plists is None.")
            return None
        
        #find remote file path
        path = None
        for p in self.all_plists:
            if p.find(filename) != -1:
                path = p
                break
                
        if path is None:
            G.log(G.INFO, "Can not find this plist file.")
            return None
        
        if path not in self.plist_util_obj_dict:
            #cache file and get local path
            #can not "path.encode('utf-8').strip()" here, this will cause a crash when path contain Chinese character
            local_path = self.cache_file(re.sub("\n", "", path))
            if local_path is None:
                return None
            plist_obj = PlistUtil(local_path)
            #plist_obj.view_detail()
            self.plist_util_obj_dict[path] = plist_obj
        
        
        return self.plist_util_obj_dict[path].dic
        

    #----------------------------------------------------------------------
    def grep_sqlite(self, pattern):
        """"""
        #find all db 
        db_list = self.find_all_sqlite()
    
        if db_list is None:
            G.log(G.INFO, "NO DB FILE FOUND.")
            return 
    
        echo_str = "\'{}\' match result:".format(pattern)
        G.log(G.INFO, echo_str)
    
        for dbpath in db_list:
            table_list = self.list_tables_by_dbpath(dbpath)
            if table_list is not None:
                for tn in table_list:
                    l = self.view_content_by_tablename(dbpath, tn[0])
                    for e in l:
                        if str(e).find(pattern) != -1:
                            path = re.sub(self.app_dir, '[APP DIR]', dbpath)
                            path = re.sub(self.data_dir, '[DATA DIR]', path)
                            print path, '=>\n', tn[0], '=>', e 
                        
    
    #----------------------------------------------------------------------
    def grep_plists(self, pattern, path=None):
        """"""
        if self.storages == {}:
            self.find_all_storages()
        
        if self.all_plists is None:
            G.log(G.INFO, "plists is None.")
            return None

        #the two lines below for :
        #UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-15: ordinal not in range(128)
        reload(sys)
        sys.setdefaultencoding("utf-8")
        
        result = list()
        
        #path is not None
        #grep in a singal plist file
        p_key = None
        if path is not None:
            #check path exists
            for e in self.all_plists:
                if e.find(path) != -1:
                    p_key = e
                    break
                
            if p_key is  None:
                G.log(G.INFO, "Plist file not found.")
                return None
            
            if p_key not in self.plist_util_obj_dict:
                local_path = self.cache_file(re.sub("\n", "", p_key.encode('utf-8').strip()))
                if local_path is None:
                    return None
                plist_obj = PlistUtil(local_path)
                self.plist_util_obj_dict[p_key] = plist_obj
                
            search_obj = self.plist_util_obj_dict[p_key].dic
            if pattern in search_obj:
                _path = re.sub(self.app_dir, '[APP DIR]', p_key)
                _path = re.sub(self.data_dir, '[DATA DIR]', p_key)                
                s = "{}=> {} : {}".format(_path, pattern, search_obj[pattern])
                result.append(s)
        
            for e in [k for k, v in search_obj.items() if (str(v).encode('utf-8').strip().find(pattern) != -1)]:
                _path = re.sub(self.app_dir, '[APP DIR]', p_key)
                _path = re.sub(self.data_dir, '[DATA DIR]', p_key)                 
                s = "{}=> {} : {}".format(_path, e, search_obj[e])
                result.append(s)            
            return result
        
        
        #path is None
        #grep in all plist files
        for p in self.all_plists:
            
            if p not in self.plist_util_obj_dict:
                local_path = self.cache_file(re.sub("\n", "", p.encode('utf-8').strip()))
                if local_path is None:
                    continue
                plist_obj = PlistUtil(local_path)
                self.plist_util_obj_dict[p] = plist_obj
                
            search_obj = self.plist_util_obj_dict[p].dic
            if search_obj is None:
                continue
            if pattern in search_obj:
                s = "{}=> {} : {}".format(p, pattern, search_obj[pattern])
                result.append(s)
                
            if type(search_obj) == list:
                for tmp_obj in search_obj:
                    if type(tmp_obj) == list:
                        for x in tmp_obj:
                            if type(x) == dict:
                                for e in [k for k, v in x.items() if (str(v).encode('utf-8').strip().find(pattern) != -1)]:
                                    _path = re.sub(self.app_dir, '[APP DIR]', p)
                                    _path = re.sub(self.data_dir, '[DATA DIR]', _path)                         
                                    s = "{}=> {} : {}".format(_path, e, search_obj[e])
                                    result.append(s)     
                            else:
                                if str(x).encode('utf-8').strip().find(pattern) != -1:
                                    _path = re.sub(self.app_dir, '[APP DIR]', p)
                                    _path = re.sub(self.data_dir, '[DATA DIR]', _path)                         
                                    s = "{}=> {} : {}".format(_path, e, search_obj[e])
                                    result.append(s)                              
                    elif type(tmp_obj) == dict:
                        for e in [k for k, v in tmp_obj.items() if (str(v).encode('utf-8').strip().find(pattern) != -1)]:
                            _path = re.sub(self.app_dir, '[APP DIR]', p)
                            _path = re.sub(self.data_dir, '[DATA DIR]', _path)                         
                            s = "{}=> {} : {}".format(_path, e, search_obj[e])
                            result.append(s)   
            elif type(search_obj) == dict:
                #take all search_obj as dict for now, may change at last
                for e in [k for k, v in search_obj.items() if (str(v).encode('utf-8').strip().find(pattern) != -1)]:
                    _path = re.sub(self.app_dir, '[APP DIR]', p)
                    _path = re.sub(self.data_dir, '[DATA DIR]', _path)                    
                    s = "{}=> {} : {}".format(_path, e, search_obj[e])
                    result.append(s)
            else:
                if (str(search_obj).encode('utf-8').strip().find(pattern) != -1):
                    _path = re.sub(self.app_dir, '[APP DIR]', p)
                    _path = re.sub(self.data_dir, '[DATA DIR]', _path)                    
                    s = "{}=> {}".format(_path, search_obj)
                    result.append(s)
        
        return result
    
     
    #----------------------------------------------------------------------
    def grep_sqlite_in_path(self, pattern, path):
        """"""
        sqlite_obj = self.find_sqlite_obj_by_path(path)
        
        
        
    #----------------------------------------------------------------------
    def list_tables_by_dbpath(self, dbpath):
        """"""
        '''
        if self.all_sqlites is None:
            print "sqlite is None."
            return None        
        
        #find remote file path
        path = None
        for p in self.all_sqlites:
            if p.find(dbpath) != -1:
                path = p
                break
    
        if path is None:
            print "Can not find this db file."
            return None
    
        if path not in self.sqlite_util_obj_dict:
            #cache file and get local path     
            local_path = self.cache_file(re.sub("\n", "", path.encode('utf-8').strip()))
            sqlite3_obj = Sqlite3Util(local_path)
            self.sqlite_util_obj_dict[path] = sqlite3_obj
        '''
        if self.storages == {}:
            self.find_all_storages()  
            
        obj = self.find_sqlite_obj_by_path(dbpath)
        if obj is not None:
            return obj.list_tables()
        else:
            return None
        
        
    
    #----------------------------------------------------------------------
    def view_sqlite_by_filename(self, filename):
        """"""
        if self.storages == {}:
            self.find_all_storages()        
        
        return self.find_sqlite_obj_by_path(filename).dump_db()
        
    
    
    
    #----------------------------------------------------------------------
    def view_content_by_tablename(self, dbpath, tablename):
        """"""

        if self.storages == {}:
            self.find_all_storages()
        
        sqlite_obj = self.find_sqlite_obj_by_path(dbpath)
        if sqlite_obj is not None:
            return sqlite_obj.select_all(tablename)
        else:
            return None
    
    
    #----------------------------------------------------------------------
    def grep_pattern_in_tablename(self, dbpath, tablename, pattern):
        """"""
        sqlite_obj = self.find_sqlite_obj_by_path(dbpath)
        if sqlite_obj is not None:
            return sqlite_obj.select_all(tablename)
        else:
            return None        
    
    
    #----------------------------------------------------------------------
    def find_sqlite_obj_by_path(self, filename):
        """"""
        if self.all_sqlites is None:
            G.log(G.INFO, "sqlite is None.")
            return None
        
        #find remote file path
        path = None
        for p in self.all_sqlites:
            if p.find(filename) != -1:
                path = p
                break
    
        if path is None:
            G.log(G.INFO, "Can not find this db file.")
            return None
    
        if path not in self.sqlite_util_obj_dict:
            #cache file and get local path     
            local_path = self.cache_file(re.sub("\n", "", path.encode('utf-8').strip()))
            if local_path is None:
                return None
            sqlite3_obj = Sqlite3Util(local_path)
            self.sqlite_util_obj_dict[path] = sqlite3_obj
        
        return self.sqlite_util_obj_dict[path]
    
    
    
    #----------------------------------------------------------------------
    def grep_pattern_in_storage(self, pattern, path=None):
        """"""
        if self.storages == {}:
            self.find_all_storages()        

        result  = list()
        
        self.grep_sqlite(pattern)
        
        l = self.grep_plists(pattern, path)
        if l is not None:
            result.extend(l)
       
        return result
    
    
    
    #----------------------------------------------------------------------
    def read_binary_cookie(self):
        """"""
        binary_cookie_remote_path = self.data_dir + '/Library/Cookies/Cookies.binarycookies'
        if self.device.file_exists(binary_cookie_remote_path):
            binary_cookie_path = self.cache_file(binary_cookie_remote_path)
            if binary_cookie_path is None:
                return None
            binary_cookie = BinaryUtil(binary_cookie_path)
            binary_cookie.read_binary_cookie()
        else:
            G.log(G.INFO, 'This application has no binarycookies file.')
        
        
    #----------------------------------------------------------------------
    def weak_classdump(self):
        """"""
        if not self.device.tool_installed(''):
            self.device.minisftp.putfile()
            
            
    #----------------------------------------------------------------------
    def fuzz_url_schema(self, template):
        """"""
        fuzzer = UrlSchemaFuzzer()
        fuzzer.clear_old_crash(self.device, self.binary_name)
        
        pocs = fuzzer.genarate_pocs(template)
        
        for poc in pocs:
            r = fuzzer.execute(poc, self.device, self.binary_name)
            if r == True:
                G.log(G.INFO, 'crashed: {}'.format(poc))
            else:
                G.log(G.INFO, 'no crash: {}'.format(poc))
                
    
    
    #----------------------------------------------------------------------
    def download_dict(self, dest_path):
        """"""
        if dest_path is None:
            G.log(G.INFO, 'Dest dir is None.')
            return None
        
        if not os.path.exists(dest_path):
            G.log(G.INFO, 'Dir \'{}\' not found.'.format(dest_path))
            return None

        if not self.device.tool_installed('tar'):
            G.log(G.INFO, 'Tool \'/usr/bin/tar\' not found on device.')
            return None
        
        #1>.cd to app dir
        #2>.tar cvf /var/root/AliDecices.tar ./*
        #3>.cd to data dir
        #4>.tar -rf /var/root/AliDecices.tar ./*
        #5>.gzip -c /var/root/AliDecices.tar
        #6>.cd back to home
        #7>.sftp pull remote file to local
        #8>.do clear job
        
        bundle_dir = self.app_dir
        data_dir = self.data_dir
        tar_name = '/var/root/{}.tar'.format(self.binary_name)
        gz_name = '{}.gz'.format(tar_name)
        local_path = os.path.join(dest_path, '{}.tar.gz'.format(self.binary_name))
        
        if self.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.device.sshopt.ssh_exec(cmd)
            
        if self.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.device.sshopt.ssh_exec(cmd)

        
        if self.device.ios_version == 8:
            G.log(G.INFO, 'Packet app dir of \'{}\'...'.format(self.bundle_identifier))
        else:
            G.log(G.INFO, 'Packet app & data dir of \'{}\'...'.format(self.bundle_identifier))
        cmd = 'cd \'{}\' && tar cvf {} ./*'.format(bundle_dir, tar_name)
        self.device.sshopt._ssh_exec(cmd)
        #time.sleep(5)
        
        if self.device.ios_version == 8:
            G.log(G.INFO, 'Packet data dir of \'{}\'...'.format(self.bundle_identifier))
            cmd = 'cd \'{}\' && tar -rf {} ./*'.format(data_dir, tar_name)
            self.device.sshopt._ssh_exec(cmd)
            #time.sleep(5)
        
        G.log(G.INFO, 'Gzip package...')
        cmd = 'cd ~ && gzip \'{}\''.format(tar_name)
        self.device.sshopt._ssh_exec(cmd)
        #time.sleep(10)
        
        G.log(G.INFO, 'Download package from device...')
        self.device.minisftp.getfile(gz_name, local_path, None)
        
        #do clear job
        G.log(G.INFO, 'Do clear job...')
        if self.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.device.sshopt.ssh_exec(cmd)
            
        if self.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.device.sshopt.ssh_exec(cmd)
        
        return local_path
    
    
    
    #----------------------------------------------------------------------
    def download_storage(self, dest_path):
        """"""
        if dest_path is None:
            G.log(G.INFO, 'Dest dir is None.')
            return None
        
        if not os.path.exists(dest_path):
            G.log(G.INFO, 'Dir \'{}\' not found.'.format(dest_path))
            return None

        if not self.device.tool_installed('tar'):
            G.log(G.INFO, 'Tool \'/usr/bin/tar\' not found on device.')
            return None

        #1>.cd to app dir
        #2>.tar cvf /var/root/AliDecices_storage.tar ./plist_path ./db_path
        #3>.cd to data dir
        #4>.tar -rf /var/root/AliDecices_storage.tar ./plist_path ./db_path
        #5>.gzip -c /var/root/AliDecices_storage.tar
        #6>.cd back to home
        #7>.sftp pull remote file to local
        #8>.do clear job
        
        bundle_dir = self.app_dir
        data_dir = self.data_dir
        tar_name = '/var/root/{}_storage.tar'.format(self.binary_name)
        gz_name = '{}.gz'.format(tar_name)
        local_path = os.path.join(dest_path, '{}_storage.tar.gz'.format(self.binary_name))
        
        if self.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.device.sshopt.ssh_exec(cmd)
            
        if self.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.device.sshopt.ssh_exec(cmd)
        
        G.log(G.INFO, 'Find all storage of application:\'{}\'...'.format(self.bundle_identifier))
        storages = self.find_all_storages()
        all_plists = storages["all_plists"]
        all_sqlites = storages["all_sqlites"]
        
        cmd_app_dir = 'tar cvf {}'.format(tar_name)
        cmd_data_dir = 'tar -rf {}'.format(tar_name)
        if all_plists is not None:
            for p in all_plists:
                if p.startswith(bundle_dir):
                    tmp = re.sub(bundle_dir, ".", p[:-1])
                    cmd_app_dir += ' {} '.format(tmp)
                elif p.startswith(data_dir):
                    tmp = re.sub(data_dir, ".", p[:-1])
                    cmd_data_dir += ' {} '.format(tmp)

        if all_sqlites is not None:
            for p in all_plists:
                if p.startswith(bundle_dir):
                    tmp = re.sub(bundle_dir, ".", p[:-1])
                    cmd_app_dir += ' {} '.format(tmp)
                elif p.startswith(data_dir):
                    tmp = re.sub(data_dir, ".", p[:-1])
                    cmd_data_dir += ' {} '.format(tmp)
        
        if self.device.ios_version == 8:
            G.log(G.INFO, 'Packet storage of \'{}\' in app dir...'.format(self.bundle_identifier))
        else:
            G.log(G.INFO, 'Packet storage dir of \'{}\' in app & data...'.format(self.bundle_identifier))

        cmd = 'cd \'{}\' && {}'.format(bundle_dir, cmd_app_dir)
        self.device.sshopt._ssh_exec(cmd)
        #time.sleep(5)
        
        if self.device.ios_version == 8:
            G.log(G.INFO, 'Packet storage of \'{}\' in data dir...'.format(self.bundle_identifier))
            cmd = 'cd \'{}\' && {}'.format(data_dir, cmd_data_dir)
            self.device.sshopt._ssh_exec(cmd)
                #time.sleep(5)
        
        G.log(G.INFO, 'Gzip package...')
        cmd = 'cd ~ && gzip \'{}\''.format(tar_name)
        self.device.sshopt._ssh_exec(cmd)
        #time.sleep(10)
        
        G.log(G.INFO, 'Download package from device...')
        self.device.minisftp.getfile(gz_name, local_path, None)
        
        #do clear job
        G.log(G.INFO, 'Do clear job...')
        if self.device.file_exists(tar_name):
            cmd = 'rm {}'.format(tar_name)
            self.device.sshopt.ssh_exec(cmd)
            
        if self.device.file_exists(gz_name):
            cmd = 'rm {}'.format(gz_name)
            self.device.sshopt.ssh_exec(cmd)
        
        return local_path
    
    
    
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
        cmd = 'ps aux| grep {} | grep {}'.format(self.uuid, self.binary_name)
        
        l =  self.device.sshopt.ssh_exec(cmd)
        
        path = re.sub("/private", "", self.binary_path())
        for e in l:
            if path in e:
                r = filter(None, e.split(' '))
                if len(r) > 1:
                    #USER PID %CPU %MEM VSZ RSS TT STAT STARTED TIME COMMAND
                    self.pid = r[1]
                
                break
        
        return self.pid
    
    
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
            debugserver = self.tool_path['debugserver61']
        else:
            debugserver = self.tool_path['debugserver84']
        
        if not self.device.tool_installed(debugserver):
            G.log(G.INFO, 'debugserver not installed.')
            return False
        
        #mapping port first 
        LocalUtils().mapping_port(port, port)
        
        #debugserver *:123456 -a 'MobileSafari'
        cmd = '{} *:{} -a \'{}\''.format(debugserver, str(port), self.binary_name)
        #self.device.sshopt.ssh_exec(cmd)

        #sleep here, waiting for application finish launch 
        #time.sleep(1)        

        import threading
        #t_stop = threading.Event()
        t = threading.Thread(target=self.device.sshopt.ssh_exec, args=(cmd, ))
        t.start()
        
        G.log(G.INFO, 'debugserver attach \'%s\' on \'%s\'.' %(self.binary_name, port))
        
        return True