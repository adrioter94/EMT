#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 10:39:36 2019

@author: adrian
"""

from pyemtmad import Wrapper
from threading import Thread
import sys, time, pickle

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

# Devuelve los buses que estan circulando para una linea.
def get_buses(line):
    buses = []
    line_forward = []
    line_backward = []

    line_forward.append(line[0])
    for l in line[1:]:
        if l.distance_orig == 0:
            break
    
        line_forward.append(l)
        
    line_backward = line[len(line_forward):] 
        
    buses += get_buses_direction(line_backward)
            
    buses += get_buses_direction(line_forward)
    
    buses = clean_duplicates(buses)
    
    return buses

def get_buses_direction(line_direction):
    buses = []
    last_stop = line_direction[-1]
    
    while True:
        if len(buses) > 0:
            distance_next_stop = last_stop.distance_orig - buses[-1].distance
            if distance_next_stop < 0:
                break
        arrive_stop = wrapper.geo.get_arrive_stop(stop_number=last_stop.id, lang="es")
        if not arrive_stop[0]:
            return buses
            sys.exit("get_arrive_stop error: invalid Stop ID:")
            
        try:
            stop_line_id = unicode(int(last_stop.line))
        except:
            stop_line_id = last_stop.line
        
        for arrived in arrive_stop[1]:
            try:
                arrived_line_id = unicode(int(arrived.line_id))
            except:
                arrived_line_id = arrived.line_id

            if stop_line_id == arrived_line_id:
                distance_next_stop = last_stop.distance_orig - arrived.distance
                if distance_next_stop > 0:
#                    print ("Nuevo Bus añadido: " + str(arrived.bus_id) + ", Dist: " + str(arrived.distance) + ", Linea: " + str(arrived.line_id))
                    buses.append(arrived)
                else:
                    return buses
                    break
                
#       Si no hay buses en la linea, por ejemplo, nocturnos.      
        if not buses:
            return buses
        
        i = 0
        while line_direction[i].distance_orig < distance_next_stop:
            i += 1
            if i >= len(line_direction):
                return buses

        last_stop = line_direction[i-1]
        
    return buses

def clean_duplicates(buses):
    
    for bus in buses:
        if bus.distance <= 50:
            buses.remove(bus)
    return buses

if __name__ == "__main__":
    
    # Se accede a la API con el usuario y la clave.
    wrapper = Wrapper('WEB.SERV.adrianoter94@gmail.com', 'D488F32F-1559-428A-9325-B3AB69C0EEC5')
    
    lines = {}
    buses_lines = {}
    buses_lines_aux = []
  
    start_time = time.time()

#   Se cargan todas las lineas de bus
    lines_in = open("lines.pickle","rb")
    lines = pickle.load(lines_in)


#   Se calculan los buses
    threads = []
    start_time = time.time()
    for line_id, line in lines.items():
        twrv = ThreadWithReturnValue(target=get_buses, args=(line,))
        twrv.start()
        threads.append(twrv)    
    
    for th in threads:
        buses_lines_aux.append(th.join())
        
    for bus in buses_lines_aux:
#       Solo lineas que tengan buses actualmente
        if bus:
            buses_lines[bus[0].line_id] = bus

    print("--- %s seconds ---" % (time.time() - start_time))


#%%
import folium 
 
m = folium.Map(location=[40.4167278, -3.7033387], zoom_start=11)
 
for line, buses in buses_lines.items():
    for bus in buses:
        bus_id = str(bus.bus_id)
        folium.Marker([bus.latitude, bus.longitude], popup=bus_id).add_to(m)
 
m.save('buses.html')