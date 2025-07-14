import maya.cmds as cmds

'''
MIT License

Copyright (c) 2025 Leficious

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# Smooth Normal Transfer Tool for Maya
# By Lefi Shan (Leficious) – 2025/07/13
# Transfers smooth vertex normals from a generated ovoid to the selected mesh.
# Adjustable scale, resolution, and offset via UI. Includes live preview, reset, and auto-combine for multi-selection.

preview_visible = [False]
toggle_button_name = "togglePreviewBtn"

def create_preview_sphere(target_obj, scale_multiplier, resolution, offset):
    if cmds.objExists("previewSphere_normalTool"):
        cmds.delete("previewSphere_normalTool")

    bbox = cmds.exactWorldBoundingBox(target_obj)
    center = [(bbox[0] + bbox[3]) / 2 + offset[0],
              (bbox[1] + bbox[4]) / 2 + offset[1],
              (bbox[2] + bbox[5]) / 2 + offset[2]]
    scale = [(bbox[3] - bbox[0]) / 2, (bbox[4] - bbox[1]) / 2, (bbox[5] - bbox[2]) / 2]

    prev_selection = cmds.ls(selection=True)

    sphere = cmds.polySphere(name="previewSphere_normalTool", sx=resolution, sy=resolution, r=1)[0]
    cmds.scale(scale[0] * scale_multiplier, scale[1] * scale_multiplier, scale[2] * scale_multiplier, sphere)
    cmds.move(center[0], center[1], center[2], sphere)

    cmds.setAttr(f"{sphere}.overrideEnabled", 1)
    cmds.setAttr(f"{sphere}.overrideShading", 0)
    cmds.setAttr(f"{sphere}.overrideColor", 18)

    if not cmds.objExists("previewShader_normalTool"):
        shader = cmds.shadingNode('lambert', asShader=True, name="previewShader_normalTool")
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader + "SG")
        cmds.setAttr(shader + ".color", 0.4, 0.8, 1.0, type="double3")
        cmds.setAttr(shader + ".transparency", 0.7, 0.7, 0.7, type="double3")
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
    else:
        sg = "previewShader_normalToolSG"
    cmds.sets(sphere, e=True, forceElement=sg)

    cmds.select(prev_selection, replace=True)

def update_preview_on_change(*args):
    if check_multi_selection():
        return

    selection = cmds.ls(selection=True)
    if not selection or len(selection) != 1:
        return

    scale = cmds.floatSliderGrp("scaleSlider", query=True, value=True)
    res = cmds.intSliderGrp("resSlider", query=True, value=True)
    offset = [
        cmds.floatSliderGrp("offsetXSlider", query=True, value=True),
        cmds.floatSliderGrp("offsetYSlider", query=True, value=True),
        cmds.floatSliderGrp("offsetZSlider", query=True, value=True),
    ]

    create_preview_sphere(selection[0], scale, res, offset)

def toggle_preview_sphere(*args):
    if check_multi_selection():
        return

    selection = cmds.ls(selection=True)
    if not selection or len(selection) != 1:
        return

    if preview_visible[0]:
        if cmds.objExists("previewSphere_normalTool"):
            cmds.delete("previewSphere_normalTool")
        preview_visible[0] = False
        if cmds.control(toggle_button_name, exists=True):
            cmds.button(toggle_button_name, edit=True, label="Show Preview")
    else:
        update_preview_on_change()
        preview_visible[0] = True
        if cmds.control(toggle_button_name, exists=True):
            cmds.button(toggle_button_name, edit=True, label="Hide Preview")

def transfer_sphere_normals(target_obj, scale_multiplier=1.0, resolution=25, offset=[0, 0, 0]):
    create_preview_sphere(target_obj, scale_multiplier, resolution, offset)
    cmds.transferAttributes("previewSphere_normalTool", target_obj, transferPositions=0, transferNormals=1,
                            transferUVs=0, transferColors=0, sampleSpace=0,
                            searchMethod=3, flipUVs=0, colorBorders=1)
    cmds.delete(target_obj, constructionHistory=True)
    cmds.delete("previewSphere_normalTool")
    preview_visible[0] = False

# COMBINE CHECK
def check_multi_selection():
    selection = cmds.ls(selection=True)
    if selection and len(selection) > 1:
        confirm_combine_then_ui()
        return True
    return False

def confirm_combine_then_ui():
    window_name = 'combinePromptWindow'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title='Combine Objects?', widthHeight=(360, 160), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign='center')
    cmds.separator(style='none', height=5)
    cmds.text(label="You selected multiple objects.", align="center", font="boldLabelFont")
    cmds.text(label="Would you like to combine them before continuing?", align="center", wordWrap=True)
    cmds.separator(style='none', height=5)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(170, 170), columnAttach=[(1, 'both', 10), (2, 'both', 10)])
    cmds.button(label="Cancel", height=30, command=lambda *a: cmds.deleteUI(window_name), bgc=(0.4, 0.2, 0.2))
    cmds.button(label="Combine and Continue", height=30,
                command=lambda *a: [cmds.deleteUI(window_name), combine_and_launch_ui()],
                bgc=(0.2, 0.6, 0.2))
    cmds.setParent('..')
    cmds.separator(style='none', height=10)
    cmds.showWindow(window_name)

def combine_and_launch_ui():
    combined_obj = cmds.polyUnite(cmds.ls(selection=True), name="combinedMesh", ch=False)[0]
    cmds.delete(combined_obj, constructionHistory=True)
    cmds.select(combined_obj)
    launch_smooth_normal_ui()

# APPLY & RESET
def apply_transfer_from_ui(*args):
    if check_multi_selection():
        return

    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No object selected.")
        return

    scale = cmds.floatSliderGrp("scaleSlider", query=True, value=True)
    res = cmds.intSliderGrp("resSlider", query=True, value=True)
    offset = [
        cmds.floatSliderGrp("offsetXSlider", query=True, value=True),
        cmds.floatSliderGrp("offsetYSlider", query=True, value=True),
        cmds.floatSliderGrp("offsetZSlider", query=True, value=True),
    ]

    transfer_sphere_normals(selection[0], scale, res, offset)
    cmds.confirmDialog(title="Success", message="Normals transferred successfully.", button=["OK"])

def reset_sliders(*args):
    cmds.floatSliderGrp("scaleSlider", edit=True, value=1.0)
    cmds.intSliderGrp("resSlider", edit=True, value=25)
    cmds.floatSliderGrp("offsetXSlider", edit=True, value=0.0)
    cmds.floatSliderGrp("offsetYSlider", edit=True, value=0.0)
    cmds.floatSliderGrp("offsetZSlider", edit=True, value=0.0)
    update_preview_on_change()

# MAIN UI
def launch_smooth_normal_ui():
    window_name = 'smoothNormalsUI'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title='Smooth Normal Transfer Tool', widthHeight=(420, 410), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, columnAlign='center', rowSpacing=12, columnOffset=["both", 20])

    cmds.separator(style='none', height=10)
    cmds.text(label='Smooth Normals via Sphere', align='center', font='boldLabelFont')
    cmds.separator(style='in', height=5)

    def padded_slider(name, label, slider_type, **kwargs):
        cmds.columnLayout(adjustableColumn=True, columnOffset=("left", -100))  # max shift left
        slider_type(name, label=label, width=395, columnWidth=(1, 150), **kwargs)
        cmds.setParent('..')

    padded_slider("scaleSlider", 'Scale', cmds.floatSliderGrp,
                  field=True, minValue=0.5, maxValue=2.0, value=1.0,
                  cc=update_preview_on_change, dc=update_preview_on_change)

    padded_slider("resSlider", 'Resolution', cmds.intSliderGrp,
                  field=True, minValue=8, maxValue=64, value=25,
                  cc=update_preview_on_change, dc=update_preview_on_change)

    cmds.text(label='Offset Position (World)', align='center', font='boldLabelFont')

    for axis in ['X', 'Y', 'Z']:
        padded_slider(f"offset{axis}Slider", f'{axis} Offset', cmds.floatSliderGrp,
                      field=True, minValue=-100.0, maxValue=100.0, value=0.0,
                      cc=update_preview_on_change, dc=update_preview_on_change)

    cmds.separator(style='none', height=10)

    # button row toggle + defaults
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2,
                   columnAttach=[(1, 'both', 15), (2, 'both', 15)],
                   columnWidth2=(170, 170))
    cmds.button(toggle_button_name, label='Show Preview', height=35,
                bgc=(0.2, 0.5, 0.8), command=toggle_preview_sphere)
    cmds.button(label='Defaults', height=35,
                bgc=(0.3, 0.3, 0.3), command=reset_sliders)
    cmds.setParent('..')

    # center apply transfer button
    cmds.rowLayout(numberOfColumns=1, adjustableColumn=1, columnAlign=(1, 'center'))
    cmds.button(label='Apply Transfer', height=35, width=50, bgc=(0.2, 0.7, 0.3), command=apply_transfer_from_ui)
    cmds.setParent('..')

    cmds.setParent('..')  # exit column layout
    cmds.showWindow(window_name)

# ENTRY
def smart_launch_normal_tool():
    if check_multi_selection():
        return
    launch_smooth_normal_ui()

# RUN
smart_launch_normal_tool()
