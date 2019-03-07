from opcua import Client

c = Client("opc.tcp://10.10.16.240:4840")

c.connect()
M = c.get_node("ns=1;s=Tag30[0]").get_value()
# print(c.get_node("ns=1;s=Tag30[0]").get_value())
import struct

# d = struct.pack('!c', M)
print(M.encode())
