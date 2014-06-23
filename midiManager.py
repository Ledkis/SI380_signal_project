# -*- coding:Utf-8 -*-
'''
Created on 23 sept. 2013

@author: Emile
'''

import m_log as Log

import midiConnexion 



class MidiManager:
    def __init__(self):
        self.midiNoteAbleton_Hm = init_Midi_Note_Hm('midiNoteAbleton.txt')
        self.midiNote_Hm = init_Midi_Note_Hm('midiNote.txt')
        self.control_Change_Hm = init_ControlChange_Hm()
        
        self.midiConnexion = midiConnexion.MidiConnexion()
        self.midiConnexion.init_Connexion()
        
        self.TAG = "MidiManager"    
        Log.d(self.TAG, 'MidiManager initialized', True)
        
def midi_Hm_To_SortedTuple(midi_Hm):
    seq = [(mmap,midi_Hm[mmap])  for mmap in midi_Hm.keys()]
    return list(sorted(seq, key = lambda x: x[1]))

def init_Midi_Note_Hm(source):
    """Initialiser un dictionnaire nom de la note / valeur à partir d'un fichier text"""
    return dict((lambda x: (x[0], int(x[1])))(el.split(";")) for el in open(source, 'r').read().split("\n") if el.split(";") != '')

def init_ControlChange_Hm():
    """Initialiser un dictionnaire control change / valeur"""
    return dict(('CC_'+str(i),i) for i in range(128))
        
if __name__ == "__main__":
    m = MidiManager() #.init_View().mainloop()