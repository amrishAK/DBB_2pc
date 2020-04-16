import socket
import json
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 7000))
msg = {"payload" : {"Data" : "Bro!!",
	"PayLoadToken" : 1587006709.9}, "type" : "data", "source" : "primaryReplica"}
client.send(bytes(json.dumps(msg), "utf8"))
client.close()