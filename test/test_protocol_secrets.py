import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.websocket.method.protocol import protocol


class ProtocolSecretsTest(unittest.TestCase):
    def test_secret_fields_never_render_or_appear(self):
        Application.mode(Mode.render_cli)
        public, secret = MagicMock(), MagicMock()
        public.is_secret.return_value = False
        public.render_json.return_value = {'public': 'value'}
        public.fqcn.return_value = 'Public'
        secret.is_secret.return_value = True
        model = MagicMock()
        model.fqcn.return_value = 'Model'
        model.table.return_value.columns.return_value = {'public': public, 'secret': secret}
        module = MagicMock()
        module.gdo_classes.return_value = [model]
        with patch('gdo.websocket.method.protocol.ModuleLoader.instance') as loader:
            loader.return_value._enabled = [module]
            result = protocol().gdo_execute().render_json()
        self.assertEqual([{'public': 'value'}], result['gdo']['Model'])
        self.assertEqual({'Public': {'public': 'value'}}, result['gdt'])
        secret.render_json.assert_not_called()
        secret.fqcn.assert_not_called()
