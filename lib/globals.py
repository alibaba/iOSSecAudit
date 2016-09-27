
#====================================================lazy mode============================================================

#check enviroment at first of first
CHENV_ENVIROMENT = False

#ssh config: ip, username, password, port, connect_way
#port must be integer value
#connect_way can be: 'usb' or 'lan'
SSH_CONFIG = ['127.0.0.1', 'root', '123456', 2222, 'usb']
#SSH_CONFIG = ['10.1.148.219', 'root', 'alpine', 22, 'lan']

#app bundle to analyze 
BUNDLE_IDENTIFER = 'com.mimimix.tiaomabijia'#'com.taobaobj.moneyshield'

#dump ipa file save path
IPA_DUMP_PATH = '~/tmp/test'

#dump binary file save path
BINARY_DUMP_PATH = '~/tmp/test'

#list all application first?
LIST_APPLICATION = True

#keyword to search in storage
STORAGE_GREP_PATTERNS = ['123456', 'password']

#ipa file path to be installed
INSTALL_IPA_PATH = None

#path of whole app directory
APP_DIR_SAVE_PATH = '~/tmp/test'

#path of whole app storage file
APP_STORAGE_SAVE_PATH = '~/tmp/test'

#DEBUG flag
DEBUGABLE = True

#====================================================lazy mode============================================================



#====================================================log============================================================
INFO = "i"
DEBUG = 'd'
ERROR = 'e'
WARING = 'w'
VERBOSE = 'v'

#----------------------------------------------------------------------
def log(label, content):
    """"""
    
    if DEBUGABLE == False:
        #log nothing
        return 
    
    if label == INFO:
        label = 'I'
    elif label == DEBUG:
        label = 'D'
    elif label == WARING:
        label = 'W'
    elif label == VERBOSE:
        label = 'V'
    elif label == ERROR:
        label = 'E'
    else:
        #log nothing
        return 
    
    result = "[%s]: %s" % (label, content)
    
    print result
    
    return result
#====================================================log============================================================


#====================================================copyright============================================================

#----------------------------------------------------------------------
def copyright():
    """"""
    print 'Copyright (c) 2015-2016 Alibaba Mobile Security @ June.\nAll Rights Reserved.\n'
    print 'Copyright (c) 2014-2015 Alibaba Mobile Security @ June.\nAll Rights Reserved.'

#====================================================copyright============================================================


#====================================================strings============================================================
WRONG_ARGS = 'Wrong args.'
CONNECT_DEVICE_FIRST = 'Please connect device first.'
prompt = ">>>"
cmd_count_per_line = 10
VERSION_CODE = 'v2.0'
CONSOLE_HISTORY = "~/.console-history"

AUTHOR_MAIL = 'by <xxjun3@gmail.com>'

DEFAULT_DEBUG_PORT = 12346
#====================================================strings============================================================


#====================================================thread name============================================================
LOG_THREAD = 'log'

#====================================================thread name============================================================





cmmands = {'help':'\tprint help message.\n\targs: [cmd0] [cmd1] [cmd2]...\n\texample: \'help ab abr\'',
           'h':'\tprint help message',
           'go':'\tlazy mode(config globals.py and go).\n\targs: no arg\n\texample: \'go\'',
           'usb':'\tssh device over usb(Max OS X support only).\n\targs: [username] [password] [port]\n\texample: \'usb root alpine\' or \'usb root alpine 2222\'',
           'ssh':'\tconnect to device with ssh.\n\targs: [ip] [username] [password]\n\texample: \'ssh 10.1.1.1 root alpine\'',
           'mport':'\tmapping local port to a remote port.\n\targs: [remote_port] [local_port]\n\texample: \'mport 12345 12345\'',
           'la':'\tlist all third party application.\n\targs: no arg\n\texample: \'la\'',
           'sd':'\tshow application detail.\n\targs: [bundle_identifer]\n\texample: \'sd com.taobaobj.moneyshield\' or \'sd\'',
           'ab':'\tanalyze binary and print result.\n\targs: [bundle_identifer]\n\texample: \'ab com.taobaobj.moneyshield\' or \'ab\'',
           'las':'\tlist all storage file of an application.\n\targs: [bundle_identifer]\n\texample: \'las com.taobaobj.moneyshield\' or \'las\'',
           'vpl':'\tview plist file.\n\targs: [bundle_identifer] [plist path]\n\texample: \'vpl com.taobaobj.moneyshield /moneyshield.app/PlugIns/widget.appex/Info.plist\'',
           'gsp':'\tgrep pattern in a plist file.\n\targs: [bundle_identifer] [pattern] [plist path]\n\texample: \'gsp com.taobaobj.moneyshield iphoneos /moneyshield.app/PlugIns/widget.appex/Info.plist\'',
           'gs':'\tgrep pattern in the storage of an application.\n\targs: [bundle_identifer] [pattern]\n\texample: \'gs com.taobaobj.moneyshield iphoneos\'',
           'vdb':'\tview the content of db file.\n\targs: [bundle_identifer] [db path]\n\texample: \'vdb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db\'',
           'ltb':'\tlist tablenames of db file.\n\targs: [bundle_identifer] [db path]\n\texample: \'ltb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db\'',
           'vtb':'\tview the content of a table in db file.\n\targs: [bundle_identifer] [db path] [tablename]\n\texample: \'vtb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db cfurl_cache_response\'',
           'gtb':'\tgrep pattern in a table.\n\targs: [bundle_identifer] [db path] [tablename] [pattern]\n\texample: \'gtb com.taobaobj.moneyshield /Library/introspy-com.taobaobj.moneyshield.db cfurl_cache_response aliyun\'',
           'gdbs':'\tgrep pattern in all db file.\n\targs: [bundle_identifer] [pattern]\n\texample: \'gdbs aliyun\'',
           'gdb':'\tgrep pattern in a db file.\n\targs: [bundle_identifer] [db path] [pattern]\n\texample: \'gdb /Library/Caches/com.taobaobj.moneyshield/Cache.db aliyun\'',
           'upload':'\tupload file to device.\n\targs: [remote_path] [local_path]\n\texample: \'upload \"/var/root/x.ipa\", \"~/tmp/x.ipa\"\'',
           'dnload':'\tdownload file from device.\n\targs: [remote_path] [local_path]\n\texample: \'dnload \"/var/root/x.ipa\", \"~/tmp/x.ipa\"\'',
           'br':'\tbinary cookie reader.\n\targs: no arg\n\texample: \'br\'',
           'abr':'\tapplication binary cookie reader.\n\targs: [bundle_identifer]\n\texample: \'abr com.taobaobj.moneyshield\'',
           'vkc':'\tview keyboard cache.\n\targs: no arg\n\texample: \'vkc\'',
           'skc':'\tsearch keyboard cache.\n\targs: [pattern]\n\texample: \'skc ert\'',
           'lsl':'\tlist shared libraries.\n\targs: [bundle_identifer]\n\texample: \'lsl com.taobaobj.moneyshield\'',
           'lbs':'\tlist binary strings.\n\targs: [bundle_identifer]\n\texample: \'lbs com.taobaobj.moneyshield\'',
           'gbs':'\tgrep pattern in binary strings.\n\targs: [bundle_identifer] [pattern]\n\texample: \'gbs com.taobaobj.moneyshield AES\'',
           'dwa':'\tdownload whole dir of an application.\n\targs: [bundle_identifer] [dest path]\n\texample: \'dwa com.taobaobj.moneyshield ~/tmp\'',
           'clzdp':'\tclass dump an application.\n\targs: [bundle_identifer] [save path]\n\texample: \'clzdp com.taobaobj.moneyshield ~/tmp\'',
           'wclzdp':'\tdump all header files of an application to local.\n\targs: [bundle_identifer] [save path]\n\texample: \'wclzdp com.taobaobj.moneyshield ~/tmp\'',
           'cycript':'\trun a cycript file in an application.\n\targs: [bundle_identifer] [cy path]\n\texample: \'cycript com.taobaobj.moneyshield ~/tmp/path.cy\'',
           'dws':'\tdownload all storage files of an application.\n\targs: [bundle_identifer] [dest path]\n\texample: \'dws com.taobaobj.moneyshield ~/tmp\'',
           'log':'\tlogging.\n\targs: [binary name]\n\texample: \'log moneyshield\'',
           'wpb':'\twatch pasteboard.\n\targs: no arg\n\texample: \'wpb\'',
           'kcd':'\tkeychain dump.\n\targs: no arg\n\texample: \'kcd\'',
           'kcs':'\tgrep pattern in keychain.\n\targs: [pattern]\n\texample: \'kcs 123456\'',
           'kce':'\tedit keychian record.\n\targs: [ID] [data] [base64]\n\texample: \'kce 198 MTIwNzEyMDdsdQ== base64\' or \'kce 198 12345678\'',
           'kcdel':'\tdelete keychian record.\n\targs: [ID]\n\texample: \'kcdel 198\'',
           'dbn':'\tdump binary.\n\targs: [bundle_identifer] [save path]\n\texample: \'dbn com.taobaobj.moneyshield ~/tmp/xxx\'',
           'cipa':'\tcrack ipas in path and save decrypted ipa in path.\n\targs: [ipas path] [save path]\n\texample: \'cipa ~/tmp/ipas, ~/tmp/dumppath\'',
           'dipa':'\tdump ipa.\n\targs: [bundle_identifer] [save path]\n\texample: \'dipa com.taobaobj.moneyshield ~/tmp/xxx\'',
           'iipa':'\tinstall ipa.\n\targs: [ipa path]\n\texample: \'iipa ~/tmp/com.taobaobj.moneyshield.ipa\'',
           'lapp':'\tlaunch application.\n\targs: [bundle_identifer]\n\texample: \'lapp com.taobaobj.moneyshield\'',
           'ibca':'\tinstall burp suite cert.\n\targs: no arg\n\texample: \'ibca\'',
           'lca':'\tlist all cert of device.\n\targs: no arg\n\texample: \'lca\'',
           'dca':'\tdelete cert by cert id.\n\targs: [cert id]\n\texample: \'dca 1\'',
           'aca':'\timport cert to device.\n\targs: [cert path]\n\texample: \'aca /Users/xx/Downloads/cacert.der\'',
           'pca':'\texport cert to local.\n\targs: [cert path]\n\texample: \'pca /Users/xx/tmp/cert\'',
           'fus':'\tfuzz url shema.\n\targs: [bundle_identifer] [urls]\n\texample: \'fus com.taobaobj.moneyshield\' \'qiandun://?token=%*%&registered=%*%\'',
           'nonfat':'\tparse Fat binary to non-Fat.\n\targs: [input_fils] [output_file]\n\texample: \'nonfat \'~/tmp/FleaMarket.decrypted\'\' or \'nonfat \'~/tmp/FleaMarket.decrypted\' \'~/tmp/\'\'',
           'clche':'\tclear local cache files.\n\targs: no arg\n\texample: \'clche\'',
           'pid':'\tget pid of an application.\n\targs: [bundle_identifer]\n\texample: \'pid com.taobaobj.moneyshield\'',
           'stop':'\tstop thread by name.\n\targs: [log/]\n\texample: \'stop log\'',
           'dbgsvr':'\tdebugserver on a process, waiting for debugger.\n\targs: [pattern]\n\texample: \'dbgsvr MobileSafari\'',
           'panic':'\tdownload panic log to local.\n\targs: [local_path]\n\texample: \'panic ~/tmp\'',
           'dlinj':'\tinject dylib into a binary.\n\targs: [binary_path] [dylib_path]\n\texample: \'dlinj ~/tmp/moneyshield ~/tmp/libtest.dylib\'',
           'resign':'\tresign an ipa file.\n\targs: [ipa_path] [entitlements_path] [mobileprovision_path] [identity]\n\texample: \'resign ~/tmp/xin.ipa ~/tmp/entitlements.plist ~/tmp/ios_development.mobileprovision iPhone Developer: Name Name (xxxxxx)\'',
           'dlini':'\tinject a dylib into an ipa file and resign.\n\targs: [ipa_path] [entitlements_path] [mobileprovision_path] [identity] [dylib]\n\texample: \'dlini ~/tmp/xin.ipa ~/tmp/entitlements.plist ~/tmp/ios_development.mobileprovision \'iPhone Developer: Name Name (xxxxxx)\' ~/tmp/libtest.dylib\'',
           'dlinji':'\tinject a dylib into an ipa file, resign and install.\n\targs: [ipa_path] [entitlements_path] [mobileprovision_path] [identity] [dylib]\n\texample: \'dlini ~/tmp/xin.ipa ~/tmp/entitlements.plist ~/tmp/ios_development.mobileprovision \'iPhone Developer: Name Name (xxxxxx)\' ~/tmp/libtest.dylib\'',
           'chenv':'\tcheck enviroment.',
           'quit':'\texit safely.',
           'exit':'\texit safely.',
           'q':'\texit safely.',
           'e':'\texit safely.',
           'cprt':'\tprint copyright message.'
           }




    