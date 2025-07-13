import maya.cmds as cmds

'''
this is a python script made for Autodesk Maya by Lefi Shan (Leficious) - 2024/03/10
the tool pulls information from a single selected object's bounding box and then creates and transfers a smooth ovoid's vertex normals onto the selected object
this tool is particularly useful for when you want a large number of objects to shade more smoothly (stylized leaves, papers, chainmail, etc.)
'''

#selected object in window
objSelected = cmds.ls(sl=True)

#counts selected objects
selectionCount = len(objSelected)
#print (selectionCount, objSelected)

def transfer_sphereNormals(drivenObject):

    #gets the min and max translate values of the bounding box in world space
    boundingBox = cmds.exactWorldBoundingBox(drivenObject)

    #calculates the scale values for the mesh later in world space
    xScale = abs(boundingBox[0] - boundingBox[3])/2
    yScale = abs(boundingBox[1] - boundingBox[4])/2
    zScale = abs(boundingBox[2] - boundingBox[5])/2
    #print(xScale, yScale, zScale)

    #calculates the translate values for the mesh later in world space
    xLoc = (boundingBox[0] + boundingBox[3])/2
    yLoc = (boundingBox[1] + boundingBox[4])/2
    zLoc = (boundingBox[2] + boundingBox[5])/2

    #creates a sphere
    driverMesh = cmds.polySphere(n='driverMesh_uniqueName_sphereNormalBake', sx=25, sy=25, r=1)

    #editable scale value by UI interface
    scaleThreshold = 1.25

    #moves and scales it to the selected mesh's transforms & scales 
    cmds.scale(xScale * scaleThreshold, yScale * scaleThreshold, zScale * scaleThreshold)
    cmds.move(xLoc, yLoc, zLoc)

    #transfers normals from driver to selected
    cmds.transferAttributes('driverMesh_uniqueName_sphereNormalBake', drivenObject, transferPositions=0, transferNormals=1, transferUVs=0, transferColors=0, sampleSpace=0, searchMethod=3, flipUVs=0, colorBorders=1)

    #scene cleanup
    cmds.delete(drivenObject, constructionHistory=True)
    cmds.delete(driverMesh)

def window_combineError():
    
    #deletes a window if there is already a window
    window_name = 'Window'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)
    
    #editable columns and UI text and size
    window = cmds.window(window_name, title='Error Resolution Prompt', widthHeight=(500, 250))
    cmds.columnLayout(adjustableColumn=True)

    #text elements and button functionality
    cmds.text(label="\nYou have more than one object selected.\nWould you like to combine them to continue the command?\n", align="center", font="boldLabelFont")

    #executes command then closes window
    def window_executeDelete(*arg):

        combine_resolution()
        cmds.deleteUI(window_name, window=True)

    #terminates command then closes window
    def window_cancelDelete(*arg):

        cmds.deleteUI(window_name, window=True)
        cmds.warning('WARNING: operation canceled')

    cmds.button(label="Close", align="right", command=window_cancelDelete)
    cmds.button(label="Continue", align="left", command=window_executeDelete)

    #execute
    cmds.showWindow(window)

def combine_resolution():
    
    #combines and deletes history
    cmds.polyUnite(objSelected)
    cmds.delete(constructionHistory=True)

    #defines local variable and executes command
    unitedObj = cmds.ls(sl=True)
    transfer_sphereNormals(unitedObj)

#if only one object is selected
if selectionCount == 1:

    print('The operation was successful')
    transfer_sphereNormals(objSelected)

#if more than 1 object was selected
elif selectionCount > 1:

    #executes the UI error interface command
    window_combineError()
    #error message dialogue
    cmds.warning('WARNING: You have more than one object selected. Please use the dialogue box to resolve the issue')

#if no objects were selected
else:

    #error message dialogue
    cmds.error('ERROR: You do not have an object selected. Please select an object and try again')