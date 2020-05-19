import json
import logging
import random

def ifconfig_parse(ifconfig, node_id):
    """ 
    Parse through ifconfig.txt file which is created from saving the node.cmd('ifconfig') command output
    the a text file

    Selects src and dest

    The search could be made separate from this but I decided to just do the search for src and dest in this function

    :param node_id: neighboring node connected to the nodes who ifconfig is being parse 
    :param ifconfig: ifconfig.txt
    """
    src_addr, dest_addr, port = '-', '-', '-'
    intf, dict = None, []
    string_iter = iter(ifconfig.splitlines())

    for line in string_iter:
        if line.find('-') is not -1:
            intf = str(line).split(' ')[0]

        elif str(line).split(' ')[0] == 'lo':
            break

        if line.find('inet') is not -1 and intf.split('-')[0] == str(node_id):
            src_addr = str(line).split(':')[1].split(' ')[0]
            bcast = str(line).split(':')[2].split(' ')[0]
            dict.append({"dest_id": "-", "dest_addr": dest_addr,"dest_port": port, "gateway": src_addr, "iface":intf, "bcast": bcast, "cost": 1})

    with open('routing_tables/{}_routing_table.json'.format(node_id), 'w') as fp:
        json.dump(dict, fp, sort_keys=True, indent=4)


