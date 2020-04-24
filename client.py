import c_s_message_pb2
import socket
import struct

# def recv_mssg(socket):
#     msglen = recv_all_mssg(socket, 2)
#     if not(msglen):
#         return None
#     m_len = struct.unpack('>I', msglen)[0]
#     return recv_all_mssg(socket, m_len)

def recv_all_mssg(socket, m_len):
    data = bytearray()
    while len(data) < m_len:
        packet = socket.recv(m_len - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def client():
    request_mssg = c_s_message_pb2.total_message()
    request_mssg.type = 0;

    llen = request_mssg.ByteSize()
    request_m_len = llen.to_bytes(2, 'big')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('cs177.seclab.cs.ucsb.edu', 54526))

    no_flag = True
    request_task = 0
    key = None;
    value = None;
    count = None;
    e_error = None;
    flag = None;
    key_val_dict = {}

    while no_flag:
        #Send a request task
        s.sendall(request_m_len)
        s.sendall(request_mssg.SerializeToString())
        #Get response length
        data = s.recv(2)
        unsigned_m_len = int.from_bytes(data,"big")
        #Get response output o
        o = recv_all_mssg(s, unsigned_m_len)
        return_m = c_s_message_pb2.total_message()
        return_m.ParseFromString(o)
        #get request task type
        print("Return Message")
        print(return_m)
        request_task = return_m.type
        print("\n")
        print("TYPE")
        print(request_task)
        #based on the task respond to the server with appropriate message
        #if flag is recieved then the while loop breaks
        if(request_task == 1):
            print("INTO REQUEST 1")
            key = return_m.key
            print("Key input ")
            print(key)
            value = return_m.value
            print("Value for key is: " + value)
            key_val_dict[key] = value
            r1 = c_s_message_pb2.total_message()
            r1.type = 2
            r1_len = r1.ByteSize()
            r1_m_len = r1_len.to_bytes(2, 'big')
            s.sendall(r1_m_len)
            s.sendall(r1.SerializeToString())
        elif(request_task == 3):
            print("INTO REQUEST 3")
            print("Requested key: ")
            print(key)
            key = return_m.key
            if key not in key_val_dict:
                r3_error = c_s_message_pb2.r5_msg();
                r3_error.type = 5;
                r3_error_len = r3_error.ByteSize()
                r3_error_m_len = r3_error_len.to_bytes(2, 'big')
                s.sendall(r3_error_m_len)
                s.sendall(r3_error.SerializeToString())
            else:
                r3 = c_s_message_pb2.r4_msg()
                r3.type = 4
                r3.value = key_val_dict[key]
                print("Value for key is: " + key_val_dict[key])
                # print("Type of value is: ")
                # print(type(key_val_dict[key]))
                print("Message object being sent from type 4 is: ")
                print(r3)
                r3_len = r3.ByteSize()
                r3_m_len = r3_len.to_bytes(2, 'big')
                s.sendall(r3_m_len)
                s.sendall(r3.SerializeToString())
        elif(request_task == 6):
            print("INTO REQUEST 6")
            valid_pairs = len(key_val_dict)
            r6 = c_s_message_pb2.r7_msg()
            r6.type = 7;
            r6.count = valid_pairs
            r6_len = r6.ByteSize()
            r6_m_len = r6_len.to_bytes(2, 'big')
            s.sendall(r6_m_len)
            s.sendall(r6.SerializeToString())
        elif(request_task == 8):
            return_error = c_s_message_pb2.flag()
            return_error.ParseFromString(o)
            print("ERROR MESSAGE: ")
            print("\n")
            e_error = return_error.error
            print(e_error)
            print("Dictionary contains: ")
            for i in key_val_dict.keys():
                print("Key")
                print(i)
                print("Value")
                print(key_val_dict[i])
            no_flag = False
        elif(request_task == 9): #flag output
            return_flag = c_s_message_pb2.flag()
            return_flag.ParseFromString(o)
            flag = return_flag.flag
            print("Got Flag")
            print(return_flag.flag)
            no_flag = False
        else:
            print("Error with return message")
            no_flag = False
    s.close()

client()