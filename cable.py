import time
import simpy
import random

class ODN(object):
    """This class represents optical distribution Network."""
    #{'lambda':{active: int,OLT_id: int, ONU_dict: {oid,distance}, }}
    def __init__(self, env):
        self.env = env
        self.wavelengths = {}
        self.OLTs = None
        self.ONUs = None
        self.lightspeed = float(200000)
        #self.upstream = simpy.Store(self.env)
        #self.downstream = simpy.Store(self.env)
        #self.up_proc = self.env.process(self.UpStream())
        #self.down_proc = self.env.process(self.DownStream())

    def set_ONUs(self,ONUs):
        self.ONUs = ONUs

    def set_OLTs(self,OLTs):
        self.OLTs = OLTs

    def create_wavelength(self,wavelength):
        self.wavelengths[wavelength] = {"active": 0, "OLT": -1,
            "upstream": simpy.Store(self.env), "downstream": simpy.Store(self.env),
            "up_proc": self.env.process(self.UpStream(wavelength)), "down_proc": self.env.process(self.DownStream(wavelength)) }

    def activate_wavelenght(self, wavelength,olt):
        self.wavelengths[wavelength]["active"] = 1
        self.wavelengths[wavelength]["OLT"] = olt

    def propagation_delay(self,onu):
        distance = self.ONUs[onu].distance
        delay = distance/self.lightspeed
        #print("p delay={}".format(delay))
        yield self.env.timeout(delay) #propagation delay

    def UpStream(self,wavelength):
        while True:
            onu,pkt,wavelength = yield self.wavelengths[wavelength]['upstream'].get()
            #print "up"
            prop = self.env.process( self.propagation_delay(onu) )
            yield prop
            olt = self.wavelengths[wavelength]["OLT"]
            self.OLTs[olt].ULInput.put(pkt)

    def DownStream(self,wavelength):
        while True:
            msg = yield self.wavelengths[wavelength]['downstream'].get()
            print self.env.now
            print("{} - down".format(msg['onu']))
            prop = self.env.process( self.propagation_delay(msg['onu']) )
            yield prop
            print(" {} - grant exit at {}".format(msg['onu'],self.env.now))
            self.ONUs[msg['onu']].DLInput.put(msg)
