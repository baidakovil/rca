import os.path as op

from pyrevit import forms


class DockablePanel(forms.WPFPanel):
    panel_title = "Revit Chat Assistant"
    panel_id = "3110e336-f81c-4927-87da-4e0d30d4d64e"
    panel_source = op.join(op.dirname(__file__), "DockablePanelRCA.xaml")

    def do_something(self, sender, args):
        forms.alert("Illa!!!")


if not forms.is_registered_dockable_panel(DockablePanel):
    forms.register_dockable_panel(DockablePanel)
else:
    pass