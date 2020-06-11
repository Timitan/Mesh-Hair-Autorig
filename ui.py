import bpy, bmesh
import math
import mathutils
import sys
import os
from mathutils import Vector
from math import degrees, radians 
from mathutils import Matrix

from . import bone_creation
from . import constraint_creation 
from . import bone_snapping
from . import strand_functions

import imp
imp.reload(bone_creation)
imp.reload(constraint_creation)
imp.reload(bone_snapping)
imp.reload(strand_functions)

from .bone_creation import *
from .constraint_creation import *
from .bone_snapping import *
from .strand_functions import *

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class ToggleSettings(PropertyGroup):
    
    ToggleBool: BoolProperty(
        name="Set Property Value",
        description="Sets the properties to a value instead of toggling",
        default = False
        )
    
    ToggleFloat: FloatProperty(
            name = "Set To Value",
            description = "The value to set to",
            default = 0.0,
            min = 0.0,
            max = 1.0
            )
            
    ToggleEnum: EnumProperty(
        name="Options:",
        description="Apply button effects onto selected property",
        items=[ ('FK_2_IK', "FK 2 IK", ""),
                ('Chain_Copy_Rot', "Chain Rot", ""),
                ('Copy_Rot', "FK Copy Rot", ""),
                ('Anchor', "FK/ IK Anchor", ""),
                ('Copy_Alt_Root', "FK Alt Root", ""),
                ('Auto_Stretch', "IK Auto Stretch", "")
               ]
        )

# ------------------------------------------------------------------------
#    Buttons
# ------------------------------------------------------------------------

class CreateBonesButton(bpy.types.Operator):
    bl_idname = "har.createbones"
    bl_label = "Create Bones"

    def execute(self, context): 
        # Get Selected object and bones
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object

        CreateBones(obj, sel_bones)

        return {'FINISHED'}
    
class CreateConstraintsButton(bpy.types.Operator):
    bl_idname = "har.createconstraints"
    bl_label = "Create Constraints"
    
    def execute(self, context): 
        # Get Selected object and bones
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object

        CreateConstraints(obj, sel_bones)

        return {'FINISHED'}

class ClearBoneNamesButton(bpy.types.Operator):
    bl_idname = "har.clearbonenames"
    bl_label = "Clear Names"
    
    def execute(self, context): 
        # Get Selected object and bones
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        
        ClearNamesButton(obj, sel_bones)
    
        return {'FINISHED'}
    
class FK2IKButton(bpy.types.Operator):
    bl_idname = "har.fk2ik"
    bl_label = "Snap FK to IK"
    
    def execute(self, context): 
        # TODO
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        
        FkToIkSnapping(obj,sel_bones)
        
        return {'FINISHED'}
        
class IK2FKButton(bpy.types.Operator):
    bl_idname = "har.ik2fk"
    bl_label = "Snap IK to FK"
    
    def execute(self, context): 
        # TODO
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        
        IkToFkSnapping(obj,sel_bones)
        
        return {'FINISHED'}
    

class TogglePropertyButton(bpy.types.Operator):
    bl_idname = "har.toggleproperty"
    bl_label = "Toggle/ Set value"
    
    def execute(self, context): 
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        scene = context.scene
        
        ToggleProperty(obj,sel_bones, scene)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
        
        #dg = bpy.context.evaluated_depsgraph_get() 
        #dg.update()
        #bpy.context.view_layer.update()
        
        return {'FINISHED'}
    
class KeyPropertyButton(bpy.types.Operator):
    bl_idname = "har.keyproperty"
    bl_label = "Keyframe property"
    
    def execute(self, context): 
        # TODO
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        scene = context.scene
        
        KeyProperty(obj, sel_bones, scene)
        
        return {'FINISHED'}
    

class IsolateStrandsButton(bpy.types.Operator):
    bl_idname = "har.isolatestrands"
    bl_label = "Isolate strands"
    
    def execute(self, context): 
        # TODO
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        
        IsolateBones(obj, sel_bones)
        
        return {'FINISHED'}
        
# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class HairAutoRigPanel:
    bl_label = "Hair AutoRig Panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Item"

class HAR_PT_RootPanel(HairAutoRigPanel, bpy.types.Panel):
    bl_idname = "HAR_PT_RootPanel"
    bl_label = "Hair AutoRig Main Panel"
    
    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_ARMATURE','POSE'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        
class HAR_PT_MainPanel(HairAutoRigPanel, bpy.types.Panel):
    bl_parent_id = "HAR_PT_RootPanel"
    bl_idname = "HAR_PT_MainPanel"
    bl_label = "Hair AutoRig Utilities"
    
    @classmethod
    def poll(cls, context):
        # Only display if the object is in pose mode and is a rig generated by Hair Autorig
        try:
            return(context.mode in {'POSE'} and context.active_object.get("rig_bool") == 1)
        except:
            return context.mode in {'POSE'}
    
    def draw(self, context):
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        layout = self.layout
        scene = context.scene
        col = layout.column()
        c = "_"
        d = "."

        col.operator("har.fk2ik")
        col.operator("har.ik2fk")
        
        if (len(sel_bones) > 0):
            for bone in sel_bones:
                if not("hair_" in bone.name) or ".mch" in bone.name or "ORG_" in bone.name:
                    break
                # Find strand num
                if("target" in bone.name and bone.name.startswith("IK")):
                    # Creates a list with the positions of the variable c
                    index = [pos for pos, char in enumerate(bone.name) if char == c][2]
                    l_index = len(bone.name)
                    
                    # Gets the string between the index of the third "_" and the index above it (The strand number)
                    strand_num = bone.name[index+1: l_index]
                else:
                    # Does the same as above except if the bone has only 2 underscore characters (Every other bone besides the Ik target)
                    index = [pos for pos, char in enumerate(bone.name) if char == c][1]
                    
                    # Get index of . to get all numbers between "_" and "."
                    index2 = [pos for pos, char in enumerate(bone.name) if char == d][0]
                    strand_num = bone.name[index+1: index2]
                    
                try:
                    b_strand_name = "DEF-hair_bone_" + strand_num + ".1"
                    b_strand = obj.pose.bones[b_strand_name]
                except:
                    pass
                
                # Get top ctrl fk bone
                ctrl_strand = "CTRL-hair_bone_" + strand_num + ".1.fk" 
                ctrl_bone = obj.pose.bones[ctrl_strand]
 
                ctrl_fk_bones = []
                # Put all selected ctrl_fk_bones into a list
                if bone.name.startswith("CTRL-hair_bone_") and bone.name.endswith(".fk"):
                    ctrl_fk_bones.append(bone)
                    
                # Get current ik target bone
                ik_target_n = "IK_hair_target_" + strand_num
                ik_target = obj.pose.bones[ik_target_n]
 
                ik_tar_bones = []
                # Put all selected ik_target_bones into a list
                if bone.name.startswith("IK_hair_target_"):
                    ik_tar_bones.append(bone)
                
                
                # Check for chain rot custom property
                try:
                    chain_rot = ctrl_bone["Chain_Copy_Rot"]
                except:
                    chain_rot = None
                    
                # Chain Copy rotation switch for CTRL.FK bones
                try:
                    test = ctrl_bone["Chain_Copy_Rot"]
                    if (len(ctrl_fk_bones) >= 0):
                        col.prop(ctrl_bone,'["Chain_Copy_Rot"]', text= "Chain Rot (" + ctrl_strand[ctrl_strand.find("-")+1:ctrl_strand.find(".")] + ")", slider = True)
                except:
                    pass
                
                # FK IK Switch for DEF bones or CTRL FK bones
                try:
                    test = b_strand["FK_2_IK"]
                    if chain_rot == 0 or chain_rot == None:
                        col.prop(b_strand,'["FK_2_IK"]', text= "FK_2_IK (" + b_strand_name[b_strand_name.find("-")+1:b_strand_name.find(".")] + ")", slider = True)
                except:
                    try:
                        test = ctrl_bone["FK_2_IK"]
                        if chain_rot == 0 or chain_rot == None:
                            col.prop(ctrl_bone,'["FK_2_IK"]', text= "FK_2_IK (" + ctrl_strand[ctrl_strand.find("-")+1:ctrl_strand.find(".")] + ")", slider = True)
                    except:
                        pass
                
                for bone in ctrl_fk_bones:
                    # Checks if bones have custom property there
                    try:
                        copy_rot = bone["Copy_Rot"]
                    except:
                        copy_rot = None
                    try:
                        rot_Anc = bone["Rot_Anchor"]
                    except:
                        rot_Anc = None
                        
                    try:
                        copy_alt = bone["Copy_Alt_Root"]
                    except:
                        copy_alt = None
                        
                    if copy_rot != None and (chain_rot == 0 or chain_rot == None):
                        col.prop(bone,'["Copy_Rot"]', text= "FK Copy Rot (" + bone.name + ")", slider = True)  
                    if rot_Anc != None and (chain_rot == 0 or chain_rot == None):
                        col.prop(bone,'["Rot_Anchor"]', text= "FK Rot Anchor (" + bone.name + ")", slider = True) 
                    if copy_alt != None and (chain_rot == 0 or chain_rot == None):  
                        row = col.row()
                        row.prop(bone,'["Copy_Alt_Root"]', text= "FK Copy Alt (" + bone.name + ")", slider = True) 
                        
                        # Disables alt root if root anchor isn't activated
                        if rot_Anc > 0:
                            row.enabled = True
                        else:
                            row.enabled = False
                        
                for bone in ik_tar_bones:
                    # Checks for IK anchor custom property for IK bones
                    try:
                        ik_Anc = bone["IK_Anchor"]
                    except:
                        ik_Anc = None
                    
                    if ik_Anc != None and (chain_rot == 0 or chain_rot == None):
                        col.prop(bone,'["IK_Anchor"]', text= "IK Target Anchor (" + bone.name + ")", slider = True)
                        col.prop(bone,'["Auto_Stretch"]', text= "IK Auto Stretch (" + bone.name + ")", slider = True)

        # Create the sliders
        
        row = col.row() 
        row.separator()
        
        row = col.row()
        row.prop(obj.data, 'layers', index=1, toggle=True, text="Strand FK (Child)")
        row.prop(obj.data, 'layers', index=2, toggle=True, text="Strand IK (Child)")
        
        row = col.row()
        row.prop(obj.data, 'layers', index=4, toggle=True, text="Strand Tweak (Child)")
        row.prop(obj.data, 'layers', index=5, toggle=True, text="Strand Snap (Child)")
        
        row = col.row()
        row.prop(obj.data, 'layers', index=17, toggle=True, text="Strand FK")
        row.prop(obj.data, 'layers', index=18, toggle=True, text="Strand IK")
        
        row = col.row()
        row.prop(obj.data, 'layers', index=19, toggle=True, text="Strand Tweak")
        row.prop(obj.data, 'layers', index=20, toggle=True, text="Strand Snap")
        
        row = col.row()
        row.separator()
        
        row = col.row()
        row.prop(obj.data, 'layers', index=3, toggle=True, text="Root")
        
    
class HAR_PT_FunctionsPanel(HairAutoRigPanel, bpy.types.Panel):
    bl_parent_id = "HAR_PT_RootPanel"
    bl_label = "Strand Extra Functions"
    
    @classmethod
    def poll(cls, context):
        try:
            return(context.mode in {'POSE'} and context.active_object.get("rig_bool") == 1)
        except:
            return context.mode in {'POSE'}
        
    def draw(self, context):
        sel_bones = bpy.context.selected_pose_bones
        obj = bpy.context.active_object
        layout = self.layout
        scene = context.scene
        col = layout.column()
        tools = scene.ToggleTools
        
        col.prop(tools, "ToggleBool")
        
        row = col.row()
        row.prop(tools, "ToggleFloat", slider = True)
        row.enabled = tools.ToggleBool
        
        row = col.row()
        row.separator()
        
        col.prop(tools, "ToggleEnum", text="") 
        
        col.operator("har.toggleproperty")
        col.operator("har.keyproperty")
        
        row = col.row()
        row.separator()
        
        col.operator("har.isolatestrands")


class HAR_PT_SubPanel(HairAutoRigPanel, bpy.types.Panel):
    bl_parent_id = "HAR_PT_RootPanel"
    bl_label = "Create Bones and Constraints"
        
    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_ARMATURE','POSE'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        
        col.operator("har.createbones")
        col.operator("har.createconstraints") 
        col.operator("har.clearbonenames")

class HAR_PT_ParentPanel(HairAutoRigPanel, bpy.types.Panel):
    bl_parent_id = "HAR_PT_SubPanel"
    bl_label = "Root Parent and Alternate Root Parent"
        
    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_ARMATURE','POSE'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        
                
        # Finds a item from a collection
        col.prop_search(data = scene,property = "ArmatureObject",search_data = scene, search_property = "objects")
        
        try:
            obj = scene.objects[scene.ArmatureObject]
        except:
            obj = None
        
        if obj != None:
            col.prop_search(data = scene,property = "BoneRoot",search_data = obj.data,search_property = "bones")
            
            try:
                obj2 = obj.pose.bones[scene.BoneRoot]
            except:
                obj2 = None
            
            if obj2 != None:
                col.prop_search(data = scene,property = "AltBoneRoot",search_data = obj.data,search_property = "bones")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    ToggleSettings,
    CreateBonesButton,
    CreateConstraintsButton,
    ClearBoneNamesButton,
    FK2IKButton,
    IK2FKButton,
    TogglePropertyButton,
    KeyPropertyButton,
    IsolateStrandsButton,
    HAR_PT_RootPanel,
    HAR_PT_FunctionsPanel,
    HAR_PT_MainPanel,
    HAR_PT_SubPanel,
    HAR_PT_ParentPanel
)

def register():
    from bpy.utils import register_class
    import time
    
    for cls in classes:
        register_class(cls)
        
    bpy.types.Scene.ArmatureObject = bpy.props.StringProperty(name="Armature")
    bpy.types.Scene.AltBoneRoot = bpy.props.StringProperty(name="Alt Root Parent")
    bpy.types.Scene.BoneRoot = bpy.props.StringProperty(name="Root Parent")
    bpy.types.Scene.ToggleTools = PointerProperty(type=ToggleSettings)
        
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Scene.ArmatureObject
    del bpy.types.Scene.BoneRoot
    del bpy.types.Scene.AltBoneRoot
    del bpy.types.Scene.ToggleTools
        
if __name__ == "__main__":
    register() 