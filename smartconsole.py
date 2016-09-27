

#author: june
#date: 12/25/2015

from lib.taskutil import *
from lib.locaUtil import *
from optparse import OptionParser
from lib.CommandUtil import switch
import lib.globals as G 


import atexit
import code
import os
import sys
import readline
import rlcompleter

#import logging
#LOG_FILENAME = '/tmp/completer.log'
#logging.basicConfig(filename=LOG_FILENAME,
#                    level=logging.DEBUG,
#                    )


class HistoryConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
    
        #readline.parse_and_bind("bind ^I rl_complete")
        
        # Register our completer function
        readline.set_completer(SimpleCompleter(G.cmmands.keys()).complete)
        
        
        #readline.set_completer(TabCompleter().complete)
        ### Add autocompletion
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind -e")
            readline.parse_and_bind("bind '\t' rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
        
        # Use the tab key for completion
        #readline.parse_and_bind('tab: complete')
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except:
                pass
            
            atexit.register(self.save_history, histfile)
            

    def save_history(self, histfile):
        readline.write_history_file(histfile)


class FileCacher:
    "Cache the stdout text so we can analyze it before returning it"
    def __init__(self): self.reset()
    def reset(self): self.out = []
    def write(self,line): self.out.append(line)
    def flush(self):
        output = '\n'.join(self.out)
        self.reset()
        return output


class Shell(HistoryConsole):
    "Wrapper around Python that can filter input/output to the shell"
    def __init__(self):
        self.stdout = sys.stdout
        self.cache = FileCacher()
        HistoryConsole.__init__(self)
        return

    def get_output(self): sys.stdout = self.cache
    def return_output(self): sys.stdout = self.stdout

    def push(self, line):
        self.get_output()
        # you can filter input here by doing something like
        # line = filter(line)
        code = HistoryConsole.push(self,line)
        self.return_output()
        output = self.cache.flush()
        # you can filter the output here by doing something like
        # output = filter(output)
        print output # or do something else with it
        return code
    
    #----------------------------------------------------------------------
    def wait_for_input(self):
        """"""
        line = raw_input(G.prompt)
        encoding = getattr(sys.stdin, "encoding", None)
        if encoding and not isinstance(line, unicode):
            line = line.decode(encoding)
            
        return line
    
    def interact(self, banner=None):

        task = None
        cmd = ''
        bundle_id = None
        
        while True:
            try:
                try:
                    line = raw_input(G.prompt)
                    
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and not isinstance(line, unicode):
                        line = line.decode(encoding)
                    
                    cmd = LocalUtils().resolve_cmd(line)#filter(None, line.split(' '))
                            
                    if len(cmd) < 1:
                        continue
                    
                    task, bundle_id = self.process_cmd(task, bundle_id, cmd)
                    
                except EOFError:
                    self.write("\n")
                    break
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
    

    
    #----------------------------------------------------------------------
    def all_in_one(self, task):
        """"""
        ssh = G.SSH_CONFIG
        bundle_id = G.BUNDLE_IDENTIFER
        if task is None:
            task = TaskUtil(ssh[0], ssh[1], ssh[2], ssh[3], ssh[4])
            if task.device.ssh is None:
                print 'Connect to device failed.'
                return None
            
        if G.CHENV_ENVIROMENT:
            task.check_env()
        
        if G.LIST_APPLICATION:
            print '===>List all applications...'
            task.list_app()
        
        if bundle_id is not None:
            print '===>Get detail info of app:\'{}\''.format(bundle_id)
            task.app_detail_info(bundle_id)
        
        if bundle_id is not None:
            print '===>Analyze binary...'
            task.analyze_binary(bundle_id)
        
        if bundle_id is not None and G.BINARY_DUMP_PATH is not None:
            print '===>Dump binary...'
            task.dump_binary(bundle_id, G.BINARY_DUMP_PATH)
        
        if bundle_id is not None and G.IPA_DUMP_PATH is not None:
            print '===>Dump ipa...'
            task.dump_ipa(bundle_id, G.IPA_DUMP_PATH)        
    
        if bundle_id is not None and G.STORAGE_GREP_PATTERNS.count > 0:
            print '===>Do search job...'
            for pattern in G.STORAGE_GREP_PATTERNS:
                task.grep_storage_by_pattern(bundle_id, pattern)
                task.keychain_grep(pattern)
                
        if bundle_id is not None and G.APP_DIR_SAVE_PATH is not None:
            print 'Downloading application...'
            task.download_app_dict(bundle_id, G.APP_DIR_SAVE_PATH)
    
        if bundle_id is not None and G.APP_STORAGE_SAVE_PATH is not None:
            print 'Downloading application storage...'
            task.download_app_storage(bundle_id, G.APP_STORAGE_SAVE_PATH) 
            
        return task

    
    #----------------------------------------------------------------------
    def process_cmd(self, task, bundle_id, _args):
        """"""

        for case in switch(_args[0]):
            if case('h'):
                pass
            if case('help'):
                cmds = []
                if len(_args) > 1:
                    cmds = _args[1:]
                LocalUtils().usage(cmds)
                break
            if case('ssh'):#connect device
                #task = TaskUtil(host, user, password, sftp_port)
                if len(_args) < 4 or len(_args) > 5:
                    G.log(G.INFO, G.WRONG_ARGS)
                    #print 'Wrong args.'
                    break
                host = _args[1]
                user = _args[2]
                password = _args[3]
                sftp_port = 22
                if len(_args) == 5:
                    sftp_port = int(_args[4])
                task = TaskUtil(host, user, password, sftp_port, "lan")
                if task.device is None:
                    task = None
                break
            if case('usb'):#connect device
                #task = TaskUtil(host, user, password, sftp_port)
                if len(_args) == 4:
                    user = _args[1]
                    password = _args[2]
                    if _args[3].isdigit():
                        sftp_port = int(_args[3])
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                elif len(_args) == 3:
                    user = _args[1]
                    password = _args[2]
                    sftp_port = 2222
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                host = '127.0.0.1'
                task = TaskUtil(host, user, password, sftp_port, "usb")
                if task.device is None:
                    task = None
                break
            if case('la'):#list application
                if task is not None:
                    task.list_app()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('sd'):#show app detail
                if task is not None:
                    #com.taobaobj.moneyshield
                    if  len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.app_detail_info(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)

                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('ab'):#analyze binary
                if task is not None:
                    #task.analyze_binary("com.taobaobj.moneyshield")
                    if len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.analyze_binary(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break 
            if case('las'):#list all starage file
                if task is not None:
                    #task.list_starage_by_bundle_id("com.taobaobj.moneyshield")
                    if len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.list_starage_by_bundle_id(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('vpl'):#view a plist file
                if task is not None:
                    #task.view_plist_by_filename("com.taobaobj.moneyshield", "/moneyshield.app/PlugIns/widget.appex/Info.plist")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        path = _args[2].decode("utf-8")
                    elif len(_args) == 2:
                        path = _args[1].decode("utf-8")
                    if bundle_id is not None:
                        task.view_plist_by_filename(bundle_id, path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gsp'):#grep pattern in a plist file
                if task is not None:
                    #task.grep_storage_by_pattern("com.taobaobj.moneyshield", "DTSDKName", "/moneyshield.app/PlugIns/widget.appex/Info.plist")
                    if len(_args) == 4:
                        bundle_id = _args[1]
                        pattern = _args[2]
                        path = _args[3]
                    elif len(_args) == 3:
                        pattern = _args[1]
                        path = _args[2]
                    if bundle_id is not None:
                        task.grep_storage_by_pattern(bundle_id, pattern, path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gs'):#grep pattern in all storage
                if task is not None:
                    #task.grep_storage_by_pattern("com.taobaobj.moneyshield", "DTSDKName")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        pattern = _args[2]
                    elif len(_args) == 2:
                        pattern = _args[1]
                    if bundle_id is not None:
                        task.grep_storage_by_pattern(bundle_id, pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('vdb'):#view all content of a db file
                if task is not None:
                    #task.view_sqlite_by_filename("com.taobaobj.moneyshield", "/Library/introspy-com.taobaobj.moneyshield.db")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        path = _args[2]
                    elif len(_args) == 2:
                        path = _args[1]
                    if bundle_id is not None:
                        task.view_sqlite_by_filename(bundle_id, path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('ltb'):#list tablename in a db file
                if task is not None:
                    #task.list_tablename_by_dbpath("com.taobaobj.moneyshield", "/Library/Caches/com.taobaobj.moneyshield/Cache.db")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        path = _args[2]
                    elif len(_args) == 2:
                        path = _args[1]
                    if bundle_id is not None:
                        task.list_tablename_by_dbpath(bundle_id, path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('vtb'):#view all content in a tablename
                if task is not None:
                    #task.select_all_from_tablename("com.taobaobj.moneyshield", "/Library/Caches/com.taobaobj.moneyshield/Cache.db", "cfurl_cache_response")
                    if len(_args) == 4:
                        bundle_id = _args[1]
                        path = _args[2]
                        tabname = _args[3]
                    elif len(_args) == 3:
                        path = _args[1]
                        tabname = _args[2]
                    if bundle_id is not None:
                        task.select_all_from_tablename(bundle_id, path, tabname)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gtb'):#grep pattern in a tablename
                if task is not None:
                    #task.grep_pattern_in_tablename(
                    #"com.taobaobj.moneyshield", 
                    #"/Library/Caches/com.taobaobj.moneyshield/Cache.db", 
                    #"cfurl_cache_response", 
                    #"aliyun")
                    if len(_args) == 5:
                        bundle_id = _args[1]
                        path = _args[2]
                        tabname = _args[3]
                        pattern = _args[4]
                    elif len(_args) == 4:
                        path = _args[1]
                        tabname = _args[2]
                        pattern = _args[3]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    if bundle_id is not None:
                        task.grep_pattern_in_tablename(bundle_id, path, tabname, pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gdbs'):#grep pattern in all db file
                if task is not None:
                    #task.grep_pattern_in_sqlite("com.taobaobj.moneyshield", "aliyun")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        pattern = _args[2]
                    elif len(_args) == 2:
                        pattern = _args[1]
                    if bundle_id is not None:
                        task.grep_pattern_in_sqlite(bundle_id, pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gdb'):#grep pattern in a db file
                if task is not None:
                    #task.grep_pattern_in_one_sqlite("com.taobaobj.moneyshield", "aliyun", "/Library/Caches/com.taobaobj.moneyshield/Cache.db")
                    if len(_args) == 4:
                        bundle_id = _args[1]
                        dbpath = _args[2]
                        pattern = _args[3]
                    elif len(_args) == 3:
                        dbpath = _args[1]
                        pattern = _args[2]
                    if bundle_id is not None:
                        task.grep_pattern_in_one_sqlite(bundle_id, pattern, dbpath)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('br'):#binary cookie reader
                if task is not None:
                    #task.read_binary_cookie()
                    task.read_binary_cookie()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('abr'):#application binary cookie reader
                if task is not None:
                    #task.read_binary_cookie("com.taobaobj.moneyshield")
                    if len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.read_binary_cookie(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('vkc'):#view keyboard cache
                if task is not None:
                    #task.read_keyboard_cache()
                    task.read_keyboard_cache()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('skc'):#search keyboard cache
                if task is not None:
                    #task.read_keyboard_cache("ert")
                    if len(_args) == 2:
                        pattern = _args[1]
                        task.read_keyboard_cache(pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('panic'):#search keyboard cache
                if task is not None:
                    #task.get_panic_log(local_path)
                    if len(_args) == 2:
                        local_path = _args[1]
                        task.get_panic_log(local_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break            
            if case('lsl'):#list shared libraries
                if task is not None:
                    #task.get_shared_libraries("com.taobaobj.moneyshield")
                    if len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.get_shared_libraries(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('lbs'):#list binary strings
                if task is not None:
                    #task.get_all_strings("com.taobaobj.moneyshield")
                    if len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.get_all_strings(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('gbs'):#grep pattern in binary strings
                if task is not None:
                    #task.get_all_strings("com.taobaobj.moneyshield", "webkit")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        pattern = _args[2]
                    elif len(_args) == 2:
                        pattern = _args[1]
                    if bundle_id is not None:
                        task.get_all_strings(bundle_id, pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('upload'):#upload file to device
                if task is not None:
                    #task.upload_file("/var/root/debugserver", "~/tmp/x.ipa")
                    if len(_args) == 3:
                        remote_path = _args[1]
                        local_path = _args[2]
                        task.upload_file(local_path, remote_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dnload'):#download file from device
                if task is not None:
                    #task.download_file('~/tmp/Clutch', '/var/root/Clutch1')
                    if len(_args) == 3:
                        remote_path = _args[1]
                        local_path = _args[2]
                        task.download_file(local_path, remote_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break            
            if case('log'):#logging
                if task is not None:
                    #task.logging()
                    _filter = None
                    if len(_args) == 2:
                        _filter = _args[1]
                    task.logging(_filter)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('wpb'):#watch pasteboard
                if task is not None:
                    #task.watch_pasteboard()
                    task.watch_pasteboard()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('kcd'):#keychain dump
                if task is not None:
                    #task.keychain_dump()
                    task.keychain_dump()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('kce'):#keychain edit
                if task is not None:
                    #task.keychain_edit("198", "12345678")
                    #task.keychain_edit("198", "MTIwNzEyMDdsdQ==", True)
                    base64 = False
                    if len(_args) == 4:
                        dataID = _args[1]
                        newData = _args[2]
                        if _args[3] == 'base64':
                            base64 = True
                    elif len(_args) == 3:
                        dataID = _args[1]
                        newData = _args[2]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    task.keychain_edit(dataID, newData, base64)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('kcdel'):#keychain delete
                if task is not None:
                    #task.keychain_delete("62")
                    if len(_args) == 2:
                        dataID = _args[1]
                        task.keychain_delete(dataID)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('kcs'):#keychain search pattern
                if task is not None:
                    #task.keychain_grep("xml")
                    if len(_args) == 2:
                        pattern = _args[1]
                        task.keychain_grep(pattern)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dbn'):#dump binary
                if task is not None:
                    #task.dump_binary("com.mimimix.tiaomabijia", "~/tmp/xxx")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        savePath = _args[2]
                    elif len(_args) == 2:
                        savePath = _args[1]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    task.dump_binary(bundle_id, savePath)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dipa'):#dump ipa
                if task is not None:
                    #task.dump_ipa("com.mimimix.tiaomabijia", "~/tmp/")
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        savePath = _args[2]
                    elif len(_args) == 2:
                        savePath = _args[1]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    task.dump_ipa(bundle_id, savePath)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('cipa'):#crach all ipa files in a folder
                if task is not None:
                    #task.crack_ipa_inpath('~/tmp/ipas', '~/tmp/dumppath')
                    if len(_args) == 3:
                        ipa_path = _args[1]
                        save_Path = _args[2]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    task.crack_ipa_inpath(ipa_path, save_Path)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('iipa'):#install ipa
                if task is not None:
                    #task.install_ipa("~/.ihack/C7E834A6-19DC-4A73-AC88-14B89F3D8620/com.mimimix.tiaomabijia.ipa")
                    if len(_args) == 2:
                        path = _args[1]
                        task.install_ipa(path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('lapp'):#launch application
                if task is not None:
                    #task.launch_app("com.mimimix.tiaomabijia")
                    if  len(_args) == 2:
                        bundle_id = _args[1]
                    if bundle_id is not None:
                        task.launch_app(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('ibca'):#install burp cert
                if task is not None:
                    task.install_burp_cert()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('lca'):#list all certs
                if task is not None:
                    task.list_all_certs()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dca'):#delete ca cert
                if task is not None:
                    #task.delete_cert_by_id("1")
                    if  len(_args) == 2:
                        cert_id = _args[1]
                        task.delete_cert_by_id(cert_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('aca'):#import cert to device
                if task is not None:
                    #task.add_cert_by_path("/Users/june/Downloads/cacert.der")
                    if  len(_args) == 2:
                        cert_path = _args[1]
                        task.add_cert_by_path(cert_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('pca'):#export cert to device
                if task is not None:
                    #task.export_cert('/Users/june/tmp/cert')
                    if  len(_args) == 2:
                        path = _args[1]
                        task.export_cert(path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break            
            if case('fus'):#fuzz url scheme
                if task is not None:
                    #task.fuzz_url_schema("com.taobaobj.moneyshield", 'qiandun://?token=%*%&registered=%*%')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        template = _args[2]
                    elif len(_args) == 2:
                        template = _args[1]
                    if bundle_id is not None:
                        task.fuzz_url_schema(bundle_id, template)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('chenv'):#check enviroment
                #check enviroment
                if task is not None:
                    task.check_env()
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('nonfat'):#parse Fat header file to non-Fat
                #non fat
                _output = None
                if len(_args) == 3:
                    _output = _args[2]
                    _input = _args[1]
                elif len(_args) == 2:
                    _input = _args[1]
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                LocalUtils().nonFat(_input, _output)
                break
            if case('mport'):#mapping local port to remote port
                #LocalUtils().mapping_port(12346, 12346)
                _output = None
                if len(_args) == 3:
                    local_port = int(_args[2])
                    remote_port = int(_args[1])
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                LocalUtils().mapping_port(remote_port, local_port)
                break            
            if case('dwa'):#download whole application
                if task is not None:
                    #task.download_app_dict('com.taobaobj.moneyshield', '~/tmp')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        dest_dict = _args[2]
                    elif len(_args) == 2:
                        dest_dict = _args[1]
                    if bundle_id is not None:
                        task.download_app_dict(bundle_id, dest_dict)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dws'):#download whole application storage
                if task is not None:
                    #task.download_app_storage('com.taobaobj.moneyshield', '~/tmp')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        dest_dict = _args[2]
                    elif len(_args) == 2:
                        dest_dict = _args[1]
                        
                    if bundle_id is not None:
                        task.download_app_storage(bundle_id, dest_dict)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('pid'):#get pid 
                if task is not None:
                    #task.get_pid_by_bundle_id('com.fotoable.pipcam')
                    if len(_args) == 2:
                        bundle_id = _args[1]
                        
                    if bundle_id is not None:
                        task.get_pid_by_bundle_id(bundle_id)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dbgsvr'):#debugserver on a process, waiting for debugger 
                if task is not None:
                    #task.debugserver('com.fotoable.pipcam')
                    if len(_args) == 2:
                        pattern = _args[1]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    task.debugserver(pattern)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break            
            if case('clzdp'):#class-dump 
                if task is not None:
                    #task.clzdp('cn.xiaochuankeji.tieba', '~/tmp/')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        save_path = _args[2]
                    elif len(_args) == 2:
                        save_path = _args[1]
                        
                    if bundle_id is not None:
                        task.clzdp(bundle_id, save_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('stop'):#stop thread
                if task is not None:
                    #task.stop_thread_by_key(key)
                    if len(_args) == 2:
                        key = _args[1]
                        task.stop_thread_by_key(key)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('wclzdp'):#weak_classdump 
                if task is not None:
                    #task.weak_classdump('cn.xiaochuankeji.tieba', '~/tmp/')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        save_path = _args[2]
                    elif len(_args) == 2:
                        save_path = _args[1]
                        
                    if bundle_id is not None:
                        task.weak_classdump(bundle_id, save_path)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('cycript'):#run cycript file on the remote device inside an application
                if task is not None:
                    #task.cycript_file('cn.xiaochuankeji.tieba', '~/tmp/test.cy')
                    if len(_args) == 3:
                        bundle_id = _args[1]
                        cy_file = _args[2]
                    elif len(_args) == 2:
                        cy_file = _args[1]
                    if bundle_id is not None:
                        task.cycript_file(bundle_id, cy_file)
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break
            if case('dlinj'):#inject a dylib into a binary
                #LocalUtils().inject_dylib_to_binary('~/tmp/xin.ipa', '~/tmp/libeeee.dylib')
                if len(_args) == 3:
                    binary = _args[1]
                    dylib = _args[2]
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                LocalUtils().inject_dylib_to_binary(binary, dylib)
                break
            if case('resign'):#resign an ipa file
                #LocalUtils().resign_ipa('~/tmp/xin.ipa', '~/tmp/entitlements.plist', '~/tmp/ios_development.mobileprovision', 'iPhone Developer: Name Name (xxxxxx)')
                if len(_args) == 5:
                    ipa_path = _args[1]
                    entitlements_path = _args[2]
                    mobileprovision_path = _args[3]
                    identity = _args[4]
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                LocalUtils().resign_ipa(ipa_path, entitlements_path, mobileprovision_path, identity)
                break
            if case('dlini'):#inject a dylib into an ipa file and resign 
                #LocalUtils().resign_ipa('~/tmp/xin.ipa', '~/tmp/entitlements.plist', '~/tmp/ios_development.mobileprovision', 'iPhone Developer: Name Name (xxxxxx)', '~/tmp/dylib')
                if len(_args) == 6:
                    ipa_path = _args[1]
                    entitlements_path = _args[2]
                    mobileprovision_path = _args[3]
                    identity = _args[4]
                    dylib = _args[5]
                else:
                    G.log(G.INFO, G.WRONG_ARGS)
                    break
                LocalUtils().resign_ipa(ipa_path, entitlements_path, mobileprovision_path, identity, [dylib])
                break
            if case('dlinji'):#inject a dylib into an ipa file, resign it, install it
                if task is not None:
                    #task.inject_dylib_resign_install_ipa('~/tmp/xin.ipa', '~/tmp/entitlements.plist', '~/tmp/ios_development.mobileprovision', 'iPhone Developer: Name Name (xxxxxx)')
                    if len(_args) == 6:
                        ipa_path = _args[1]
                        entitlements_path = _args[2]
                        mobileprovision_path = _args[3]
                        identity = _args[4]
                        dylib = _args[5]
                    else:
                        G.log(G.INFO, G.WRONG_ARGS)
                        break
                    task.inject_dylib_resign_install_ipa(ipa_path, entitlements_path, mobileprovision_path, identity, dylib)
                    break
                G.log(G.INFO, G.CONNECT_DEVICE_FIRST)
                break             
            if case('go'):#lazy is good.
                all_in_one(task)
                break
            if case('clche'):#clear local cache files
                task.clear_cache()
                break
            if case('e'):#quit
                pass            
            if case('exit'):#quit
                pass            
            if case('q'):#quit
                pass
            if case('quit'):#quit
                if task is not None:
                    task.exit_safely()
                G.log(G.INFO, 'Exit safely.')
                exit(0)
                break
            if case('cprt'):#copyright
                G.copyright()
                break
            if case(): # default, could also just omit condition or 'if True'
                G.log(G.INFO, "Command not support!")
                G.log(G.INFO, "Try \"help\".")
                
        return task, bundle_id
  
    

class SimpleCompleter(object):
    
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None

        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
                #logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.options[:]
                #logging.debug('(empty input) matches: %s', self.matches)
        
        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        #logging.debug('complete(%s, %s) => %s', repr(text), state, repr(response))
        return response
    



'''
#from: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
#for python tab completer, history cmd


import readline,rlcompleter
### Indenting
class TabCompleter(rlcompleter.Completer):
    """Completer that supports indenting"""
    def complete(self, text, state):
        if not text:
            return ('    ', None)[state]
        else:
            return rlcompleter.Completer.complete(self, text, state)

readline.set_completer(TabCompleter().complete)

### Add autocompletion
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind -e")
    readline.parse_and_bind("bind '\t' rl_complete")
else:
    readline.parse_and_bind("tab: complete")

### Add history
import os
histfile = os.path.join(os.environ["HOME"], ".pyhist")
try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)
del histfile

'''

