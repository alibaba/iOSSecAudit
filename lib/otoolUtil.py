

#author: june


import os
import re
from abstracttool import Tool
import globals as G


########################################################################
class OtoolUtil(Tool):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, binary_path):
        """Constructor"""
        self.otool_path = "/usr/bin/otool"
        if not os.path.exists(self.otool_path):
            self.otool_path = None
            G.log(G.INFO, "otool not found.")
            
        self.binary_path = binary_path
        
        self.parse_load_commands()
        self.parse_shared_libraries()
        self.parse_header()
        self.process_symbol_table()
    
    
    #----------------------------------------------------------------------
    def parse_load_commands(self):
        """"""
        if self.otool_path is None:
            G.log(G.INFO, "otool not found.")
            return

        self.load_cmds = dict()
        
        cmd_load = "{} -l {}".format(self.otool_path, self.binary_path)
        buff = self.exec_shell(cmd_load)

        pattern_load_cmd = re.compile(r"Load command (\d+)")
        pattern_cmd_crypt = re.compile(r"\s*(cmd|cryptid)\s(.+)")
        
        l = buff.split("\n")
        for line in l:
            match_lc = pattern_load_cmd.match(line)
            if match_lc:
                command = dict()
                self.load_cmds[match_lc.group(1)] = command
                continue
            match_cc = pattern_cmd_crypt.match(line)
            if match_cc:
                command[match_cc.group(1)] = match_cc.group(2)
                
    
    
    #----------------------------------------------------------------------
    def parse_shared_libraries(self):
        """"""
        self.shared_library = list()
        
        if self.otool_path is None:
            G.log(G.INFO, "otool not found.")
            return        
        
        cmd_sl = "{} -L {}".format(self.otool_path, self.binary_path)
        buff = self.exec_shell(cmd_sl)
        
        l = buff.split("\n")
        for line in l[1:]:
            if line is not None:
                self.shared_library.append(line.strip())
                
        #print ""
            
    
    #----------------------------------------------------------------------
    def parse_header(self):
        """"""
        
        if self.otool_path is None:
            G.log(G.INFO, "otool not found.")
            return
        
        cmd = "{} -h {}".format(self.otool_path, self.binary_path)
        buff = self.exec_shell(cmd)
        
        pie_flag = 0x00200000
        v = buff.split("\n")[3]
        r_blank = v.rfind(" ")
        if r_blank == -1:
            G.log(G.INFO, "Check PIE flag error.")
            self.pie = False
            return False
        
        flags = int(v[r_blank:], 16)
        if flags & pie_flag == pie_flag:
            self.pie = True
        else:
            self.pie = False
        
        return self.pie
        
    
    #----------------------------------------------------------------------
    def process_symbol_table(self):
        """"""
        
        if self.otool_path is None:
            G.log(G.INFO, "otool not found.")
            return        
        
        cmd = "{} -I -v {}".format(self.otool_path, self.binary_path)
        buff = self.exec_shell(cmd)
        
        if buff.find("stack_chk_fail") != -1 or buff.find("stack_chk_guard") != -1:
            self.stack_canaries = True
        else:
            self.stack_canaries = False
            
        if buff.find("_objc_release") != -1:
            self.arc = True
        else:
            self.arc = False