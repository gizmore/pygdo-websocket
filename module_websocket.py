from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_Server import GDO_Server
from gdo.core.Connector import Connector
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Path import GDT_Path
from gdo.net.GDT_Host import GDT_Host
from gdo.net.GDT_Port import GDT_Port
from gdo.shadowdogs.GDT_Location import GDT_Location
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page
from gdo.ui.GDT_PageLocation import GDT_PageLocation
from gdo.websocket.connector.Websocket import Websocket


class module_websocket(GDO_Module):

    ##########
    # Config #
    ##########

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Host('ws_host').not_null().initial('127.0.0.1'),
            GDT_Port('ws_port').not_null().initial('61221'),
            GDT_Bool('ws_tls').not_null().initial('0'),
            GDT_Path('ws_tls_key').existing_file(),
            GDT_Path('ws_tls_cert').existing_file(),
            GDT_Bool('ws_autoconnect').not_null().initial('1'),
            GDT_Bool('ws_raw').not_null().initial('1'),
            GDT_PageLocation('ws_raw_location').initial('_left_bar'),
        ]

    def cfg_host(self) -> str:
        return self.get_config_val('ws_host')

    def cfg_port(self) -> int:
        return self.get_config_value('ws_port')

    def cfg_tls(self) -> bool:
        return self.get_config_value('ws_tls')

    def cfg_tls_key_path(self) -> str:
        return self.get_config_val('ws_tls_key')

    def cfg_tls_cert_path(self) -> str:
        return self.get_config_val('ws_tls_key')

    def cfg_auto_connect(self) -> bool:
        return self.get_config_value('ws_autoconnect')

    ########
    # Init #
    ########

    async def gdo_install(self):
        if not GDO_Server.get_by_connector('websocket'):
            GDO_Server.blank({
                'serv_name': 'ws',
                'serv_connector': 'websocket',
            }).insert()

    def gdo_init(self):
        Connector.register(Websocket)

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_js('js/pygdo_websocket.js')
        self.add_css('css/pygdo_websocket.css')

    def autoconnect_script(self):
        self.add_js_inline("window.gdo.ws.init();")

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        self.add_js_inline("window.gdo.ws.tls = " + str(int(self.cfg_tls())) +";\nwindow.gdo.ws.ip = '" + self.cfg_host() + "';\nwindow.gdo.ws.port = " + str(self.cfg_port()) + ";\nwindow.gdo.ws.cookie = '" + Application.get_cookie(GDO_Session.COOKIE_NAME) + "';")
        if self.cfg_auto_connect() and GDO_User.current().is_user():
            self.autoconnect_script()
        if self.get_config_value('ws_raw'):
            self.get_config_value('ws_raw_location').add_field(GDT_Link().href(self.href('raw')).text('module_websocket'))
