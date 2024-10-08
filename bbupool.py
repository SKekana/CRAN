import simpy
from bbu import BBU

class BBUPool(object):
	def __init__(self,env,bbupoll_id,wavelength,net_output=None):
		#def __init__(self,env,DC_type,bbupoll_id,OLT,odn=None):
 		self.env = env
 		#self.DC_type = DC_type # 1 = Fog node; 2 = DC local; 3 = DC central
		self.wavelength = wavelength
 		self.bbupoll_id = bbupoll_id 
 		self.ULInput = simpy.Store(self.env) #An input buffer for packets arriving at the BBU pool.
		self.net_output = net_output
		self.pre_proc_buffer = simpy.Store(self.env) # A buffer for packets before processing by individual BBUs.
		self.post_proc_buffer = simpy.Store(self.env) # A buffer for packets after processing by individual BBUs.

		self.pre_proc = self.env.process(self.Pre_Proc()) #Handles pre-processing of packets (distributing them to BBUs).
		self.post_proc = self.env.process(self.Post_Proc()) #Handles post-processing of packets (after they've been processed by BBUs).

		self.BBU_DICT = {} #Creates an empty dictionary BBU_DICT to store BBU objects, keyed by their IDs.

	def add_bbu(self,bbu_id):
		self.BBU_DICT[bbu_id] = BBU(self.env,bbu_id,self.post_proc_buffer)

	def Pre_Proc(self):
		while True:
			pkt = yield self.ULInput.get()

			print(self.BBU_DICT)
			print(pkt)
			
			BBU_id = pkt.id # src id is the same for all DC BBUs of a cell
			#print("BBU_id = " + str(BBU_id))

			self.BBU_DICT[BBU_id].proc_buffer.put(pkt) #write to BBU proc buffer

	def Post_Proc(self):
		while True:
			
			pkt = yield self.post_proc_buffer.get()
			#if odn != none:
			#print "BBUPOOL: Send to ODN"
