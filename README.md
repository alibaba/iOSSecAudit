1.Installation

1.1 Mac OS X
1.1.1 pc env prepare
  1.  install python2.7
  2.  "sudo easy_install pip"
  3.  "sudo pip install paramiko"
  4.  "easy_install prettytable" or "easy_install -U prettytable"
  5.  "xcode-select --install", select “install”, then "agre..."
  6.  "brew install libimobiledevice", if don't have homebrew ,install it first: "ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null"
  7.  "git clone https://github.com/alibaba/iOSSecAudit.git"
  8.  cd /path/to/iOSSecAudit, "python main.py"

1.1.2 device env prepare
  1.  jailbreak iOS device
  2.  install cycript in Cydia
  

1.2 Linux or Windows
  
  Never test on Linux or Windows, cause i am tooooo lazy...
  
2.Usage

  Special Note: strongly suggest execute "chenv" after you connect to your device
  
  Usage:
  
 $ python main.py 
 
Type "help", "cprt" for more information.

\>\>\>help

[I]: Documented commands (type help [topic]):

ab 	abr 	aca 	br 	chenv 	cipa 	clche 	clzdp 	cprt 	cycript 	
dbgsvr 	dbn 	dca 	dipa 	dlini 	dlinj 	dlinji 	dnload 	dwa 	dws 	
e 	exit 	fus 	gbs 	gdb 	gdbs 	go 	gs 	gsp 	gtb 	
h 	help 	ibca 	iipa 	kcd 	kcdel 	kce 	kcs 	la 	lapp 	
las 	lbs 	lca 	log 	lsl 	ltb 	mport 	nonfat 	panic 	pca 	
pid 	q 	quit 	resign 	sd 	skc 	ssh 	stop 	upload 	usb 	
vdb 	vkc 	vpl 	vtb 	wclzdp 	wpb 	

[I]: try 'help [cmd0] [cmd1]...' or 'help all' for more infomation.

\>\>\>help ssh
ssh 	connect to device with ssh.
	args: [ip] [username] [password]
	example: 'ssh 10.1.1.1 root alpine'
\>\>\>help usb
usb 	ssh device over usb(Max OS X support only).
	args: [username] [password] [port]
	example: 'usb root alpine' or 'usb root alpine 2222'
\>\>\>help dlinji
dlinji 	inject a dylib into an ipa file, resign and install.
	args: [ipa_path] [entitlements_path] [mobileprovision_path] [identity] [dylib]
	example: 'dlini ~/tmp/xin.ipa ~/tmp/entitlements.plist ~/tmp/ios_development.mobileprovision 'iPhone Developer: Name Name (xxxxxx)' ~/tmp/libtest.dylib'
\>\>\>usb root xxroot
[E]: SSH Authentication failed when connecting to host
[I]: Connect failed.
\>\>\>usb root alpine
[I]: Connect success.
\>\>\>la
[I]: Refresh LastLaunchServicesMap...
[I]: All installed Applications:
0>.手机淘宝(com.taobao.taobao4iphone)
1>.Alilang(com.alibaba.alilang)
2>.微信(com.tencent.xin)
3>.putong(com.yaymedialabs.putong)
4>.支付宝(com.alipay.iphoneclient)
5>.条码二维码(com.mimimix.tiaomabijia)
6>.最右(cn.xiaochuankeji.tieba)
\>\>\>help las
las 	list all storage file of an application.
	args: [bundle_identifer]
	example: 'las com.taobaobj.moneyshield' or 'las'
\>\>\>help sd
sd 	show application detail.
	args: [bundle_identifer]
	example: 'sd com.taobaobj.moneyshield' or 'sd'
\>\>\>sd cn.xiaochuankeji.tieba
[I]: 最右 Detail Info:
Bundle ID       : cn.xiaochuankeji.tieba
UUID            : D9B2B45F-0D25-4F4F-B6A1-45B514BF4D4B
binary name     : tieba
Platform Version: 9.3
SDK Version     : iphoneos9.3
Mini OS         : 7.0
Data Directory  : 5D9B5BE7-A438-4057-8A88-4FDEA6FC2153
URL Hnadlers    : wx16516ad81c31d872
                  QQ41C6A3FB
                  tencent1103537147
                  zuiyou7a7569796f75
                  wb4117400114
Entitlements    :
	get-task-allow: 
	beta-reports-active: 
	aps-environment: production
	application-identifier: 3JDS7K3BCM.cn.xiaochuankeji.tieba
	com.apple.developer.team-identifier: 3JDS7K3BCM
	com.apple.security.application-groups:
