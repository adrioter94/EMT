#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:04:55 2019

@author: adrian
"""

from pyemtmad import Wrapper
from threading import Thread
import datetime, time, sys
import pickle

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return
    
# Devuelve las paradas de una linea, con el formato qde paradas ue nos interesa 
def get_line(line_id):
        
    line = []
    
    now = datetime.datetime.now()
    route = wrapper.geo.get_route_lines_route(day=now.day, month=now.month, year=now.year, lines=line_id)
    if not route[0]:
        sys.exit("get_route_lines_route error: invalid Line ID")

    for stop in route[1]:
        if stop.name != None:
            line.append(stop);
    
    return line

def get_lines_ids(w):
    
    lines_id = []
    now = datetime.datetime.now()
    lines = w.bus.get_list_lines(day=now.day, month=now.month, year=now.year)
    if not lines[0]:
        sys.exit("get_list_lines: invalid date")
    
    for line in lines[1]:
        lines_id.append(line.line)
    
    return lines_id

    

if __name__ == "__main__":
    
    # Se accede a la API con el usuario y la clave.
    wrapper = Wrapper('WEB.SERV.adrianoter94@gmail.com', 'D488F32F-1559-428A-9325-B3AB69C0EEC5')
    
    # Line ID tiene que ser un string o int
    lines_aux = []
    lines = {}
    threads = []
    
    
    lines_id = get_lines_ids(wrapper)
    start_time = time.time()
    for line_id in lines_id:
        line = get_line(line_id)
        lines[line_id] = line
    print("--- %s seconds ---" % (time.time() - start_time))
    
    lines_out = open("lines.pickle","wb")
    pickle.dump(lines, lines_out)
    lines_out.close()




    
    
    