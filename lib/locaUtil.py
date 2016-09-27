

#author: june

import os
import re
import subprocess
import uuid
from abstracttool import Tool
import globals as G
from CommandUtil import switch
from InfoPlistUtil import InfoPlistUtil


########################################################################
class LocalUtils(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(self.__class__, self).__init__()
    
    
    #----------------------------------------------------------------------
    def nonFat(self, binaryPath, savePath=None):
        """"""
        if binaryPath is None:
            G.log(G.INFO, 'binary path is None.')
            return 
        
        binaryPath = os.path.abspath(os.path.expanduser(binaryPath))
        
        if not self.local_file_exists(binaryPath):
            G.log(G.INFO, 'file \'%s\' not exists or not a file.'%binaryPath)
            return 
        
        
        if savePath is None:
            savePath = "{}.nonFat".format(binaryPath)
        
        binaryPath = os.path.abspath(os.path.expanduser(binaryPath))
        nonfat = os.path.join(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]), os.path.join('bin', 'nonFat'))
        cmd = '%s %s %s' % (nonfat, binaryPath, savePath)
        #cmd = "{}{}bin{}nonFat {} {}".format(os.getcwd(), os.path.sep, os.path.sep, binaryPath, savePath)
        
        G.log(G.INFO, self.exec_shell(cmd))
    
    
    #----------------------------------------------------------------------
    def run_process_in_background(self, cmd):
        """"""
        #file_out = subprocess.Popen(cmd)
        file_out = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return file_out
        
    #----------------------------------------------------------------------
    def active_usbmuxd(self, port):
        """"""        
        ps, nt = self.is_port_in_use(port)
        if ps and nt:
            #port is in use by self
            return True
        elif nt:# and ps == False
            G.log(G.INFO, "Port: {} already in use.".format(port))
            return False
        
        path = "{}{}".format(os.path.split(os.path.realpath(__file__))[0], "/pyusbmuxd/tcprelay.py")
        
        cmd = [os.path.abspath(os.path.expanduser(path)), "-t", "22:{}".format(port)]
        
        self.run_process_in_background(cmd)
        
        import time
        time.sleep(3)
        
        return True
    
    #----------------------------------------------------------------------
    def is_port_in_use(self, local_port, remote_port=22):
        """"""
        
        ps_res = self.exec_shell("ps aux|grep \'{}\'".format(local_port))
        nt_res = self.exec_shell("netstat -an | grep \'{}\'".format(local_port))
        
        
        if((nt_res.find("127.0.0.1.{}".format(local_port)) != -1)):
            nt = True
        else:
            nt = False
            
        if (ps_res.find("tcprelay.py -t {}:{}".format(remote_port, local_port)) != -1):
            ps = True
        else:
            ps = False
        
        return ps, nt
    
    
    #----------------------------------------------------------------------
    def mapping_port(self, remote_port, local_port):
        """"""
        ps, nt = self.is_port_in_use(remote_port, local_port)
        if ps and nt:
            #port is in use 
            G.log(G.INFO, "Local port: {} already in use.".format(local_port))
            return False
        
        path = "{}{}".format(os.path.split(os.path.realpath(__file__))[0], "/pyusbmuxd/tcprelay.py")
        
        cmd = [os.path.abspath(os.path.expanduser(path)), "-t", "{}:{}".format(remote_port, local_port)]
        
        self.run_process_in_background(cmd)
                
        import time
        time.sleep(3)
        
        G.log(G.INFO, "Mapping port {}:{} success.".format(remote_port, local_port))
        
        return True
    
    
    #----------------------------------------------------------------------
    def resolve_cmd(self, cmd):
        """
        trust me, i know exactly this is a stupid idea to resolve cmd
        but efficient and sample
        well, if u can not agree this idea
        bit me :)
        """
        
        _args = []
        regex = re.compile('\'(.*?)\'')
        match = regex.findall(cmd)
        regex = re.compile('"(.*?)"')
        match.extend(regex.findall(cmd))
        
        match = sorted(match)
        
        n = 0
        _cmd = re.sub('"', '', re.sub('\'', '', cmd))
        rpl_tab = {}
        while n<len(match):
            rpl = 'rpl_arg_place_holder_'+str(n)
            rpl_tab[rpl] = match[n]
            #to avoid reserved word in regx
            #we can't use re.sub
            #use replace instead
            #_cmd = re.sub(rpl_tab[rpl], rpl, _cmd, 1)
            _cmd = _cmd.replace(rpl_tab[rpl], rpl, 1)
            n += 1
        
        #filte space and none
        _args = filter(None, _cmd.split(' '))
        
        res = []
        for e in _args:
            if e in rpl_tab.keys():
                res.append(rpl_tab[e])
            else:
                res.append(e)
    
        return res     
    
    #----------------------------------------------------------------------
    def usage(self, cmds=[]):
        """"""
        if cmds == []:
            self.help_cmds_list()
        
        for cmd in cmds:
            if cmd == 'all':
                self.help_cmds_detail()
            else:
                for e in [k for k, v in G.cmmands.items() if str(k) == cmd]:
                    print e, G.cmmands[e]
          

    #----------------------------------------------------------------------
    def help_cmds_list(self):
        """""" 
        G.log(G.INFO, 'Documented commands (type help [topic]):')
        #for e in [k for (k,v) in G.cmmands.items()]:
        count = 0
        keys = G.cmmands.keys()
        keys.sort()

        for k in keys:
                
            print k, '\t',
            count += 1
            
            if count == G.cmd_count_per_line:
                count = 0
                print '\n',
        
        if count != 0:
            print '\n',
        
        G.log(G.INFO, 'try \'help [cmd0] [cmd1]...\' or \'help all\' for more infomation.')
            
    
    #----------------------------------------------------------------------
    def resign_ipa(self, ipa_path, entitlements_path, mobileprovision_path, identity, sign_file=None):
        """
        important: type(sign_file) should be []

        1.unzip ipa file
        2.remove old sign dictionary
        3.copy mobileprovision
        4.sign and inject all sign_file if sign_file is not None
        5.sign app
        6.verify sign
        7.zip as ipa
        8.return new signed ipa_path
        """
        
        ipa_path = os.path.abspath(os.path.expanduser(ipa_path))
        entitlements_path = os.path.abspath(os.path.expanduser(entitlements_path))
        mobileprovision_path = os.path.abspath(os.path.expanduser(mobileprovision_path))
        #check ipa_path, entitlements_path, mobileprovision_path exists and is file
        if not self.local_file_exists(ipa_path):
            G.log(G.INFO, 'File \'%s\' not exists or not a file.' % ipa_path)
            return None
        elif not self.local_file_exists(entitlements_path):
            G.log(G.INFO, 'File \'%s\' not exists or not a file.' % entitlements_path)
            return None
        elif not self.local_file_exists(mobileprovision_path):
            G.log(G.INFO, 'File \'%s\' not exists or not a file.' % mobileprovision_path)
            return None
        
        #mk temp dir
        basename = os.path.basename(ipa_path)
        cmd = '/usr/bin/mktemp -d %s' % os.path.join('/tmp', '_SecAutid_IPA_%s_%s' % (basename, uuid.uuid1()))
        r = self.exec_shell(cmd)
        tmp = r[:-1]
        
        #1.unzip ipa file
        G.log(G.INFO, 'unzip ipa file')
        cmd = 'cd %s && /usr/bin/unzip -q \'%s\'' % (tmp, ipa_path)
        r = self.exec_shell(cmd)
        
        #get *.app path
        app_tmp_path = None
        for f in os.listdir(os.path.join(tmp, 'Payload')):
            if f.endswith('.app'):
                app_tmp_path = os.path.join(tmp, os.path.join('Payload', f))
        
        if app_tmp_path is None:
            G.log(G.INFO, 'unzip error')
            return None
        
        #2.remove old sign dictionary
        G.log(G.INFO, 'remove old sign dictionary')
        old_sign_dir = os.path.join(app_tmp_path, '_CodeSignature')
        if os.path.exists(old_sign_dir):
            cmd = 'rm -rf %s' % (old_sign_dir)
            r = self.exec_shell(cmd)
            
        #3.copy mobileprovision
        G.log(G.INFO, 'copy mobileprovision')
        cmd = 'cp %s %s' % (mobileprovision_path, os.path.join(app_tmp_path, 'embedded.mobileprovision'))
        r = self.exec_shell(cmd)
        
        #4.sign and inject all sign_file if sign_file is not None
        if sign_file is not None:
            if type(sign_file) is list:
                G.log(G.INFO, 'sign all inject file')
                
                #find binary path
                info_plist = os.path.join(app_tmp_path, 'Info.plist')
                import shutil
                info_plist_path = os.path.join(tmp, 'Info.plist')
                shutil.copy2(info_plist, info_plist_path)
                info_plist_util = InfoPlistUtil(info_plist_path)
                binary_name = info_plist_util.get_property("CFBundleExecutable")
                binary_path = os.path.join(app_tmp_path, binary_name)                

                for f in sign_file:
                    #cp f Payload/WeChat.app/
                    #codesign -f -s 'iPhone Developer: Long Chen (3K54S797W6)' --entitlements entitlements.plist Payload/WeChat.app/libeeee.dylib
                    path = os.path.abspath(os.path.expanduser(f))
                    if self.local_file_exists(path):
                        #copy file into *.app
                        cmd = 'cp %s %s' % (path, app_tmp_path)
                        r = self.exec_shell(cmd)
                        #sign inject file
                        cmd = '/usr/bin/codesign -f -s \'%s\' --entitlements %s %s' % (identity, entitlements_path, os.path.join(app_tmp_path, os.path.basename(path)))
                        r = self.exec_shell(cmd)
                        #inject binary
                        self.inject_dylib_to_binary(binary_path, path)
                        
        #5.sign app
        G.log(G.INFO, 'sign app')
        #cmd: codesign -f -s 'iPhone Developer: Name Name (XXXXXXXX)' --entitlements entitlements.plist Payload/WeChat.app
        cmd = '/usr/bin/codesign -f -s \'%s\' --entitlements %s %s' % (identity, entitlements_path, app_tmp_path)
        r = self.exec_shell(cmd)
        
        #6.verify sign
        G.log(G.INFO, 'verify sign')
        cmd = '/usr/bin/codesign --verify %s' % app_tmp_path
        r = self.exec_shell(cmd)
        if r != '':
            G.log(G.INFO, 'verify sign failed')
            return None
        
        #7.zip as ipa
        G.log(G.INFO, 'zip new ipa file')
        new_signed_ipa = os.path.join(os.path.dirname(ipa_path), '%s.resigned.ipa'%basename)
        cmd = 'cd %s && /usr/bin/zip -qr %s %s' % (tmp, new_signed_ipa, 'Payload')
        r = self.exec_shell(cmd)
        
        G.log(G.INFO, 'Resign success')
        G.log(G.INFO, 'resigned ipa: %s' % new_signed_ipa)
        
        return new_signed_ipa
    
    
    #----------------------------------------------------------------------
    def inject_dylib_to_binary(self, binary, dylib):
        """
        1.macho header
        2.load commadns
        """
        
        binary = os.path.abspath(os.path.expanduser(binary))
        dylib = os.path.abspath(os.path.expanduser(dylib))
        
        if not self.local_file_exists(binary):
            G.log(G.INFO, 'file \'%s\' not exists or not a file.' % binary)
        elif not self.local_file_exists(dylib):
            G.log(G.INFO, 'file \'%s\' not exists or not a file.' % dylib)
            
        injector = os.path.join(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]), os.path.join('bin', 'dylib_injector'))
        cmd = '%s %s %s' % (injector, binary, dylib)
        
        G.log(G.INFO, self.exec_shell(cmd))
        
    
    #----------------------------------------------------------------------
    def inject_dylib_to_ipa(self, ipa, dylib):
        """
        1.unzip ipa
        2.find binary path
        3.inject dylib into binary
        4.zip ipa
        """
        ipa_path = os.path.abspath(os.path.expanduser(ipa))
        dylib_path = os.path.abspath(os.path.expanduser(dylib))
        
        if not self.local_file_exists(ipa_path):
            G.log(G.INFO, 'File \'%s\' not exists or not a file.' % ipa_path)
            return None
        elif not self.local_file_exists(dylib_path):
            G.log(G.INFO, 'File \'%s\' not exists or not a file.' % dylib_path)
            return None
        
        #mk temp dir
        basename = os.path.basename(ipa_path)
        cmd = '/usr/bin/mktemp -d %s' % os.path.join('/tmp', '_SecAutid_IPA_%s_%s' % (basename, uuid.uuid1()))
        r = self.exec_shell(cmd)
        tmp = r[:-1]
        
        #1.unzip ipa file
        G.log(G.INFO, 'unzip ipa file')
        cmd = 'cd %s && /usr/bin/unzip -q \'%s\'' % (tmp, ipa_path)
        r = self.exec_shell(cmd)
        
        #get *.app path
        app_tmp_path = None
        for f in os.listdir(os.path.join(tmp, 'Payload')):
            if f.endswith('.app'):
                app_tmp_path = os.path.join(tmp, os.path.join('Payload', f))
        
        if app_tmp_path is None:
            G.log(G.INFO, 'unzip error')
            return None        
        
        #2.find binary path
        info_plist = os.path.join(app_tmp_path, 'Info.plist')
        import shutil
        info_plist_path = os.path.join(tmp, 'Info.plist')
        shutil.copy2(info_plist, info_plist_path)
        info_plist_util = InfoPlistUtil(info_plist_path)
        binary_name = info_plist_util.get_property("CFBundleExecutable")
        binary_path = os.path.join(app_tmp_path, binary_name)
        
        #3.inject dylib into binary
        self.inject_dylib_to_binary(binary_path, dylib_path)
        
        #4.zip ipa
        G.log(G.INFO, 'zip new ipa file')
        new_ipa = os.path.join(os.path.dirname(ipa_path), '%s.new.ipa'%basename)
        cmd = 'cd %s && /usr/bin/zip -qr %s %s' % (tmp, new_ipa, 'Payload')
        r = self.exec_shell(cmd)
        
        G.log(G.INFO, 'inject success')
        G.log(G.INFO, 'new ipa: %s' % new_ipa)
        
        return new_ipa
    
    
    #----------------------------------------------------------------------
    def inject_dylib_and_resign_ipa(self, ipa, dylib, entitlements_path, mobileprovision_path, identity):
        """"""
        
        new_ipa = self.inject_dylib_to_ipa(ipa, dylib)
        
        if new_ipa is not None:
            self.resign_ipa(new_ipa, entitlements_path, mobileprovision_path, 
                       identity, [dylib])
    
    
    #----------------------------------------------------------------------
    def help_cmds_detail(self):
        """"""

        #for (k,v) in G.cmmands.items():
        #    print k, v
        for cmd in G.cmmands:
            print cmd, G.cmmands[cmd]
        '''
        print "Welcome to iOS Security Audit Tool v0.1.\n"
        print "Usage: [command] [arg] [arg] [arg]...\n"
        print "Commands:"
    
        print "help\tprint this help message"
    
        print "go\tlazy mode(config globals.py and go)."
        print "\targs: no arg"
        print "\texample: \'go\'"    
    
        print "usb\tssh device over usb(Max OS X support only)."
        print "\targs: [username] [password] [port]"
        print "\texample: \'usb root alpine\' or \'usb root alpine 2222\'"
    
        print "ssh\tconnect to device with ssh."
        print "\targs: [ip] [username] [password]"
        print "\texample: \'ssh 10.1.1.1 root alpine\'"  
    
        print "mport\tmapping local port to a remote port."
        print "\targs: [remote_port] [local_port]"
        print "\texample: \'mport 12345 12345\'"    
    
        print "la\tlist all third party application."
        print "\targs: no arg"
        print "\texample: \'la\'"
    
        print "sd\tshow application detail."
        print "\targs: [bundle_identifer]"
        print "\texample: \'sd com.taobaobj.moneyshield\' or \'sd\'"
    
        print "ab\tanalyze binary and print result."
        print "\targs: [bundle_identifer]"
        print "\texample: \'ab com.taobaobj.moneyshield\' or \'ab\'"
    
        print "las\tlist all storage file of an application."
        print "\targs: [bundle_identifer]"
        print "\texample: \'las com.taobaobj.moneyshield\' or \'las\'"
    
        print "vpl\tview plist file."
        print "\targs: [bundle_identifer] [plist path]"
        print "\texample: \'vpl com.taobaobj.moneyshield /moneyshield.app/PlugIns/widget.appex/Info.plist\'"
    
        print "gsp\tgrep pattern in a plist file."
        print "\targs: [bundle_identifer] [pattern] [plist path]"
        print "\texample: \'gsp com.taobaobj.moneyshield iphoneos /moneyshield.app/PlugIns/widget.appex/Info.plist\'"
    
        print "gs\tgrep pattern in the storage of an application."
        print "\targs: [bundle_identifer] [pattern]"
        print "\texample: \'gs com.taobaobj.moneyshield iphoneos\'"
    
        print "vdb\tview the content of db file."
        print "\targs: [bundle_identifer] [db path]"
        print "\texample: \'vdb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db\'"  
    
        print "ltb\tlist tablenames of db file."
        print "\targs: [bundle_identifer] [db path]"
        print "\texample: \'ltb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db\'"      
    
        print "vtb\tview the content of a table in db file."
        print "\targs: [bundle_identifer] [db path] [tablename]"
        print "\texample: \'vtb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db cfurl_cache_response\'" 
    
        print "gtb\tgrep pattern in a table."
        print "\targs: [bundle_identifer] [db path] [tablename] [pattern]"
        print "\texample: \'gtb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db cfurl_cache_response aliyun\'" 
    
        print "gdbs\tgrep pattern in all db file."
        print "\targs: [bundle_identifer] [pattern]"
        print "\texample: \'gdbs aliyun\'"
    
        print "gdb\tgrep pattern in a db file."
        print "\targs: [bundle_identifer] [db path] [pattern]"
        print "\texample: \'gdb /Library/Caches/com.taobaobj.moneyshield/Cache.db aliyun\'"
    
        print "upload\tupload file to device."
        print "\targs: [remote_path] [local_path]"
        print "\texample: \'upload \"/var/root/x.ipa\", \"~/tmp/x.ipa\"\'"
        
        print "\tdnload file from device."
        print "\targs: [remote_path] [local_path]"
        print "\texample: \'tdnload \"/var/root/x.ipa\", \"~/tmp/x.ipa\"\'"         
    
        print "br\tbinary cookie reader."
        print "\targs: no arg"
        print "\texample: \'br\'"
    
        print "abr\tapplication binary cookie reader."
        print "\targs: [bundle_identifer]"
        print "\texample: \'abr com.taobaobj.moneyshield\'" 
    
        print "vkc\tview keyboard cache."
        print "\targs: no arg"
        print "\texample: \'vkc\'"
    
        print "skc\tsearch keyboard cache."
        print "\targs: [pattern]"
        print "\texample: \'skc ert\'"
    
        print "lsl\tlist shared libraries."
        print "\targs: [bundle_identifer]"
        print "\texample: \'lsl com.taobaobj.moneyshield\'"    
    
        print "lbs\tlist binary strings."
        print "\targs: [bundle_identifer]"
        print "\texample: \'lbs com.taobaobj.moneyshield\'"   
    
        print "gbs\tgrep pattern in binary strings."
        print "\targs: [bundle_identifer] [pattern]"
        print "\texample: \'gbs com.taobaobj.moneyshield AES\'"
    
        print "dwa\tdownload whole dir of an application."
        print "\targs: [bundle_identifer] [dest path]"
        print "\texample: \'dwa com.taobaobj.moneyshield ~/tmp\'"  
    
        print "dws\tdownload all storage files of an application."
        print "\targs: [bundle_identifer] [dest path]"
        print "\texample: \'dws com.taobaobj.moneyshield ~/tmp\'"   
        
        print "clzdp\tclass dump an application."
        print "\targs: [bundle_identifer] [save path]"
        print "\texample: \'clzdp com.taobaobj.moneyshield ~/tmp\'"
        
        print "wclzdp\tdump all header files of an application to local."
        print "\targs: [bundle_identifer] [save path]"
        print "\texample: \'wclzdp com.taobaobj.moneyshield ~/tmp\'"        
    
        print "log\tlogging."
        print "\targs: [binary name]"
        print "\texample: \'log moneyshield\'"
    
        print "wpb\twatch pasteboard."
        print "\targs: no arg"
        print "\texample: \'wpb\'"
    
        print "kcd\tkeychain dump."
        print "\targs: no arg"
        print "\texample: \'kcd\'"
    
        print "kcs\tgrep pattern in keychain."
        print "\targs: [pattern]"
        print "\texample: \'kcs 123456\'"
    
        print "kce\tedit keychian record."
        print "\targs: [ID] [data] [base64]"
        print "\texample: \'kde 198 MTIwNzEyMDdsdQ== base64\' or \'kde 198 12345678\'" 
    
        print "kcdel\tdelete keychian record."
        print "\targs: [ID]"
        print "\texample: \'kcdel 198\'"
    
        print "dbn\tdump binary."
        print "\targs: [bundle_identifer] [save path]"
        print "\texample: \'dbn com.taobaobj.moneyshield ~/tmp/xxx\'"
    
        print "cipa\tcrack ipas in path and save decrypted ipa in path."
        print "\targs: [ipas path] [save path]"
        print "\texample: \'cipa ~/tmp/ipas, ~/tmp/dumppath\'"     
    
        print "dipa\tdump ipa."
        print "\targs: [bundle_identifer] [save path]"
        print "\texample: \'dipa com.taobaobj.moneyshield ~/tmp/xxx\'" 
    
        print "iipa\install ipa."
        print "\targs: [ipa path]"
        print "\texample: \'iipa ~/tmp/com.taobaobj.moneyshield.ipa\'"
    
        print "lapp\tlaunch application."
        print "\targs: [bundle_identifer]"
        print "\texample: \'lapp com.taobaobj.moneyshield\'"
    
        print "ibca\tinstall burp suite cert."
        print "\targs: no arg"
        print "\texample: \'ibca\'"
    
        print "lca\tlist all cert of device."
        print "\targs: no arg"
        print "\texample: \'lca\'"
    
        print "dca\tdelete cert by cert id."
        print "\targs: [cert id]"
        print "\texample: \'dca 1\'"
    
        print "aca\timport cert to device."
        print "\targs: [cert path]"
        print "\texample: \'aca /Users/xx/Downloads/cacert.der\'"
    
        print "pca\texport cert to local."
        print "\targs: [cert path]"
        print "\texample: \'pca /Users/xx/tmp/cert\'"    
    
        print "fus\tfuzz url shema."
        print "\targs: [bundle_identifer] [urls]"
        print "\texample: \'fus com.taobaobj.moneyshield\' \'qiandun://?token=%*%&registered=%*%\'"
    
        print "nonfat\tparse Fat binary to non-Fat."
        print "\targs: [input_fils] [output_file]"
        print "\texample: \'nonfat \'~/tmp/FleaMarket.decrypted\'\' or \'nonfat \'~/tmp/FleaMarket.decrypted\' \'~/tmp/\'\'"
    
        print "clche\tclear local cache files."
        print "\targs: no arg"
        print "\texample: \'clche\'"     
    
        print "chenv\tcheck enviroment."
    
        print "quit\texit safely."
    
        print "cprt\tprint copyright message."        
        '''
