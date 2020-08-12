# Python SCPI socket functions
# This is not an official Keysight driver.  
# Very limited testing has been done.
# Feel free to modify this
# Version 0.5 


import socket

def SCPI_sock_connect(ipaddress,port=5025):
    """ Opens up a socket connection between an instrument and your PC
        Returns the socket session

        Arguments:
        ipaddress -> ip address of the instrument
        port -> optional -> socket port of the instrument (default 5025)"""

    try:
        session=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #session.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
        #session.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 0)
        session.connect((ipaddress,port))
    except IOError:
        print( "Failed to connect to the instrument, pleace check your IP address" )
        return
    return session

def SCPI_sock_send(session,command,error_check=False):
    """Sends a command to an instrument

        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command
        error_check -> optional -> Check for instrument errors (default False)"""
    
    resp = " "
    session.sendall(str.encode(command + "\n"))

    if error_check==True:
        err = get_error(session, command)        
        
def SCPI_sock_query(session,command,error_check=False):
    """Sends a query to an instrument
        Returns the query response
        
        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command
        error_check -> optional -> Check for instrument errors (default False)"""
    
    session.settimeout(2.0)
    try:
        session.sendall(str.encode(command + "\n"))
        response = getDataFromSocket(session)
        if error_check==True:
            err = get_error(session, command)
            if err:
                response = "<ERROR>"
        return response
        
    except socket.timeout:
        print( "Query error:" )
        get_error(session, command)
        response = "<ERROR>"
        return response

def SCPI_sock_close(session):
    """Closes the socket connection

        Argument:
        session -> TCPIP socket connection"""
    
    session.close()

def getDataFromSocket(session):
    """Reads from a socket until a newline is read
        Returns the data read

        Argument:
        session -> TCPIP socket"""
    
    dat = ""
    while 1:
        message = session.recv(4096).decode()
        last=len(message)
        if message[last-1] == "\n":
            dat=dat+message[:-1]
            return dat
        else:
            dat=dat+message

def get_error(session, command):
    """Checks an instrument for errors and print( them out )
        Returns True if any errors are encountered

        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command"""
        
    has_err=False
    resp = SCPI_sock_query(session,"SYST:ERR?")
    
    if int(resp[:2]) != 0:
        print( "Your command: " + command + " has errors:" )
        print( resp )
        has_err = True
    while int(resp[:2]) != 0:
        resp=SCPI_sock_query(session,"SYST:ERR?")
        if int(resp[:2]) != 0:
            print( resp )

    return has_err
