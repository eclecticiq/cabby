import socket
import threading

import pytest
import werkzeug.serving

import cabby
import fixtures11


@pytest.fixture
def httpsserver(request):
    port = get_free_port()
    server_key = 'tests/ssl_test_files/root_ca.key'
    server_cert = 'tests/ssl_test_files/root_ca.pem'
    server = werkzeug.serving.make_server(
        host='127.0.0.1',
        port=port,
        app=remote_taxii_app,
        passthrough_errors=True,
        ssl_context=(server_cert, server_key))
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    request.addfinalizer(server.shutdown)
    return server


def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def remote_taxii_app(env, start_response):
    if env['PATH_INFO'] == '/auth':
        start_response('200 OK',  [('Content-Type', 'application/json')])
        return [b'{"token": "123"}']
    elif env['PATH_INFO'] == fixtures11.DISCOVERY_PATH:
        taxii_headers = [
            ('Content-Type', 'application/xml'),
            ('X-TAXII-Content-Type', 'urn:taxii.mitre.org:message:xml:1.1'),
        ]
        start_response('200 OK', taxii_headers)
        return [fixtures11.DISCOVERY_RESPONSE.encode()]
    else:
        raise Exception('Unknown test path')


def test_jwt_auth_with_ssl(httpsserver):
    # Serve a JWT token
    host, port = httpsserver.server_address
    client = cabby.create_client(
        host=host,
        port=port,
        use_https=True,
        discovery_path=fixtures11.DISCOVERY_PATH)
    client.set_auth(
        username='cabby',
        password='test',
        ca_cert='tests/ssl_test_files/root_ca.pem',
        cert_file='tests/ssl_test_files/client.pem',
        key_file='tests/ssl_test_files/client.key',
        key_password='cabby-test',
        jwt_auth_url='/auth',
        verify_ssl=True)
    services = client.discover_services()
    assert len(services) == 4
