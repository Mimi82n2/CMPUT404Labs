#!/usr/bin/env python3
import socket
import time
from multiprocessing import Process, Pool

#define address & buffer size
HOST = ""
PORT = 8001
BUFFER_SIZE = 4096
#create a tcp socket
def create_tcp_socket():
    print('Creating socket')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except (socket.error, msg):
        print(f'Failed to create socket. Error code: {str(msg[0])} , Error message : {msg[1]}')
        sys.exit()
    print('Socket created successfully')
    return s

#get host information
def get_remote_ip(host):
    print(f'Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print ('Hostname could not be resolved. Exiting')
        sys.exit()

    print (f'Ip address of {host} is {remote_ip}')
    return remote_ip

#send data to server
def send_data(serversocket, payload):
    print("Sending payload")    
    try:
        serversocket.sendall(payload.encode())
    except socket.error:
        print ('Send failed')
        sys.exit()
    print("Payload sent successfully")
           
            
    
def proxy_handler(conn):
        try:
            google_payload = conn.recv(BUFFER_SIZE).decode('utf-8')     
            time.sleep(0.5)

        
            #define address info, payload, and buffer size
            google_host = 'www.google.com'
            google_port = 80
            s_google = create_tcp_socket()
            s_google.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            google_remote_ip = get_remote_ip(google_host)
            s_google.connect((google_remote_ip, google_port))
            print (f'Socket Connected to {google_host} on ip {google_remote_ip}')

            send_data(s_google, google_payload)

            s_google.shutdown(socket.SHUT_WR)
            google_full_data = b""
            while True:
                google_data = s_google.recv(BUFFER_SIZE)
                
                if not google_data:
                    break
                
                google_full_data += google_data

        except Exception as e:
            raise e
        finally:
            s_google.close()
            time.sleep(1)
            conn.sendall(google_full_data)
            conn.sendall("STOP".encode())
            time.sleep(1)

            conn.close()
            return google_full_data
        
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
        #QUESTION 3
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #bind socket to address
        s.bind((HOST, PORT))
        #set to listening mode
        s.listen(2)
        
        #continuously listen for connections
        while True:
            conn, addr = s.accept()
            print("Connected by", addr)
            
            
            p = Pool(1)
            p.apply(proxy_handler, args=(conn,))

            #p = Process(target=proxy_handler, args=(conn))
            #p.daemon = True
            #p.start()
            #conn.close()
        



if __name__ == "__main__":
    main()
