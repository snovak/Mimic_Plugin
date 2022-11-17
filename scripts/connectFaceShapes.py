from inspect import getmembers
from pprint import pprint
import re
# pprint(getmembers(...))
# bpy.data.objects['Wolf3D_Head']
import bpy
from bpy.props import *

def checkSelection():
    try:
        # if selected objects is 2
#        if not len(bpy.context.selected_objects) == 2:
#            raise Exception("There should be 2 objects selected. First, select the face object, with shape keys.  Then select Mimic Root object.")
#            return 0
        # if face_obj is of type object and has > 10 shape keys 
        if not bpy.context.selected_objects[0].name == 'MimicRoot':
            raise Exception("Mimic Root should be selected first")
            return
        else:
            print('Selection PASS')
            for i in range(len(bpy.context.selected_objects)):
                if i > 0:
                    connectFaceShapes(bpy.context.selected_objects[0], bpy.context.selected_objects[i])
    except Exception as e:
        print('Selection Check ERROR:')
        print(e)
        
# The drivers are here
# bpy.data.shape_keys["Wolf3D_Head"].animation_data.drivers

def connectFaceShapes(mimic_root, face_obj):
    print('connectFaceShapes')
    try: 
        # display keyshapes in face_obj
        #for shapekey in bpy.data.shape_keys:
           # print('--------------' + shapekey.name + '--------------')
            # rename / translate shape key names by changing shapekey.name
            for keyblock in  bpy.data.shape_keys[face_obj.name].key_blocks:
                #print('keyblock: ' + keyblock.name)
                #print('value: ' + str(keyblock.value))
                # loop through Mimic empties to find name matches
                # if matched, setup driver. 
                for empty in mimic_root.children:
                    #if keyblock.name == empty.name:
                    if findMatch(keyblock.name, empty.name):                    
                        print('Matched: ' + keyblock.name + ' to ' + empty.name)
                                
                        fCurve = keyblock.driver_add('value')
                        driver = fCurve.driver
                        driver.expression = 'var'
                        if len(driver.variables) == 0:
                            driverVariable = driver.variables.new()  
                            driverVariable.targets[0].id = empty
                            driverVariable.targets[0].data_path='location.x'
                            
                        
                        #driver = fCurve.driver.new()
                        #pprint(getmembers(driver))
                        #shapeIndex = bpy.data.shape_keys[face_obj.name].key_blocks.find(driver.name)
                        # add a DriverTarget
                        #print(shapeIndex)
                
                # rename / translate block key names by changing keyblock.name
        

    except Exception as e:
        print(e)
        #pprint(getmembers(face_obj))
        #print('------------------------------------------------')
        #pprint(getmembers(mimic_root))
        
def findMatch(blendshape, mimicObj):
    #print('checking: ' + blendshape + ' <~> ' + mimicObj)
    
    if mimicObj == blendshape:
        return(True)
    
    searchReplaceList = [['_L$', 'Left'],['_R$', 'Right']]

    for srPair in searchReplaceList:
        if re.sub(srPair[0], srPair[1], mimicObj) == blendshape:
            return True
        
    return False
#    mimicObjReg = ""
#    mimicObjReg = re.sub("_L$","Left", mimicObj)
#    if blendshape == mimicObjReg:
#        return(True)
#    mimicObjReg = re.sub("_R$","Right", mimicObj)
#    if blendshape == mimicObjReg:
#        return(True)
#
    return(False)

checkSelection()