import socket
import pickle
import json
from IPython import embed

class RokokoUpdater():
  def __init__(self):
    self.server_ip = "127.0.0.1"
    self.server_port = 14042
    self.server_addr_port = (self.server_ip, self.server_port)
    self.buffersize = 20000
    
    self.udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # socket in udp / bind ip and port/ and change to non-blocking
    self.udp_server_socket.bind(self.server_addr_port)
    self.udp_server_socket.setblocking(False)
 
    print("UDP server starting")

    self.msg_list = []
    self.msg_json_list = []
  
  def update(self):  
    try:
      byte_addr_pair = self.udp_server_socket.recvfrom(self.buffersize)
    except BlockingIOError:
      raise BlockingIOError
    msg  = byte_addr_pair[0]
    addr = byte_addr_pair[1]
  
    # client_msg = "\rmsg from client : {}".format(len(msg))
    # print(client_msg)
    msg_decode = msg.decode('utf-8')
    self.msg_list.append(msg)
    self.msg_json_list.append(json.loads(msg_decode))
    
  def get_current_info(self):
    return self.msg_json_list[-1]['scene']['actors'][0]['body']
    
  def record(self):
    with open('./test_output_json.pickle', 'wb') as f:
        pickle.dump(self.msg_list, f, pickle.HIGHEST_PROTOCOL)
    # embed()
    # with open('./test_output_json.json', 'w') as jf:
    #   json.dump(msg_json, jf)