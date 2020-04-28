import json
import logging
import random

def ifconfig_parse(ifconfig, node_id):
    """ 
    Parse through ifconfig.txt file which is created from saving the node.cmd('ifconfig') command output
    the a text file

    Selects src and dest

    The search could be made separate from this but I decided to just do the search for src and dest in this function

    :param dest: destination interface
    :param src: source interface
    :param ifconfig: ifconfig.txt
    :return: src and dest addresses
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
            dict.append({'dest_id': '-', 'dest_addr': dest_addr,'dest_port': port, 'gateway': src_addr, 'iface':intf, 'bcast': bcast, 'cost': 1})

        #Cannot assume that ifconfig contains info about neighbor node intf
        #elif line.find('inet') is not -1 and intf == dest:
            #dest_addr = str(line).split(':')[1].split(' ')[0]

    with open('routing_tables/{}_routing_table.json'.format(node_id), 'w') as fp:
        json.dump(dict, fp, sort_keys=True, indent=4)




#Currently Not used will enventually delete
def generate_routing_table(id, links, ifconfig):
    """ 

    :param id:
    :param ifconfig: text file containing all ifconfig
    :return:
    """
    dict = []
    try:
        for idx in range(len(links)):

            intf1, intf2 = str(links[idx].intf1), str(links[idx].intf2)
            src_addr, dest_addr = 'None', 'None'

            if intf1.split('-')[0] == id:
                src_addr, bcast, dest_addr = ifconfig_parse(ifconfig, src=intf1, dest=intf2)
                dict.append({'Destination_id': intf2.split('-')[0], 'Destination': dest_addr,'Gateway': src_addr, 'Iface':intf1, 'bcast': bcast, 'Cost': 1})

            elif intf2.split('-')[0] == id:
                src_addr, bcast, dest_addr = ifconfig_parse(ifconfig, src=intf2, dest=intf1)
                dict.append({'Destination_id': intf1.split('-')[0], 'Destination': dest_addr,'Gateway': src_addr, 'Iface':intf2, 'bcast': bcast, 'Cost': 1})

        with open('routing_tables/{}_routing_table.json'.format(id), 'w') as fp:
                json.dump(dict, fp, sort_keys=True, indent=4)

    except Exception as e:
        logging.basicConfig(filename='debug_logs/utility_debug.log', level=logging.INFO)
        logging.info(e)

