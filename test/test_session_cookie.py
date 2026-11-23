import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.websocket.module_websocket import module_websocket


class WebsocketSessionCookieTest(unittest.TestCase):
    def test_uses_configured_cookie_name_and_default(self):
        for configured, expected in (('PyGDO', 'PyGDO'), (None, 'GDO'), ('', 'GDO')):
            with self.subTest(configured=configured):
                module = object.__new__(module_websocket)
                module.cfg_client_tls = MagicMock(return_value=True)
                module.cfg_client_host = MagicMock(return_value='localhost')
                module.cfg_client_port = MagicMock(return_value=61555)
                module.get_config_value = MagicMock(return_value=False)
                module.add_js_inline = MagicMock()
                with patch.object(Application, 'config', return_value=configured), \
                     patch.object(Application, 'get_cookie', return_value='test-session') as get_cookie:
                    module.gdo_init_sidebar(None)
                get_cookie.assert_called_once_with(expected)
                self.assertIn('test-session', module.add_js_inline.call_args.args[0])
