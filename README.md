Installing:

	pip install --user linx_connection

Usage:

    conn = LinxConnection(port='\<port>') # \<port> can be /dev/ttyUSBX if you are running on Linux or COMX if Windows
    dct = conn.AnalogRead(1) # -> {..., 'data': \<data>, ...} where \<data> is bytes object representing status of A1 port. Use transfrom(dct) to get normal int value