from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.message.GDT_PRE import GDT_PRE
from gdo.ui.GDT_Page import GDT_Page


class raw(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.text('info_websocket_raw')
        form.add_fields(
            GDT_String('ws_cmdline').not_null(),
        )
        super().gdo_create_form(form)

    def render_page(self) -> GDT:
        return GDT_Container().add_fields(
            GDT_PRE().attr('id', 'ws_log'),
            super().render_page()
        )

    def form_submitted(self) -> GDT:
        GDT_Page._js_inline += '<script>alert(1);</script>'
        return self.msg('msg_ws_raw_sent')
    