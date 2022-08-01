# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Mimic",
    "author" : "xr.tools",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 7, 8),
    "location" : "",
    "warning" : "",
    "category" : "Animation"
}

import socket

import bpy
from bpy.props import *

def getCollection():
    if 'MimicCollection' not in bpy.data.collections:

        bpy.ops.collection.create(name = 'MimicCollection')
        bpy.data.collections[0].children.link(bpy.data.collections['MimicCollection'])
        return bpy.data.collections['MimicCollection']
    else :
        return bpy.data.collections['MimicCollection']

def getMimicRoot():
    if bpy.data.objects.get("MimicRoot") is None:
        print("Creating MimicRoot")
        # collection = getCollection()
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        parent_obj = bpy.context.active_object
        # parent_obj = bpy.data.objects.new(type='EMPTY', name="MimicRoot", enter_editmode=False)
        parent_obj.name = "MimicRoot"
        parent_obj.empty_display_size = 0.2
        parent_obj.empty_display_type = 'ARROWS'
        # bpy.context.scene.collection.objects.link( parent_obj )
        # parent_obj.rotation_mode = "XYZ"
        # parent_obj.rotation_euler.x = math.radians(90)
        
        # collection.add( obj )
        # collection.objects.link(parent_obj)
        return parent_obj
    else:
        print("Found MimicRoot linking") 
        parent_obj = bpy.data.objects.get("MimicRoot")
        return(parent_obj)

def set_location(objects, ob_name, ob_val):
    #objects - list of initialized tracking objects
    #ob_name - name of object recieved
    #ob_val - float value to plot on y-axis
    def str_vec(s):
        try:
            i = 0
            if len(s) != 0:
                print ("set_location: Array len %s." % (len(s)))
                s_arr = s.split(",")
                for val in s_arr:
                    s_arr[i] = float(val)
                    i += 1
                return s_arr
            else:
                print ("set_location: Array was empty.")
                return []
        except Exception as e:
            print("ERROR: set_location > str_vec : %s" % e)
    
    try:
        if ob_name not in objects.keys():
            print("set_location > new object: " + ob_name)
            MimicRoot = getMimicRoot()
            bpy.ops.object.add()
            ob = bpy.context.object

            ob.parent = MimicRoot
            ob.empty_display_size = 0.2
            ob.name = ob_name
    except Exception as e:
        print("set_location > new object ERROR: %s" % e )

    try:    
        s_arr_val = ob_val.split(";")
        if len(s_arr_val) == 1:
            #TODO: set x to val
            objects[ob_name].location[0] = float(s_arr_val[0])
            if(bpy.context.scene.Mimic_auto_record):
                objects[ob_name].keyframe_insert(data_path="location")
        else:
            #set position
            position = str_vec(s_arr_val[0])
            objects[ob_name].location = position
            if(bpy.context.scene.Mimic_auto_record):
                objects[ob_name].keyframe_insert(data_path="location")

            #set rotation
            rotation = str_vec(s_arr_val[1])
            objects[ob_name].rotation_mode = 'QUATERNION'
            objects[ob_name].rotation_quaternion = rotation
            if(bpy.context.scene.Mimic_auto_record):
                objects[ob_name].keyframe_insert(data_path="rotation_quaternion")
    except Exception as e:
        print("set_location ERROR: %s" % e)
        raise
        



class MimicReceiver():
    def run(self, objects, set_location_func):
        #set beginning frame
        
        scene = bpy.context.scene
        try:
            data = self.sock.recv( 1024 * 2 )
            receive = True
            # print(data)
            #parse data
            # print(type(data))           
        except:
            data = None     
            receive = False
        
        # sync = False
        #create or move empties.
        trash = data
        while(receive):   
            data = trash             

            decoded = data.decode('ascii')

            # print (type(decoded))
            print(decoded)

            frameNum = 0
            frameStr = decoded.split("|",1)[0].split("s",1 )[1]
            frameStr = ''.join(i for i in frameStr if i.isdigit())
            # print(frameStr)
            frameNum = int(frameStr)
            # print(frameNum)

            #set start frame to increment from
            if frameNum == 1:
                scene.Mimic_start_frame = scene.frame_current
            else:
                scene.frame_current = frameNum + scene.Mimic_start_frame
            decoded = decoded.rstrip('\x00')

            newValues = decoded.split("|",1)[1].split("~")

            for arr in newValues:
                arr = arr.split(":")
                try:
                    if(len(arr) == 2):
                        set_location_func(objects, arr[0], arr[1])

                except Exception as e:
                    print("run > set_location_func ERROR: %s" % e)
                    print("vals count: %s" % len(arr) )
                    print("decoded: %s" % decoded )
                    print("newValues: %s" % newValues )
                    raise Exception("Error parsing incoming data.")

            #clear buffer                   
            try:
                while self.sock.recv(1024): pass
            except:
                print("buffer empty")
                pass
            receive = False 

    def __init__(self, UDP_PORT, QUIT_PORT):
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind( ("0.0.0.0", UDP_PORT) )

        self.quit_port = QUIT_PORT

        self.original_rotations = {}
        self.original_locations = {}
        
        self.location_dict = {}
        self.rotation_dict = {}
        
        print("Hi, Mimic listening on port " + str(UDP_PORT))

    def __del__(self):
        self.sock.close()
        print("Mimic stopped listening")


class Mimic(bpy.types.Operator):
    bl_idname = "wm.mimic_start"
    bl_label = "Mimic Start"
    bl_description = "Start receiving data from Mimic"
    bl_options = {'REGISTER'}
    
    enabled = False
    receiver = None
    timer = None

    def dumpObj(objects):
        print("Dump Object, length: " + len(objects))
        # for key, value in objects:
        #     print("%s : %s" % (key, value))
    
    def modal(self, context, event):
        if event.type == 'ESC' or not __class__.enabled:
            return self.cancel(context)
        
        if event.type == 'TIMER':
            try:
                self.receiver.run(bpy.data.objects, set_location)
            except Exception as e:
                print("Mimic.modal: ERROR: %s" % (e))
                Mimic.disable()
            # self.receiver.run(bpy.data.objects, set_location, set_rotation)

        
        return {'PASS_THROUGH'}     

    def execute(self, context):
        __class__.enabled = True
        self.receiver = MimicReceiver(context.scene.Mimic_port, None)
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True
        
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(1/context.scene.render.fps, window=bpy.context.window)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        __class__.enabled = False
        context.window_manager.event_timer_remove(self.timer)
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
        # del self.receiver
        
        return {'CANCELLED'}
    
    @classmethod
    def disable(cls):
        if cls.enabled:
            cls.enabled = False

class MimicStop(bpy.types.Operator):
    bl_idname = "wm.mimic_stop"
    bl_label = "Mimic Stop"
    bl_description = "Stop receiving data from Mimic app"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        Mimic.disable()
        return {'FINISHED'}
    
    
class VIEW3D_PT_Panel_Mimic(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Mimic"
    bl_category = "XR Tools"
    
    def draw(self, context):
        scene = bpy.types.Scene

        measure_size = 0.6
        unit_size = 0.3
        box = self.layout.box()
        box_col = box.column()

        row = box_col.split(factor=0.2)
        row.label(text='IP: ')
        row.label(text=get_ip())
        # row.label(text='Cube')

        layout = self.layout
        layout.use_property_split = True
        col = layout.column()

        col.enabled = not Mimic.enabled
        col.prop(context.scene, "Mimic_port", text="Port:")
        col.prop(context.scene, "Mimic_auto_record", text="Auto Record")
        
        if(Mimic.enabled):
            self.layout.operator("wm.mimic_stop", text="Stop")
        else:
            self.layout.operator("wm.mimic_start", text="Listen")
            


            
def init_properties():
    scene = bpy.types.Scene

    scene.Mimic_start_frame = bpy.props.IntProperty(
        name="Start Frame",
        description="Start frame of the last Capture.",
        default = 0)   
    scene.Mimic_port = bpy.props.IntProperty(
        name="Port",
        description="Receive on this port",
        default = 14300,
        min = 0,
        max = 65535)
    scene.Mimic_auto_record = bpy.props.BoolProperty(
        name="Auto Record", 
        default=True,
        description="Start Recording when incoming stream detected.")


def get_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def clear_properties():
    scene = bpy.types.Scene
    
    del scene.Mimic_port
    del scene.Mimic_auto_record
    del scene.Mimic_start_frame
 
classes = (
    Mimic,
    MimicStop,
    VIEW3D_PT_Panel_Mimic
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    # get_Host_name_IP()
    init_properties()

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    clear_properties()
