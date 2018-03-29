import socket
import threading

import pytest
import werkzeug.serving
import werkzeug.wrappers
from six.moves import urllib

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
    path = env['PATH_INFO']

    if path == '/auth':
        start_response('200 OK',  [('Content-Type', 'application/json')])
        return [b'{"token": "123"}']

    if path == fixtures11.DISCOVERY_PATH:
        taxii_headers = [
            ('Content-Type', 'application/xml'),
            ('X-TAXII-Content-Type', 'urn:taxii.mitre.org:message:xml:1.1'),
        ]
        start_response('200 OK', taxii_headers)
        return [fixtures11.DISCOVERY_RESPONSE.encode()]

    raise Exception('Unknown test path')


def test_set_auth_ssl(httpsserver):
    host, port = httpsserver.server_address
    client = cabby.create_client(
        host=host,
        port=port,
        use_https=True,
        discovery_path=fixtures11.DISCOVERY_PATH)

    auth_params = dict(
        username='cabby',
        password='test',
        ca_cert='tests/ssl_test_files/root_ca.pem',
        cert_file='tests/ssl_test_files/client.pem',
        key_file='tests/ssl_test_files/client.key',
        key_password='cabby-test',
        jwt_auth_url='/auth',
        verify_ssl=True)

    # Test client certificate with key_password.
    # This doesn't use the requests library, instead
    # it uses urllib2 or 3 through the 'request_with_key_password' function:
    client.set_auth(**auth_params)
    services = client.discover_services()
    assert len(services) == 4

    # Test we get the correct error when forgetting a key_password:
    missing_key_password = dict(auth_params, key_password=None)
    client.set_auth(**missing_key_password)
    error_msg = "Key file is encrypted but key password was not provided"
    with pytest.raises(ValueError, matches=error_msg):
        client.discover_services()

    # Test that server certificate authentication can fail:
    invalid_server_ca_cert = dict(auth_params, ca_cert=None)
    client.set_auth(**invalid_server_ca_cert)
    error_msg = "certificate verify failed"
    with pytest.raises(urllib.error.URLError, matches=error_msg):
        client.discover_services()

    # Test that verify_ssl=False ignores the invalid certificate:
    invalid_server_ca_cert_no_verify = dict(
        auth_params, ca_cert=None, verify_ssl=False)
    client.set_auth(**invalid_server_ca_cert_no_verify)
    services = client.discover_services()
    assert len(services) == 4

    # Test client certificate with key_password.
    # This uses the requests library as usual:
    client_key_without_passphrase = dict(
        auth_params,
        key_file='tests/ssl_test_files/client_no_pass.key',
        cert_file='tests/ssl_test_files/client_no_pass.pem')
    client.set_auth(**client_key_without_passphrase)
    services = client.discover_services()
    assert len(services) == 4
