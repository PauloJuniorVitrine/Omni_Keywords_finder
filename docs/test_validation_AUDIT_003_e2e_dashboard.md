============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.1.1, pluggy-1.5.0
rootdir: D:\PROJETOS\SISTEMAS\PROGRAMAS\omni_keywords_finder
configfile: pytest.ini
plugins: anyio-4.9.0, Faker-24.14.1, asyncio-0.26.0, cov-4.1.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 1 item

tests\e2e\test_dashboard_e2e.py F                                        [100%]

================================== FAILURES ===================================
_________________________ test_dashboard_metrics_e2e __________________________
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connection.py:198: in _new_conn
    sock = connection.create_connection(
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] Nenhuma conex├úo p├┤de ser feita porque a m├íquina de destino as recusou ativamente

The above exception was the direct cause of the following exception:
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connectionpool.py:787: in urlopen
    response = self._make_request(
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connection.py:445: in request
    self.endheaders()
C:\Program Files\Python311\Lib\http\client.py:1277: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
C:\Program Files\Python311\Lib\http\client.py:1037: in _send_output
    self.send(msg)
C:\Program Files\Python311\Lib\http\client.py:975: in send
    self.connect()
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connection.py:276: in connect
    self.sock = self._new_conn()
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connection.py:213: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPConnection object at 0x00000204C78621D0>: Failed to establish a new connection: [WinError 10061] Nenhuma conex├úo p├┤de ser feita porque a m├íquina de destino as recusou ativamente

The above exception was the direct cause of the following exception:
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\adapters.py:667: in send
    resp = conn.urlopen(
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\connectionpool.py:841: in urlopen
    retries = retries.increment(
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\urllib3\util\retry.py:519: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /api/dashboard/metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x00000204C78621D0>: Failed to establish a new connection: [WinError 10061] Nenhuma conex├úo p├┤de ser feita porque a m├íquina de destino as recusou ativamente'))

During handling of the above exception, another exception occurred:
tests\e2e\test_dashboard_e2e.py:11: in test_dashboard_metrics_e2e
    resp = requests.get(url, timeout=10)
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\api.py:73: in get
    return request("get", url, params=params, **kwargs)
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\api.py:59: in request
    return session.request(method=method, url=url, **kwargs)
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\sessions.py:589: in request
    resp = self.send(prep, **send_kwargs)
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\sessions.py:703: in send
    r = adapter.send(request, **kwargs)
C:\Users\SEDUC\Desktop\PROJETOS\omni_keywords_finder\.venv\Lib\site-packages\requests\adapters.py:700: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retries exceeded with url: /api/dashboard/metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x00000204C78621D0>: Failed to establish a new connection: [WinError 10061] Nenhuma conex├úo p├┤de ser feita porque a m├íquina de destino as recusou ativamente'))
=========================== short test summary info ===========================
FAILED tests/e2e/test_dashboard_e2e.py::test_dashboard_metrics_e2e - requests...
======================== 1 failed, 1 warning in 4.99s =========================
