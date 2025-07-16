import maya.cmds as cmds
import os
import sys
import importlib

def onMayaDroppedPythonFile(*args):
    # === CONFIGURATION ===
    tool_filename = "TransferNormalsTool.py"
    tool_module_name = "TransferNormalsTool"
    shelf_name = "Custom"
    button_label = "TransferNormals"
    icon = "polySphere.png"

    # === FIND TOOL LOCATION ===
    this_file = __file__ if '__file__' in globals() else cmds.file(query=True, sceneName=True)
    tool_dir = os.path.dirname(this_file)
    tool_path = os.path.join(tool_dir, tool_filename)

    if not os.path.isfile(tool_path):
        cmds.confirmDialog(
            title="Installation Error",
            message=f"Could not find '{tool_filename}' in:\n{tool_dir}",
            button=["OK"]
        )
        raise RuntimeError("Tool file not found.")

    if tool_dir not in sys.path:
        sys.path.append(tool_dir)

    try:
        tool_module = importlib.import_module(tool_module_name)
        importlib.reload(tool_module)
    except Exception as e:
        cmds.confirmDialog(
            title="Import Failed",
            message=f"Could not import '{tool_module_name}':\n{e}",
            button=["OK"]
        )
        raise

    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent="ShelfLayout")

    for child in cmds.shelfLayout(shelf_name, query=True, childArray=True) or []:
        if cmds.shelfButton(child, query=True, label=True) == button_label:
            cmds.deleteUI(child)

    cmds.shelfButton(
        label=button_label,
        parent=shelf_name,
        command=f"import {tool_module_name}; {tool_module_name}.smart_launch_normal_tool()",
        image=icon,
        imageOverlayLabel=button_label,
        overlayLabelColor=(1, 1, 1),
        overlayLabelBackColor=(0, 0, 0, 0.5),
        annotation="Launch Transfer Normals Tool",
        sourceType="python"
    )

    cmds.inViewMessage(
        amg=f"<hl>{button_label}</hl> added to shelf <hl>{shelf_name}</hl>.",
        pos="topCenter", fade=True
    )
