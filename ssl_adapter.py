from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class SSLAdapter(HTTPAdapter):
    """
    A custom adapter for the `requests` library that allows specifying a set of SSL ciphers 
    to be used for HTTPS requests. This is useful when you need to enforce a certain level of 
    security or need to ensure compatibility with a server that requires specific ciphers.

    The SSLAdapter class inherits from `HTTPAdapter` and overrides the `init_poolmanager` method 
    to create an SSL context with a custom cipher set. This context is then used for all HTTPS 
    connections made by this adapter.

    Example usage:
        import requests

        # Create a session and attach the SSLAdapter with custom ciphers
        s = requests.Session()
        adapter = SSLAdapter()
        s.mount('https://', adapter)

        # Make a request to a server that requires specific SSL ciphers
        response = s.get('https://example.com')

    Note:
        It's important to choose ciphers that ensure a balance between compatibility and security. 
        Using outdated or weak ciphers can expose communications to vulnerabilities.
    """

    def init_poolmanager(self, *args, **kwargs):
        """
        Initializes the pool manager for the adapter, creating a custom SSL context with the 
        specified ciphers. Disables certificate verification for self-signed certificates.

        This method is called internally by `requests` when establishing a connection pool. 
        The custom SSL context created here is applied to all connections in the pool.
        """
        context = create_urllib3_context(ciphers='HIGH:!DH:!aNULL')
        context.check_hostname = False
        context.verify_mode = 0  # ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)
