import json
import logging

def ifconfig_parse(ifconfig, src, dest):
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
    src_addr, dest_addr = '0.0.0.0', '0.0.0.0'
    with open(ifconfig, 'r') as fp:
        line = fp.readlines()
        for idx in range(len(line)):

            if line[idx].find('-') is not -1:
                intf = str(line[idx]).split(' ')[0]

                if line[idx].find('inet') is not -1 and intf == src:
                    src_addr = str(line[idx+1]).split(':')[1].split(' ')[0]

                elif line[idx].find('inet') is not -1 and intf == dest:
                    dest_addr = str(line[idx+1]).split(':')[1].split(' ')[0]

    return src_addr, dest_addr

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
                src_addr, dest_addr = ifconfig_parse(ifconfig, src=intf1, dest=intf2)
                dict.append({'Destination_id': intf2.split('-')[0], 'Destination': dest_addr,'Gateway': src_addr, 'Iface':intf1, 'Cost': 1})

            elif intf2.split('-')[0] == id:
                src_addr, dest_addr = ifconfig_parse(ifconfig, src=intf2, dest=intf1)
                dict.append({'Destination_id': intf1.split('-')[0], 'Destination': dest_addr,'Gateway': src_addr, 'Iface':intf2, 'Cost': 1})

        with open('routing_tables/{}_routing_table.json'.format(id), 'w') as fp:
                json.dump(dict, fp, sort_keys=True, indent=4)

    except Exception as e:
        logging.basicConfig(filename='debug_logs/utility_debug.log', level=logging.INFO)
        logging.info(e)

