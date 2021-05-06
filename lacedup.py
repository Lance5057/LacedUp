# This example assumes we have a mesh object selected

bl_info = {
    "name": "New Object",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def create_offset(offset, i1, i2):
    right = i1.co - i2.co
    
    forward = i1.co - i1.handle_right
    
    up = right.cross(forward)
    
    upNormX = forward
    upNormY = right
    upNormZ = up
    
    if forward != (0,0,0) :
        upNormX = forward.normalized()
    if right != (0,0,0) :
        upNormY = right.normalized()
    if up != (0,0,0) :
        upNormZ = up.normalized()
        
    offset1NormX = offset.x * upNormX
    offset1NormY = offset.y * upNormY
    offset1NormZ = offset.z * upNormZ
    
    return offset1NormX + offset1NormY + offset1NormZ

def make_ribbon(self, context):
    if len(bpy.context.selected_objects) == 2:
        r = self.reverse
        # Get the active mesh
        spline_1 = bpy.context.selected_objects[0]
        print(spline_1)
        spline_2 = bpy.context.selected_objects[1]
        print(spline_2)
        
        print("")

        #coord list
        coord_list_1 = []
        coord_list_2 = []
        
        coord_list = []

        points_1 = spline_1.data.splines[0].bezier_points
        points_2 = spline_2.data.splines[0].bezier_points
        
        side = 1

        if len(points_1) == len(points_2):
            for x in range(0+self.removeEnd, len(points_1)-self.removeStart):
                 # todo use vector3 cross to get normalized "up" direction, 
                    #handles can provide "forward", a coord from each list with the same index can provide "right"
                i1 = points_1[x]
                i2 = points_2[x]
                    
                offset1Norm = create_offset(self.offset1, i1, i2)
                offset2Norm = create_offset(self.offset2, i2, i1)
                
                offsetTB = create_offset(Vector((0,0,self.tboffset)), i1, i2)
                
                if side == 1:
                    
                    coord_list_1.append(i1.co + spline_1.location - offsetTB + offset1Norm)
                    coord_list_1.append(i1.co + spline_1.location + offsetTB + offset1Norm)
                    
                    coord_list_2.append(i2.co + spline_2.location - offsetTB + offset2Norm)
                    coord_list_2.append(i2.co + spline_2.location + offsetTB + offset2Norm)
                    side = 2
                else:
                    
                    coord_list_1.append(i2.co + spline_2.location - offsetTB + offset2Norm)
                    coord_list_1.append(i2.co + spline_2.location + offsetTB + offset2Norm)
                    
                    coord_list_2.append(i1.co + spline_1.location - offsetTB + offset1Norm)
                    coord_list_2.append(i1.co + spline_1.location + offsetTB + offset1Norm) 
                    
                   
                    
                    
                    side = 1
    #            o = bpy.data.objects.new( "empty", None )
    #            bpy.context.scene.collection.objects.link( o )
    #            o.empty_display_size = 1
    #            o.empty_display_type = 'PLAIN_AXES' 
    #            o.location = i.co
                #print(points)
            #print(len(points))
            print("")
            
        if r :
            coord_list_1.reverse()
        else :
            coord_list_2.reverse()
        
        for i in coord_list_1:
            coord_list.append(i)
        for i in coord_list_2:
            coord_list.append(i)
        
        for i in coord_list:
            print(i)
                
        curveData = bpy.data.curves.new('ribbon', type='CURVE')
        curveData.dimensions = '3D'
        curveData.resolution_u = 2
        
        polyline = curveData.splines.new('BEZIER')
        polyline.bezier_points.add(len(coord_list)-1)
        for i, coord in enumerate(coord_list):
            x,y,z = coord
            polyline.bezier_points[i].co = (x, y, z)
            polyline.bezier_points[i].handle_left = (x, y, z)
            polyline.bezier_points[i].handle_right = (x, y, z)
            
        curveData.bevel_mode = 'OBJECT'
        
        curveOB = bpy.data.objects.new('myCurve', curveData)
        bpy.context.scene.collection.objects.link( curveOB )
        
    #    bpy.ops.object.select_all(action='DESELECT')
    #    curveOB.select_set(state=True)
    #    bpy.context.view_layer.objects.active = curveOB
    #    curveData.smooth()

    print("")

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a Ribbon"""
    bl_idname = "mesh.add_object"
    bl_label = "Create Ribbon Between 2 Curves"
    bl_options = {'REGISTER', 'UNDO'}

    reverse: BoolProperty(
        name="Reverse",
        default=False,
        subtype='NONE',
        description="Reverse Ribbon Build",
    )
    
    removeEnd: IntProperty(
        name="Remove From End",
        default=0,
        min=0,
        subtype='NONE',
        description="Remove Strands from End",
    )
    
    removeStart: IntProperty(
        name="Remove From Start",
        default=0,
        min=0,
        subtype='NONE',
        description="Remove Strands from Start",
    )
    
    offset1: FloatVectorProperty(
        name="Offset1",
        default=[0.0,0.0,0.0],
        subtype='XYZ',
        description="Offsets the ribbons",
    )
    
    offset2: FloatVectorProperty(
        name="Offset2",
        default=[0.0,0.0,0.0],
        subtype='XYZ',
        description="Offsets the ribbons",
    )
    
    tboffset: FloatProperty(
        name="Top/Bottom Offset",
        default=0.0,
        description="Offsets the top and bottom ribbons to prevent clipping",
    )

    def execute(self, context):

        make_ribbon(self, context)

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Create Ribbon",
        icon='PLUGIN')


# This allows you to right click on a button and link to documentation
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
