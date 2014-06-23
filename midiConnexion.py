# -*- coding:Utf-8 -*-
'''
Created on 23 sept. 2013

@author: Emile
'''

import midi
import m_log as Log

class MidiConnexion:
    """Pour ouvrir une connexion midi vers un cable virtuel et y envoyer des messages midi"""
    def __init__(self, outputName = b'LoopBe Internal MIDI'):
        
        self.outputName = outputName
        self.outputId = None
        self.devicesTable = []
        self.midiConnexionView = None
        self.midiConnexionListener = None
        self.isInit = False
        
        self.midiControllerTab = []
        
        self.TAG = "MidiConnexion"
        
        Log.d(self.TAG, "Initialized", True)

    
    def init_Connexion(self):
        """Initialize the midi module"""
        midi.init()
        self.nbrMidiDevice = midi.get_count()
        self.outputId = int(midi.get_default_output_id())
        self.init_DeviceTable()
        self.init_OutputId()
        self.isInit=True
        Log.d(self.TAG, 'Connexion initialized', True)
     
    def quit_Connexion(self):
        """Uninitialize the midi module"""
        midi.quit()
        self.isInit=False
        Log.d(self.TAG, 'Connexion uninitialized', True)
    
    def init_DeviceTable(self):
        self.devicesTable = []
        for i in range(0,self.nbrMidiDevice):
            self.devicesTable.append(midi.get_device_info(i))
            
    def init_OutputId(self):
        for device in self.devicesTable:
            if device[1] == self.outputName and device[3] == 1:
                self.outputId = self.devicesTable.index(device)
                break
            
    def addNewMidiController(self, midiController):
        self.midiControllerTab.append(midiController)
        
    def removeMidiController(self, midiController):
        self.midiControllerTab.remove(midiController)
        
    
    def send_Midi_Message(self, status = 9, channel = 1, parameter = 60, value = 100):
        if self.isInit==False:
            Log.d(self.TAG, 'The midi connexion has not been initialised', True)
            return
        if status <7 or status >15:
            Log.d(self.TAG, 'Status out of range, no midi message sent', True)
            return
        if channel < 1 or channel > 16:
            Log.d(self.TAG, 'Channel out of range, no midi message sent', True)
            return
        if parameter < 0 or parameter > 127:
            Log.d(self.TAG, 'Parameter out of range, no midi message sent', True)
            return
        if value < 0 or value > 127:
            Log.d(self.TAG, 'Value out of range, no midi message sent', True)
            return

        channel = channel-1
        status = (int(status) << 4) + int(channel)
        midi.Output(self.outputId).write([[[status, int(parameter), int(value)], 0]]) 
        Log.d(self.TAG, 'On output [%s], id [%s] midi message [status = %s, channel = %s, parameter = %s, value = %s] sent'%
                        (self.outputName, self.outputId, status >> 4, channel+1, parameter, value), True)
            
    def send_Note_Off(self, channel = 1, note = 60, velocity = 100): #1000
        self.send_Midi_Message(status=8, channel=channel, parameter=note, value=velocity) 
    
    def send_Note_On(self, channel = 1, note = 60, velocity = 100): #1001
        self.send_Midi_Message(status=9, channel=channel, parameter=note, value=velocity)
                               
    def send_Aftertouch(self, channel = 1, note = 60, pressure_value = 100): #1010
        self.send_Midi_Message(status=10, channel=channel, parameter=note, value=pressure_value)
        
    def send_ControlChange(self, channel = 1, controller = 7, value = 60): #1011
        self.send_Midi_Message(status=11, channel=channel, parameter=controller, value=value)
        
    def send_Default_ControlChange(self, value = 100): #1011
        self.send_Midi_Message(status=12, channel=1, parameter=7, value=int(value))
        
    def send_ProgramChange(self, channel = 1, patch_number = 60, value = 100): #1100
        self.send_Midi_Message(status=13, channel=channel, parameter=patch_number, value=value)
        
    def send_ChannelAfterTouch(self, channel = 1, pressure_value = 60, value = 100): #1101
        self.send_Midi_Message(status=14, channel=channel, parameter=pressure_value, value=value)
        
    def send_PitchBend(self, channel = 1, lsb = 32, msb = 0): #1110
        self.send_Midi_Message(status=15, channel=channel, parameter=lsb, value=msb)
    
    def abort_Sending(self):
        """Terminates aoutgoing messages immediately"""
        midi.Output(self.outputId).abort()