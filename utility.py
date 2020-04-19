import os
import logging
import json

def generate_routing_table(route, node_name):
	"""route is string table returned by the cmd command split
		Ex: route = r1.cmd('route').split()
	The array return always has the form:
	['Kernel', 'IP', 'routing', 'table', 'Destination', 'Gateway',
	 'Genmask', 'Flags', 'Metric', 'Ref', 'Use', 'Iface', 'default',
	 '10.0.2.2', '0.0.0.0', 'UG', '0', '0', '0', 'eth1' and repeats

	A dict entry has the form:
	{'Destination': value(string), 'Gateway': value(string), 'Genmask': value(string), 'Iface': value(string)}
	"""
	dict = []
	route = route[12:] #13 - 20, next would be [21 - 28] 
	for i in range(len(route)//8):
		dict.append({'Destination':route[i*8],'Gateway':route[i*8+1],'Genmask':route[i*8+2],'Iface':route[i*8+7]})
	with open('routing_tables/{}_routing_table.json'.format(node_name), 'w') as fp:
		json.dump(dict, fp, sort_keys=True, indent=4)
