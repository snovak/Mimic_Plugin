from inspect import getmembers
from pprint import pprint
import re
# pprint(getmembers(...))
# bpy.data.objects['Wolf3D_Head']
import bpy
from bpy.props import *


class MimicConnectFaceShapes(bpy.types.Operator):
    bl_idname = "wm.mimic_connectfaceshapes"
    bl_label = "Connect Mimic Face Shapes"
    bl_description = "Connect Mimic Face Shapes"
    bl_options = {'REGISTER'}
    

    def checkSelection(self):
        try:
            mimic_root = None
            face_obj = None
            
            # Find MimicRoot in all objects
            for obj in bpy.context.selected_objects:
                if re.match(r'^MimicRoot', obj.name):
                    mimic_root = obj
                else:
                    face_obj = obj
            
            if not mimic_root:
                raise Exception("An object starting with 'MimicRoot' must be selected")
                return
            
            if not face_obj:
                raise Exception("A second object with shape keys must also be selected")
                return
                
            print('Selection PASS')
            self.connectDrivers(mimic_root, face_obj)
                
        except Exception as e:
            print('Selection Check ERROR:')
            print(e)

    def execute(self, context):
    
        self.checkSelection()
        return {'FINISHED'}
            
    # The drivers are here
    # bpy.data.shape_keys["Wolf3D_Head"].animation_data.drivers
    def getShapeKeyObj(name):
        print('looking for: ' + name);
        shapeKey = None
        for shape in bpy.data.shape_keys:
            if re.search(name, shape.name):
                print('Found matching shapeKey: ')
                print(shape.name)
                shapeKey = shape

        return shapeKey

    def connectDrivers(self, mimic_root, face_obj):
        print('connectDrivers')
        try: 
            # display keyshapes in face_obj
            #for shapekey in bpy.data.shape_keys:
            # print('--------------' + shapekey.name + '--------------')
                # rename / translate shape key names by changing shapekey.name
            # match shapekeys for object (could include ###.001
            print('searching: ' + face_obj.name)
            #shapeKey = getShapeKeyObj(face_obj)
            shapeKey = face_obj.data.shape_keys
            
            if shapeKey:
                for keyblock in shapeKey.key_blocks:
                    #print('keyblock: ' + keyblock.name)
                    #print('value: ' + str(keyblock.value))
                    # loop through Mimic empties to find name matches
                    # if matched, setup driver. 
                    for bone in mimic_root.pose.bones:
                        #if keyblock.name == empty.name:
                        if self.findMatch(keyblock.name, bone.name):                    
                            print('Matched: ' + keyblock.name + ' to ' + bone.name)
                                    
                            fCurve = keyblock.driver_add('value')
                            driver = fCurve.driver
                            driver.expression = 'var'
                            if len(driver.variables) == 0:
                                driverVariable = driver.variables.new()  
                                driverVariable.type = 'TRANSFORMS'
                                driverVariable.targets[0].id = mimic_root
                                driverVariable.targets[0].bone_target = bone.name
                                driverVariable.targets[0].data_path='location.x'
                                
                                
                                #driver = fCurve.driver.new()
                                #pprint(getmembers(driver))
                                #shapeIndex = bpy.data.shape_keys[face_obj.name].key_blocks.find(driver.name)
                                # add a DriverTarget
                                #print(shapeIndex)
                        
                        # rename / translate block key names by changing keyblock.name
            else:
                print('No shape keys on the selected object.')

        except Exception as e:
            print("error in connectDrivers")
            print(e)
            #pprint(getmembers(face_obj))
            #print('------------------------------------------------')
            #pprint(getmembers(mimic_root))
            
    def findMatch(self, blendshape, mimicObj):
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
