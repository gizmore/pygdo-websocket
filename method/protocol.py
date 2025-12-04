from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDT_Dict import GDT_Dict
from gdo.core.GDT_Serialize import GDT_Serialize, SerializeMode


class protocol(Method):
    """
    Describe all GDO and GDT for javascript.
    """

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_execute(self) -> GDT:
        protocol = {
            'gdt': {},
            'gdo': {},
        }
        for module in ModuleLoader.instance()._enabled:
            for gdo in module.gdo_classes():
                protocol['gdo'][gdo.fqcn()] = [gdt.render_json() for gdt in gdo.table().columns()]
                for gdt in gdo.table().columns():
                    protocol['gdt'][gdt.fqcn()] = gdt.render_json()
        # TODO All methods
        return GDT_Dict(protocol)
