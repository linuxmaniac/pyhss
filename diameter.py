#Diameter Packet Crafter
import socket
import sys
import binascii
import math

def myround(n, base=4):
    if(n > 0):
        return math.ceil(n/4.0) * 4;
    elif( n < 0):
        return math.floor(n/4.0) * 4;
    else:
        return 4;




def generate_avp(avp_code, avp_flags, avp_content):
    #Generates an AVP with inputs provided (AVP Code, AVP Flags, AVP Content, Padding)
    #AVP content must already be in HEX - This can be done with binascii.hexlify(avp_content.encode())
    print("Generating AVP")
    avp_code = format(avp_code,"x").zfill(8)
    print("\tAVP Code:   " + str(avp_code))

    print("\tAVP Flags:  " + str(avp_flags))

    avp_length = 1 ##This is a placeholder that's overwritten later




    #ToDo - AVP Must always be a multiple of 4 - Round up.
    avp = str(avp_code) + str(avp_flags) + str("000000") + str(avp_content.decode("utf-8"))
    avp_length = int(len(avp)/2)
    print("\tAVP Length: " + str(avp_length))

    if avp_length % 4  == 0:
        print("Multiple of 4 - No Padding needed")
        avp_padding = ''
    else:
        print("Not multiple of 4 - Padding needed")
        rounded_value = myround(avp_length)
        print("Rounded value is " + str(rounded_value))
        print("Has " + str( int( rounded_value - avp_length)) + " bytes of padding")
        avp_padding = format(0,"x").zfill(int( rounded_value - avp_length) * 2)


    
    print("\tAVP Padding: " + str(avp_padding))
    
    avp = str(avp_code) + str(avp_flags) + str(avp_length) + str(avp_content.decode("utf-8") + avp_padding)
    print("\tAVP Data   :" + str(avp) + '\n')
    return avp

    



def generate_diameter_packet(packet_version, packet_flags, packet_command_code, packet_application_id, avp):
    #Placeholder that is updated later on
    packet_length = 228
    packet_length = format(packet_length,"x").zfill(6)

    print("Generating Diamter Packet")
    
    print("\tPacket Flags       : " + str(packet_flags))

    
    packet_command_code = format(packet_command_code,"x").zfill(6)
    print("\tPacket Command Code: " + str(packet_command_code))

    
    packet_application_id = format(packet_application_id,"x").zfill(8)
    print("\tPacket Application ID: " + str(packet_application_id))


    packet_hop_by_hop_id = str("256aa834")
    packet_end_to_end_id = str("8a851132")

    
    packet_hex = packet_version + packet_length + packet_flags + packet_command_code + packet_application_id + packet_hop_by_hop_id + packet_end_to_end_id + avp
    packet_length = int(round(len(packet_hex))/2)
    print("\tPacket Length: " + str(packet_length))
    packet_length = format(packet_length,"x").zfill(6)
    
    packet_hex = packet_version + packet_length + packet_flags + packet_command_code + packet_application_id + packet_hop_by_hop_id + packet_end_to_end_id + avp
    print("\tPacket Bytes over the wire are: " + packet_hex  + '\n')
    return packet_hex



#data = "010000e4800001010000000053da91a8ad31586400000108400000176873732e6c6f63616c646f6d61696e0000000128400000136c6f63616c646f6d61696e00000001164000000c5d05aad3000001014000000e00017f00000400000000010a4000000c000000000000010d00000014667265654469616d657465720000010b0000000c000027d90000012b4000000c000000000000010440000020000001024000000c010000230000010a4000000c000028af000001024000000cffffffff000001094000000c0000159f000001094000000c000028af000001094000000c000032db"

def decode_diameter_packet(data):
    packet_vars = {}
    avps = []
    print(data)
    print(type(data))
    data = data.hex()

    packet_vars['packet_version'] = data[0:2]
    packet_vars['length'] = int(data[2:8], 16)
    packet_vars['flags'] = data[8:10]       #Work out why this isn't decoding...
    packet_vars['command_code'] = int(data[10:16], 16)
    packet_vars['ApplicationId'] = int(data[16:24], 16)
    packet_vars['hop-by-hop-identifier'] = data[24:32]
    packet_vars['end-to-end-identifier'] = data[32:40]

    avp_sum = data[40:]

    print("Decoded Diameter values are:" )
    for keys in packet_vars:
        print("\t" + keys + "\t" + str(packet_vars[keys]) + "\t(" + str(type(packet_vars[keys])) + ")")
    avp_vars, remaining_avps = decode_avp_packet(avp_sum)
    avps.append(avp_vars)
    #print("Length of remaining AVPs is: " + str(len(remaining_avps)))
    while len(remaining_avps) > 0:
        avp_vars, remaining_avps = decode_avp_packet(remaining_avps)
        avps.append(avp_vars)
    else:
        print("Complete - Decoded all AVPs in Diameter Packet")

    return packet_vars, avps

def decode_avp_packet(data):
    avp_vars = {}
    #print("Recieved AVP raw is: " + str(data))
    avp_vars['avp_code'] = int(data[0:8], 16)
    avp_vars['avp_flags'] = data[8:10]
    avp_vars['avp_length'] = int(data[10:16], 16)
    #print(avp_vars['avp_length'])
    avp_vars['misc_data'] = data[16:(avp_vars['avp_length']*2)]
    if avp_vars['avp_length'] % 4  == 0:
        #print("Multiple of 4 - No Padding needed")
        avp_vars['padding'] = 0
    else:
        #print("Not multiple of 4 - Padding needed")
        rounded_value = myround(avp_vars['avp_length'])
        #print("Rounded value is " + str(rounded_value))
        #print("Has " + str( int( rounded_value - avp_vars['avp_length'])) + " bytes of padding")
        avp_vars['padding'] = int( rounded_value - avp_vars['avp_length']) * 2
    avp_vars['padded_data'] = data[(avp_vars['avp_length']*2):(avp_vars['avp_length']*2)+avp_vars['padding']]

    print("Decoded AVP values are:" )
    for keys in avp_vars:
        print("\t" + keys + "\t" + str(avp_vars[keys]) + "\t" + str(type(avp_vars[keys])))


    remaining_avps = data[(avp_vars['avp_length']*2)+avp_vars['padding']:]  #returns remaining data in avp string back for processing again

    return avp_vars, remaining_avps
    
packet_version = "01"
##packet_flags = "40" #(Proxyable only for flags header)
##packet_command_code = 272
##packet_application_id = 4
###avp = str("000001074000003b47617465776179536572766963652d352d312e73706a6b746e3030322e3b313438313032373335313b3231373831363935303700")
##avp = generate_avp(263, 40, "GatewayService-5-1.spjktn002.;1481027351;2178169507", 00)
##generate_diameter_packet(packet_version, packet_flags, packet_command_code, packet_application_id, avp)
##
##
##
##
