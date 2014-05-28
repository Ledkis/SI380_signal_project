# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 15:40:15 2014

@author: Utilisateur
"""

import datetime

SPACE_LOG = 25
path = "log/"

log_name = "log"
log_path = "log/"
    

class mLog:
    
    def __init__(self, tag, log_file_name = None, first_msg = None):
        self.tag = tag.upper()
        if log_file_name is None:
            self.log_file_name = path+self.tag+".log"
        else:
            self.log_file_name = path+log_file_name+".log"

        if first_msg is None:
            first_msg = "<<< %s LOGFILE >>>"%(self.tag)
        
        try:
            log_file  = open(self.log_file_name, "w")
            log_file.write(self.get_time()+" "+first_msg+"\n")
        except:
            print("XXX")
        finally:
            log_file.close()
        
    def _write_log(self, msg, start = "", end = ""):
        
        
        try:
            log_file  = open(self.log_file_name, "a")
            log_file.write(start+msg+end)
        finally:
            log_file.close()
        
    def d(self, msg, tag = None, display=False):
        if tag is None:
            tag =  self.tag
        tmp = "%s %s -> %s"%(self.get_time(), tag.ljust(SPACE_LOG), msg.ljust(SPACE_LOG))
        if display:
            print(tmp)
        self._write_log(msg=tmp, end="\n")
        
    def read_log(self, size=10):
        
        log =""
        try:
            log_file = open(self.log_file_name, "r")
            log_l = log_file.read().split("\n")
            log_size = len(log_l)
            if size > log_size:
                log = "\n".join(log_l)
            else:
                i = log_size-size
                log = "\n".join(log_l[i:])
        finally:
            log_file.close()
            
        return log
        
    def get_time(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return "["+now+"]"
        
initialized = False
if not initialized:
    
    log = mLog("LOG")
    
    initialized = True
    

def d(tag, msg, debug = False):
    log.d(msg, tag, debug)
    
if __name__ == "__main__":
    pass
    d("TEST", "test")
    
            
        