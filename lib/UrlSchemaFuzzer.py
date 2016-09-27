

#author: june
import itertools
import re
import os
import time
import copy


########################################################################
class UrlSchemaFuzzer:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.flag_bit = '%*%'
        self.crash_report_folder = "/var/mobile/Library/Logs/CrashReporter"
        self.testcase = [
          "A" * 10,
          "A" * 101,
          "A" * 1001,
          "\x00",
          "'",
          "%",
          "%n",
          "%@" * 20,
          "%n%d" * 20,
          "%s%p%x%d",
          "%x%x%x%x",
          "%#0123456x%08x%x%s%p%d%n%o%u%c%h%l%q%j%z%Z%t%i%e%g%f%a%C%S%08x%%",
  #        "100",
  #        "1000",
  #        "3fffffff",
  #        "7ffffffe",
  #        "7fffffff",
  #        "80000000",
  #        "fffffffe",
  #        "ffffffff",
  #        "10000",
  #        "100000",
           "0",
           "-1",
           "1",
        ]
        
    
    #----------------------------------------------------------------------
    def genarate_pocs(self, url):
        """"""
        pocs = []
        
        count = url.count(self.flag_bit)
        if count <= 0:
            return None
        
        l = itertools.product(self.testcase, repeat = count) #.combinations(self.testcase, count)
        
        for e in l:
            poc = copy.copy(url)
            
            for i in range(0, len(list(e))):
                poc = poc.replace(self.flag_bit, e[i], 1)
            
            pocs.append(poc)
            
        return pocs
    
    
    #----------------------------------------------------------------------
    def execute(self, poc, device, binary_name):
        """"""
        device.open_url(poc)
        
        time.sleep(5)
        
        device.kill_by_name(binary_name)
        
        l = device.sshopt.glob(self.crash_report_folder, "*")
        for e in l:
            if e.encode("utf-8").strip().find(binary_name) != -1:
                return True
        
        return False
    
    
    #----------------------------------------------------------------------
    def clear_old_crash(self, device, binary_name):
        """"""
        l = device.sshopt.glob(self.crash_report_folder, "*")
        for e in l:
            if e.encode("utf-8").strip().find(binary_name) != -1:
                cmd = "rm -f %s" % os.path.join(self.crash_report_folder, str(e))
                r = device.sshopt.ssh_exec(cmd)
                