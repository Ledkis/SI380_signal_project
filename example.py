#! /usr/bin/python

'''Try to implement the example in python'''

import PyWiiUse as wiiuse

import sys
import time
import os
import numpy as np
import scipy.io

nmotes = 1

def handle_event(wmp):
    wm = wmp[0]
    print '--- EVENT [wiimote id %i] ---' % wm.unid, wm.btns, wm.btns_held, wm.btns_released  
	
    if wm.btns:
        for name,b in wiiuse.button.items():
            if wiiuse.is_pressed(wm, b):
                print name,'pressed'

        if wiiuse.is_just_pressed(wm, wiiuse.button['-']):
            wiiuse.motion_sensing(wmp, 0)
        if wiiuse.is_just_pressed(wm, wiiuse.button['+']):
            wiiuse.motion_sensing(wmp, 1)
        if wiiuse.is_just_pressed(wm, wiiuse.button['B']):
            wiiuse.toggle_rumble(wmp)
        if wiiuse.is_just_pressed(wm, wiiuse.button['Up']):
            wiiuse.set_ir(wmp, 1)
        if wiiuse.is_just_pressed(wm, wiiuse.button['Down']):
            wiiuse.set_ir(wmp, 0)
    
    if wiiuse.using_acc(wm):
        print 'roll  = %f' % wm.orient.roll
        print 'pitch = %f' % wm.orient.pitch
        print 'yaw   = %f' % wm.orient.yaw
        print {'gx': wm.gforce.x,'gy': wm.gforce.y, 'gz': wm.gforce.z}
        print 'timestamp  = %f' % time.clock() 

    if wiiuse.using_ir(wm):
        for i in range(4):
            if wm.ir.dot[i].visible:
                print 'IR source %i: (%u, %u)' % (i, wm.ir.dot[i].x, wm.ir.dot[i].y)
        print 'IR cursor: (%u, %u)' % (wm.ir.x, wm.ir.y)
        print 'IR z distance: %f' % wm.ir.z

    if wm.exp.type == wiiuse.EXP_NUNCHUK:
        nc = wm.exp.u.nunchuk
        
        for name,b in wiiuse.nunchuk_button.items():
            if wiiuse.is_pressed(nc, b):
                print 'Nunchuk: %s is pressed' % name

        print 'nunchuk roll  = %f' % nc.orient.roll
        print 'nunchuk pitch = %f' % nc.orient.pitch
        print 'nunchuk yaw   = %f' % nc.orient.yaw
        print 'nunchuk joystick angle:     %f' % nc.js.ang
        print 'nunchuk joystick magnitude: %f' % nc.js.mag
    return {'acc':[wm.gforce.x, wm.gforce.y, wm.gforce.z], 'tim':time.clock()}

def handle_ctrl_status(wmp, attachment, speaker, ir, led, battery_level):
    wm = wmp[0]
    print '--- Controller Status [wiimote id %i] ---' % wm.unid
    print 'attachment', attachment
    print 'speaker', speaker
    print 'ir', ir
    print 'leds', led[0], led[1], led[2], led[3]
    print 'battery', battery_level

def handle_disconnect(wmp):
    print 'disconnect'

if os.name != 'nt': print 'Press 1&2'

wiimotes = wiiuse.init(nmotes, [1], handle_event, handle_ctrl_status, handle_disconnect)
print 'init complete'

found = wiiuse.find(wiimotes, nmotes, 5)
if not found:
    print 'not found'
    sys.exit(1)

connected = wiiuse.connect(wiimotes, nmotes)
if connected:
    print 'Connected to %i wiimotes (of %i found).' % (connected, found)
   
else:
    print 'failed to connect to any wiimote.'
    sys.exit(1)


for i in range(nmotes):
    wiiuse.set_leds(wiimotes[i], wiiuse.LED[i])
    wiiuse.rumble(wiimotes[i], 1)

time.sleep(0.2)

for i in range(nmotes):
    wiiuse.rumble(wiimotes[i], 0)

wiiuse.status(wiimotes[0])

# Main loop
try:
    glist = []
    tlist = []
    while True:
                
        if (wiiuse.poll(wiimotes, nmotes)):
            # Verification des actions
            for i in range(nmotes):
                dico = handle_event(wiimotes[i])
                gf = dico['acc']
                T = dico['tim']
                glist.append(gf)
                tlist.append(T)
except KeyboardInterrupt:
    for i in range(nmotes):
        wiiuse.set_leds(wiimotes[i], 0)
        wiiuse.disconnect(wiimotes[i])
        handle_disconnect(wiimotes[i])
# Convert list to array
x = np.array(glist, dtype=float)
y = np.array(tlist, dtype=float)
# Filename specification
matfile = 'data_mat1.mat'
# Save data
scipy.io.savemat(matfile, mdict={'out': x})
# time saving data
matfile = 'time_mat1.mat'
scipy.io.savemat(matfile, mdict={'out': y})
# load data
# matdata = scipy.io.loadmat(matfile)
# to get the matrix
# x = mat['out']
print 'done'
