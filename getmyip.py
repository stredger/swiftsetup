import socket
import sys

conn = socket.create_connection((sys.argv[1], 80))
ip = conn.getsockname()[0]
conn.close()

print ip
