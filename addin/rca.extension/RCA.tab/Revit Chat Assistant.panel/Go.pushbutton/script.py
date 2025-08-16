# -*- coding: utf-8 -*-
"""Revit Chat Assistant Add-In"""

__title__ = "Go"
__doc__ = "Interface Between You and Revit via Large Language Model"


# Import Revit UI for our dialog
from Autodesk.Revit.UI import TaskDialog # pyright: ignore[reportMissingModuleSource]

def main():
    # Create a simple dialog box
    dialog = TaskDialog("Revit Chat Assistant")
    dialog.MainInstruction = "Hello from Revit Chat Assistant!"
    dialog.Show()

# Run the function
if __name__ == '__main__':
    main()

