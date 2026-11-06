"""Edge TTS CLI using the existing Codex proxy and platform CA.

Usage: .venv/bin/python films/.speech-final/edge-with-platform-ca.py
       --voice fr-FR-DeniseNeural --text 'Bonjour.' --write-media output.mp3
No certificate checks are disabled. No proxy or CA values are persisted.
The context integration is tested with edge-tts 7.3.1.
"""
import os
import runpy
import ssl
import edge_tts.communicate
import edge_tts.voices

def configure():
    ca = os.environ.get('SSL_CERT_FILE')
    for module in (edge_tts.communicate, edge_tts.voices):
        if ca:
            module._SSL_CTX.load_verify_locations(cafile=ca)
        if not module._SSL_CTX.check_hostname or module._SSL_CTX.verify_mode != ssl.CERT_REQUIRED:
            raise RuntimeError('TLS verification must remain enabled')
    if os.environ.get('HTTPS_PROXY'):
        os.environ['WSS_PROXY'] = os.environ['HTTPS_PROXY']

if __name__ == '__main__':
    configure()
    runpy.run_module('edge_tts', run_name='__main__')
