"""Run a Python entrypoint with Python socket connections forbidden."""
import os
import runpy
import socket
import sys

def denied(*args, **kwargs):
    raise RuntimeError('Network connection forbidden during offline verification')

os.environ['HF_HUB_OFFLINE'] = '1'
socket.socket.connect = denied
socket.socket.connect_ex = denied
socket.create_connection = denied
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
