import bpy, bmesh
import math
import mathutils
from mathutils import Vector
from math import degrees, radians 
from mathutils import Matrix

# ------------------------------------------------------------------------
#    Bone Management Functions
# ------------------------------------------------------------------------

#----------------------------------------------------------------------
# Bone layer functions 

def change_bone_layer(bone, layer, old_layer):
    bone.layers[layer] = True
    bone.layers[old_layer] = False

def switch_bone_layers(obj, custom_bone_arr):
    for bone in obj.data.bones:
        pbone = obj.pose.bones[bone.name]

        # For original bones
        if bone.name.startswith("ORG-") or bone.name.startswith("m_ORG"):
            change_bone_layer(bone, 16, 0)
            
        # Put on separate layer
        if bone.name.startswith("root"):
            if "track" in bone.name:
                change_bone_layer(bone, 14, 0)
            else:
                change_bone_layer(bone, 3, 0)
        if bone.name.startswith("CTRL"):
            change_bone_layer(bone, 1, 0)
            custom_bone_arr.append(pbone)
        if bone.name.startswith("DEF"):
            change_bone_layer(bone, 8, 0)
        if bone.name.startswith("IK"):
            if "target" in bone.name:
                if ".mch" in bone.name:
                    change_bone_layer(bone, 11, 0)
                else:
                    change_bone_layer(bone, 2, 0)
                    custom_bone_arr.append(pbone)
            else:
                change_bone_layer(bone, 9, 0)
        if bone.name.startswith("FK"):
            change_bone_layer(bone, 10, 0)
        if bone.name.startswith("Tweak"):
            change_bone_layer(bone, 4, 0)
            custom_bone_arr.append(pbone)
        if bone.name.startswith("MCH"):
            if bone.name.endswith(".fk"):
                change_bone_layer(bone, 10, 0)
            if bone.name.endswith(".anchor"):
                change_bone_layer(bone, 12, 0)
            else:
                if bone.name.endswith(".snap"):
                    change_bone_layer(bone, 5, 0)
                    custom_bone_arr.append(pbone)
                else:
                    if bone.name.endswith(".stretch"):
                        change_bone_layer(bone, 13, 0)
                    else:
                        if ".def" in bone.name:
                            change_bone_layer(bone, 15, 0)
                        else:
                            change_bone_layer(bone, 11, 0)


#---------------------------------------------------------------------
# Functions for managing/ creating bone chains

def move_special_bones(obj, bone, parent_arr, b_group):
    # Put master bone strands into a different layer
    if b_group == None:
        index = [pos for pos, char in enumerate(bone.name) if char == "_"][1]
    else:
        index = [pos for pos, char in enumerate(bone.name) if char == "_"][2]
        
    index2 = [pos for pos, char in enumerate(bone.name) if char == "."][0]
    strand_num = bone.name[index+1: index2]
        
    # Moving special bones to other layers
    for y in range(1,len(parent_arr)+1):
        ctrl_fk_bone = obj.data.bones["CTRL-hair_bone_" + strand_num + "." + str(y) + ".fk"]
        ik_target = obj.data.bones["IK_hair_target_" + strand_num]
        snap_bone = obj.data.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".ik.snap"]
        
        change_bone_layer(ctrl_fk_bone, 17, 1)
        change_bone_layer(ik_target, 18, 2)
        change_bone_layer(snap_bone, 20, 5)
        
        if y == len(parent_arr):
            snap_bone2 = obj.data.bones["MCH-hair_bone_" + strand_num + "." + str(y+1) + ".ik.snap"]
            change_bone_layer(snap_bone2, 20, 5)
        
        # Operations for individual strands without master strands
        if b_group == None:
            tk_bone = obj.data.bones["Tweak-hair_bone_" + strand_num + "." + str(y)]
            change_bone_layer(tk_bone, 19, 4)
            
            if y == len(parent_arr):
                tk_bone = obj.data.bones["Tweak-hair_bone_" + strand_num + "." + str(y+1)]
                change_bone_layer(tk_bone, 19, 4)

def create_bone_chains(obj, b_chain_arr, m_b_strands):
    for bone in obj.pose.bones:
        if "_bot" in bone.name:
            # Creates bones and stores them in an array
            parent_arr = bone.parent_recursive
            parent_arr.insert(0,bone)
            b_chain_arr.append(parent_arr)
            if bone.name.startswith("m_"):
                m_index = b_chain_arr.index(parent_arr)
                m_bone = obj.pose.bones[bone.name]
                m_b_strands.append(m_bone)
                
            pbone = obj.pose.bones[bone.name]
            b_group = pbone.bone_group
            
            # Special operations for master bones
            if bone.name.startswith("m_") or b_group == None:
                move_special_bones(obj, bone, parent_arr, b_group)

def check_bone_exists(obj, name):
    try:
        bone = obj.pose.bones[name]
    except:
        bone = None
    
    return(bone)

def create_bone(obj, name, head, tail, inherit_rotation = True, use_deform = False,
        inherit_scale = "FULL"):
    bone = obj.data.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    bone.use_inherit_rotation = inherit_rotation
    bone.use_deform = use_deform
    bone.inherit_scale = inherit_scale
    
    return(bone)

def parent_child_to_parent(child_bone, parent_bone, use_connect = False):
    child_bone.use_connect = use_connect
    child_bone.parent = parent_bone

# ------------------------------------------------------------------------
#    Collection Related Functions
# ------------------------------------------------------------------------

def create_collection(parent_collection, collect_name, collect_arr, suffix):
    # Check if hair widget collection name has numbers attached to the end of it
    for collect in parent_collection.children:
        if collect.name.startswith(collect_name):
            indices = [pos for pos, char in enumerate(collect.name) if char == "."]
            # If widget collection has numbers at the end of it, append the name without the numbers to the array
            if len(indices) > 0:
                c_name = collect.name[0:indices[0]]
                suffix = collect.name[indices[0]: len(collect.name)]
                collect_arr.append(c_name)
            else:
                collect_arr.append(collect.name)
    
    # Make new collection
    if collect_name in collect_arr:
        # If the collection already exists
        widget_collect = parent_collection.children[collect_name + suffix]
    else:
        # If the collection already exists
        widget_collect = bpy.data.collections.new(collect_name)
        
        # Place newly created collection under parent collection
        parent_collection.children.link(widget_collect)
    
    return widget_collect

# ------------------------------------------------------------------------
#    Constraint Related Functions
# ------------------------------------------------------------------------

def remove_constraints(bone):
    if bone != None:
        for c in bone.constraints:
            bone.constraints.remove(c)

def create_locked_track_constraint(bone, name, target, subtarget, head_tail, 
        track_axis, lock_axis):
    lock_track_cnstr = bone.constraints.new("LOCKED_TRACK")
    lock_track_cnstr.name = name
    lock_track_cnstr.target = target
    lock_track_cnstr.subtarget = subtarget
        
    lock_track_cnstr.head_tail = head_tail
    lock_track_cnstr.track_axis = track_axis
    lock_track_cnstr.lock_axis = lock_axis

def create_track_to_constraint(bone, name, target, subtarget, use_target_z,
        track_axis, up_axis, target_space, owner_space):
    track_to_cnstr = bone.constraints.new("TRACK_TO")
    track_to_cnstr.name = name
    track_to_cnstr.target = target
    track_to_cnstr.subtarget = subtarget
    
    track_to_cnstr.use_target_z = use_target_z
    track_to_cnstr.track_axis = track_axis
    track_to_cnstr.up_axis = up_axis
    track_to_cnstr.target_space = target_space
    track_to_cnstr.owner_space = owner_space

def create_copy_transform_constraint(bone, name, target, subtarget,
        mix_mode = "REPLACE", target_space = "WORLD", owner_space = "WORLD"):
    # Copy fk bone constraints
    cp_cnstr = bone.constraints.new("COPY_TRANSFORMS")
    cp_cnstr.name = name
    cp_cnstr.target = target
    cp_cnstr.subtarget = subtarget
    cp_cnstr.mix_mode = mix_mode
    cp_cnstr.target_space = target_space
    cp_cnstr.owner_space = owner_space

def create_damped_track_constraint(bone, target, subtarget, track_axis = "TRACK_Y"):
    dmp_cnstr = bone.constraints.new("DAMPED_TRACK")
    dmp_cnstr.target = target
    dmp_cnstr.subtarget = subtarget
    dmp_cnstr.track_axis = track_axis

def create_stretch_to_constraint(bone, target, subtarget, rest_length):
    stretch_cnstr = bone.constraints.new("STRETCH_TO")
    stretch_cnstr.target = target
    stretch_cnstr.subtarget = subtarget
    stretch_cnstr.rest_length = rest_length

def create_maintain_volume_constraint(bone, owner_space = "WORLD", 
        mode = "STRICT", free_axis = "SAMEVOL_Y", volume = 1):
    vol_cnstr = bone.constraints.new("MAINTAIN_VOLUME")
    vol_cnstr.owner_space = "POSE"
    vol_cnstr.mode = mode
    vol_cnstr.free_axis = free_axis
    vol_cnstr.volume = volume

def create_copy_rot_constraint(bone, target, subtarget, mix_mode = "REPLACE", 
        target_space = "WORLD", owner_space = "WORLD", name = "Copy Rotation"):
    cr_cnstr = bone.constraints.new("COPY_ROTATION")
    cr_cnstr.target = target
    cr_cnstr.subtarget = subtarget
    cr_cnstr.mix_mode = mix_mode
    cr_cnstr.target_space = target_space
    cr_cnstr.owner_space = owner_space
    cr_cnstr.name = name

def create_child_of_constraint(bone, target, subtarget, name = "Child Of",
    use_loc_x = True, use_loc_y = True, use_loc_z = True,
    use_rot_x = True, use_rot_y = True, use_rot_z = True,
    use_scale_x = True, use_scale_y = True, use_scale_z = True):

    co_cnstr = bone.constraints.new("CHILD_OF")
    co_cnstr.name = name
    co_cnstr.target = target
    co_cnstr.subtarget = subtarget
    
    co_cnstr.use_location_x = use_loc_x
    co_cnstr.use_location_y = use_loc_y
    co_cnstr.use_location_z = use_loc_z
    co_cnstr.use_rotation_x = use_rot_x
    co_cnstr.use_rotation_y = use_rot_y
    co_cnstr.use_rotation_z = use_rot_z
    co_cnstr.use_scale_x = use_scale_x
    co_cnstr.use_scale_y = use_scale_y
    co_cnstr.use_scale_z = use_scale_z

    return(co_cnstr)

def create_ik_constraint(bone, target, subtarget, chain_count, pole_target = None):
    ik_cnstr = bone.constraints.new("IK")
    ik_cnstr.target = target
    ik_cnstr.subtarget = subtarget
    ik_cnstr.chain_count = chain_count
    ik_cnstr.pole_target = pole_target

def create_copy_loc_constraint(bone, target, subtarget, name = "Copy Location", 
        use_offset = False, target_space = "WORLD", owner_space = "WORLD"):
    cl_cnstr = bone.constraints.new("COPY_LOCATION")
    cl_cnstr.name = name
    cl_cnstr.target = target
    cl_cnstr.subtarget = subtarget
    cl_cnstr.use_offset = use_offset
    cl_cnstr.owner_space = owner_space
    cl_cnstr.target_space = target_space


# ------------------------------------------------------------------------
#    Custom Bone Functions
# ------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Functions to assist with collections and custom bone creation

def remove_existing_objs(collection, wgt_name):
    for w_obj in collection.objects:
        if w_obj.name.startswith(wgt_name):
            bpy.data.meshes.remove(w_obj.data, do_unlink=True)

def create_mesh_and_link(bm, wgt_name, collection, obj, mat, bone):
    # Make mesh off the bmesh
    me = bpy.data.meshes.new("M_" + wgt_name)
    bm.to_mesh(me)
    bm.free()
    
    # Create object with mesh data
    b_shape = bpy.data.objects.new(wgt_name, me)
    b_shape.matrix_world = mat

    # link object into collection
    collection.objects.link(b_shape)

    pbone = obj.pose.bones[bone.name]
    pbone.custom_shape = b_shape
    pbone.use_custom_shape_bone_size = False
    pbone.bone.show_wire = True

#-------------------------------------------------------------------------
# The types of custom bones

def create_ctrl_bone(ctrl_widget_collect, obj, bone, wgt_name):
    remove_existing_objs(ctrl_widget_collect, wgt_name)
        
    # Create object
    mat_loc = Matrix()
    mat_loc.translation = (bone.head[0],bone.head[1],bone.head[2])
    
    mat = obj.matrix_world @ bone.bone.matrix_local
    mat_rot = Matrix.Rotation(radians(90), 4, "X")
    
    fk_bm = bmesh.new()
    
    # Create circle around bone
    bmesh.ops.create_circle(fk_bm, cap_ends = False, radius=0.05, segments= 8)
    
    # Make line from head to tail

    v1 = fk_bm.verts.new((0, 0, 0))
    v2 = fk_bm.verts.new((0, 0, -(bone.length)))
    fk_bm.edges.new((v1, v2))
                
    # Rotate bmesh
    bmesh.ops.rotate(fk_bm, cent = [0,0,0], matrix = mat_rot ,verts = fk_bm.verts)
    
    create_mesh_and_link(fk_bm, wgt_name, ctrl_widget_collect, obj, mat, bone)

def create_ik_bone(ik_widget_collect, obj, bone, wgt_name):
    #Create object
    loc_mat = Matrix.Translation(Vector((0.0, 0.0, -(bone.length*0.75))))
    mat = obj.matrix_world @ bone.bone.matrix_local
    mat_rot =  Matrix.Rotation(radians(90), 4, "X") @ loc_mat
    ik_bm = bmesh.new()
    
    # Create cone
    bmesh.ops.create_cone(ik_bm, cap_ends = False, segments = 4, diameter1 = 0.005, diameter2 = 0.045, 
                            depth = bone.length*1.5)
    
    # Rotate bmesh
    bmesh.ops.rotate(ik_bm, cent = [0,0,0], matrix = mat_rot ,verts = ik_bm.verts)
    
    # Delete only faces
    for f in ik_bm.faces:
        f.select = True
    bmesh.ops.delete(ik_bm, geom = ik_bm.faces, context = 'FACES_ONLY')
    
    create_mesh_and_link(ik_bm, wgt_name, ik_widget_collect, obj, mat, bone)

def create_tk_bone(tk_widget_collect, obj, bone, wgt_name):
    # Create object
    mat = obj.matrix_world @ bone.bone.matrix_local 
    mat_rot = Matrix.Rotation(radians(90), 4, "X")
    
    tk_bm = bmesh.new()
    
    # Create cone
    bmesh.ops.create_uvsphere(tk_bm, u_segments = 4, v_segments = 4, diameter = 0.045)
    
    # Rotate bmesh
    bmesh.ops.rotate(tk_bm, cent = [0,0,0], matrix = mat_rot ,verts = tk_bm.verts)
    
    # Delete only faces
    for f in tk_bm.faces:
        f.select = True
    bmesh.ops.delete(tk_bm, geom = tk_bm.faces, context = 'FACES_ONLY')
    
    create_mesh_and_link(tk_bm, wgt_name, tk_widget_collect, obj, mat, bone)
    
def create_snap_bone(snap_widget_collect, obj, bone, wgt_name):
    # Create object
    mat = obj.matrix_world @ bone.bone.matrix_local
    mat_rot = Matrix.Rotation(radians(90), 4, "X")
    
    snap_bm = bmesh.new()
    
    # Create uv sphere
    bmesh.ops.create_uvsphere(snap_bm, u_segments = 3, v_segments = 3, diameter = 0.035)
    
    # Rotate bmesh
    bmesh.ops.rotate(snap_bm, cent = [0,0,0], matrix = mat_rot ,verts = snap_bm.verts)
    
    # Delete only faces
    for f in snap_bm.faces:
        f.select = True
        
    bmesh.ops.delete(snap_bm, geom = snap_bm.faces, context = 'FACES_ONLY')
        
    create_mesh_and_link(snap_bm, wgt_name, snap_widget_collect, obj, mat, bone)

# ------------------------------------------------------------------------
#    Custom Variable Related Functions
# ------------------------------------------------------------------------

def add_custom_variable(obj, name, desc, default, min, max):
    rna_ui = obj.get('_RNA_UI')
    if rna_ui is None:
        obj['_RNA_UI'] = {}
        rna_ui = obj['_RNA_UI']

    # Set custom variable settings 
    obj[name] = 1.0
    obj["_RNA_UI"][name] = {
              "description": desc,
              "default": default,
              "min": min,
              "max": max,
              "soft_min":0.0,
              "soft_max":1.0,
              "is_overridable_library":0,
    }

# ------------------------------------------------------------------------
#    Driver Related Functions
# ------------------------------------------------------------------------

def create_constraint_influence_driver(bone, constraint_name):
    try:
        bone.constraints[constraint_name].driver_remove('influence')
    except:
        pass
    fcurve = bone.constraints[constraint_name].driver_add('influence')
    driver = fcurve.driver

    return (driver)

def create_driver_var(driver, driver_type, name, obj, data_path):
    var = driver.variables.new()
    var.type = driver_type
    var.name = name
    target = var.targets[0]
    target.id = obj
    target.data_path = data_path

# ------------------------------------------------------------------------
#    Strand Related Functions
# ------------------------------------------------------------------------
            
def ToggleProperty(obj, sel_bones, scene):
    # Gets scene variables
    tools = scene.ToggleTools
    setPropertyBool = tools.ToggleBool
    propertyName = tools.ToggleEnum

    for bone in sel_bones:
        # Check if property exists for the selected bone
        
        finalPropName = propertyName
        if propertyName.startswith("Anchor"):
            if bone.name.startswith("CTRL-"):
                finalPropName = "Rot_" + propertyName
            else:
                finalPropName = "IK_" + propertyName
        
        if propertyName.startswith("FK_2_IK") or propertyName.startswith("Chain_Copy_Rot"):
            # Find strand num
            if("target" in bone.name and bone.name.startswith("IK")):
                # Creates a list with the positions of the variable c
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][2]
                l_index = len(bone.name)
                
                # Gets the string between the index of the third "_" and the index above it (The strand number)
                strand_num = bone.name[index+1: l_index]
            else:
                # Does the same as above except if the bone has only 2 underscore characters (Every other bone besides the Ik target)
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][1]
                
                # Get index of . to get all numbers between "_" and "."
                index2 = [pos for pos, char in enumerate(bone.name) if char == "."][0]
                strand_num = bone.name[index+1: index2]
            
            # Checks if a master strand is selected
            try:
                top_fk_bone = obj.pose.bones["CTRL-hair_bone_" + strand_num + ".1.fk"]
                prop = top_fk_bone[propertyName]
                
                bone = top_fk_bone
            except:
                # try statement for master bone strands and chain copy property
                try:
                    def_bone = obj.pose.bones["DEF-hair_bone_" + strand_num + ".1"]
                    prop = def_bone[propertyName]
                    
                    bone = def_bone
                except:
                    pass
            
        # Checks if selected bone has the property
        try:
            property = bone[finalPropName]
        except:
            property = None
            
        if property != None:
            # Checks the value of the anchor property
            if setPropertyBool == True:
                propertyValue = tools.ToggleFloat
                
                bone[finalPropName] = propertyValue
            else:
                if property > 0:
                    bone[finalPropName] = 0.0
                else:
                    bone[finalPropName] = 1.0
                    

def KeyProperty(obj, sel_bones, scene):
    # Gets scene variables
    tools = scene.ToggleTools
    setPropertyBool = tools.ToggleBool
    propertyName = tools.ToggleEnum

    for bone in sel_bones:
        crnt_frame = scene.frame_current
        # Check if property exists for the selected bone
        
        finalPropName = propertyName
        if propertyName.startswith("Anchor"):
            if bone.name.startswith("CTRL-"):
                finalPropName = "Rot_" + propertyName
            else:
                finalPropName = "IK_" + propertyName
        
        if propertyName.startswith("FK_2_IK") or propertyName.startswith("Chain_Copy_Rot"):
            # Find strand num
            if("target" in bone.name and bone.name.startswith("IK")):
                # Creates a list with the positions of the variable c
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][2]
                l_index = len(bone.name)
                
                # Gets the string between the index of the third "_" and the index above it (The strand number)
                strand_num = bone.name[index+1: l_index]
            else:
                # Does the same as above except if the bone has only 2 underscore characters (Every other bone besides the Ik target)
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][1]
                
                # Get index of . to get all numbers between "_" and "."
                index2 = [pos for pos, char in enumerate(bone.name) if char == "."][0]
                strand_num = bone.name[index+1: index2]
            
            # Checks if a master strand is selected
            try:
                top_fk_bone = obj.pose.bones["CTRL-hair_bone_" + strand_num + ".1.fk"]
                prop = top_fk_bone[propertyName]
                
                bone = top_fk_bone
            except:
                # try statement for master bone strands and chain copy property
                try:
                    def_bone = obj.pose.bones["DEF-hair_bone_" + strand_num + ".1"]
                    prop = def_bone[propertyName]
                    
                    bone = def_bone
                except:
                    pass
            
        # Checks if selected bone has the property
        try:
            property = bone[finalPropName]
        except:
            property = None
            
        if property != None:
            # Keyframes the property at the current frame
            obj.keyframe_insert(data_path = 'pose.bones["' + bone.name + '"]["' + finalPropName + '"]', frame = crnt_frame)
            
            
def IsolateBones(obj, sel_bones):
    b_group_arr = []
    strand_nums_arr = []
    # Get all the bone groups from the bones selected
    for bone in sel_bones:
        b_group = bone.bone_group
        if b_group != None:
            b_group_arr.append(b_group)
        else:
            # Find strand num
            if("target" in bone.name and bone.name.startswith("IK")):
                # Creates a list with the positions of the variable c
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][2]
                l_index = len(bone.name)
                
                # Gets the string between the index of the third "_" and the index above it (The strand number)
                strand_num = bone.name[index+1: l_index]
            else:
                # Does the same as above except if the bone has only 2 underscore characters (Every other bone besides the Ik target)
                index = [pos for pos, char in enumerate(bone.name) if char == "_"][1]
                
                # Get index of . to get all numbers between "_" and "."
                index2 = [pos for pos, char in enumerate(bone.name) if char == "."][0]
                strand_num = bone.name[index+1: index2]
                
            strand_nums_arr.append(strand_num)
            
    
    # Create a dictionary and revert back to remove duplicates        
    b_group_arr = list(dict.fromkeys(b_group_arr))
    
    # Hides the bones that aren't in the bone group or strand number arrays
    for bone in obj.pose.bones:
        b_group = bone.bone_group
        
        if b_group in b_group_arr:
            bone.bone.hide = False
        else:
            # If a bone without a bone group is selected, isolate based on strand numbers
            if "hair_" in bone.name:
                # Find strand num
                if("target" in bone.name and bone.name.startswith("IK")):
                    # Creates a list with the positions of the variable c
                    index = [pos for pos, char in enumerate(bone.name) if char == "_"][2]
                    l_index = len(bone.name)
                    
                    # Gets the string between the index of the third "_" and the index above it (The strand number)
                    strand_num = bone.name[index+1: l_index]
                else:
                    # Does the same as above except if the bone has only 2 underscore characters (Every other bone besides the Ik target)
                    index = [pos for pos, char in enumerate(bone.name) if char == "_"][1]
                    
                    # Get index of . to get all numbers between "_" and "."
                    index2 = [pos for pos, char in enumerate(bone.name) if char == "."][0]
                    strand_num = bone.name[index+1: index2]
                
                if strand_num in strand_nums_arr:
                    bone.bone.hide = False
                    print(bone.name + " not hidden")
                else:
                    bone.bone.hide = True
                    print(bone.name + " hidden")


# ------------------------------------------------------------------------
#    Snapping Related Functions
# ------------------------------------------------------------------------

def parent_matrix(mat, pose_bone, copy_rot, child_copy_rot, type = 0, m_bone = None, m_bool = False):
    """ This function is used in snapping FK to IK with copy rotation constraints on 
    its parents in a bone chain. This means the child bone will recieve double the rotation 
    transform of the parent. Each child bone would need to be offset by the parent's 
    matrix basis (pose space) inverted for the FK to IK snapping function to work as 
    intended. Each consecutive bone up the chain that copies its parent's rotation 
    need to be offset by the rotation of each one.If a bone along the chain doesn't 
    copy its parent's rotation, the offset value is reset to nothing or it stops 
    increasing the rotation offset."""
    
    
    b_parent = pose_bone.parent
    
    if (b_parent == None or not(("CTRL-") in b_parent.name) and not(("MCH-") in b_parent.name)):
        return mat
    else:
        # Get strand number 
        index = int(pose_bone.name[len(pose_bone.name)-4: len(pose_bone.name)-3])
        
        # Select the parent's parent if the parent is a MCH bone
        if b_parent.name.startswith("MCH-") and index > 1:
            b_parent = b_parent.parent
        else:
            if index == 1:
                return mat
             
        # Special operations for first bone and second bone
        if index == 2:
            if pose_bone["Copy_Rot"] == 1:
                if child_copy_rot == 0:
                    return parent_matrix(mat, b_parent, pose_bone["Copy_Rot"], 1)
                else:
                    # Special operations if function is performed on 2nd fk bone
                    if mat == Matrix():
                        m_final = mat @ b_parent.matrix_basis.inverted()
                    else:
                        if m_bone == None:
                            if m_bool == False:
                                m_final = mat @ b_parent.matrix_basis
                            else:
                                m_final = b_parent.matrix_basis.inverted() @ mat
                        else:
                            m_final = mat
                    return parent_matrix(m_final, b_parent, pose_bone["Copy_Rot"], 1)
            else:
                if child_copy_rot == 0:
                    return Matrix()
                else:         
                    # Keeps offset but stops increasing it
                    if mat == Matrix():
                        return mat
                    else:
                        if m_bool == False:
                            return mat @ b_parent.matrix_basis
                        else:
                            return mat
        
        # Check if pbone copies parent bone rot
        if copy_rot == 1:
            # Resets rotation offset
            if child_copy_rot == 0:
                return Matrix()
            else:
                # Special operations for 3rd bone in chain
                if index == 3 and m_bool == False:
                    if type == 0:
                        m_final = mat @ b_parent.matrix.inverted() @ b_parent.bone.matrix_local
                    else:
                        # Special operations for chain rot and copy rot
                        m_final = b_parent.matrix.inverted() @ b_parent.bone.matrix_local @ b_parent.parent.parent.matrix_basis @ m_bone.matrix_basis @ mat
                        
                else:
                    # Builds offset of consecutive bones with rotation constraints
                    m_final = b_parent.matrix_basis.inverted() @ mat 
                
                if type == 0:
                    if m_bool == False:
                        return parent_matrix(m_final, b_parent, b_parent["Copy_Rot"], pose_bone["Copy_Rot"])
                    else:
                        return parent_matrix(m_final, b_parent, b_parent["Copy_Rot"], pose_bone["Copy_Rot"], m_bool = True)
                else:
                    # Special operations for chain rot and copy rot
                    if m_bool == False:
                        return parent_matrix(m_final, b_parent, b_parent["Copy_Rot"], pose_bone["Copy_Rot"], 1, m_bone)
                    else:
                        return parent_matrix(m_final, b_parent, b_parent["Copy_Rot"], pose_bone["Copy_Rot"], 1, m_bone, m_bool = True)
        else:
            # Resets rotation offset
            if child_copy_rot == 0:
                return Matrix()
            else:         
                # Keeps offset but stops increasing it
                return mat
            
            
            
def chain_parent_recursive(mat, pose_bone, type, child_copy_rot = 1, fk_bone = None, fk_child_bone = None):
    b_parent = pose_bone.parent
    # Get pose bone strand number 
    index = int(pose_bone.name[len(pose_bone.name)-4: len(pose_bone.name)-3])

    if type == 0:
        # Get matrices of master strands
        if (b_parent == None or not(("CTRL-") in b_parent.name) and not(("MCH-") in b_parent.name)):
            return pose_bone.matrix_basis.inverted() @ mat 
        else:
            if b_parent.name.startswith("MCH-") and index > 1:
                b_parent = b_parent.parent
            else:
                if index == 1:
                    return pose_bone.matrix_basis.inverted() @ mat 
            
            copy_rot = pose_bone["Copy_Rot"]
            
            if copy_rot > 0:
                m_final = pose_bone.matrix_basis.inverted() @ mat
                
                return chain_parent_recursive(m_final, b_parent, 0)
            else:
                return pose_bone.matrix_basis.inverted() @ mat
                        
                        
        # Commands for if both copy rot and chain_copy rot are on
    else:
        # Second variation of function used to calculate parent bone matrix instead of current bone matrix
        if (b_parent == None or not(("CTRL-") in b_parent.name) and not(("MCH-") in b_parent.name)):
            return mat
        else:
            if b_parent.name.startswith("MCH-") and index > 1:
                b_parent = b_parent.parent
            else:
                if index == 1:
                    return pose_bone.matrix_basis.inverted() @ mat 
            
            copy_rot = pose_bone["Copy_Rot"]
            if copy_rot > 0:
                m_final = b_parent.matrix_basis.inverted() @ mat
                return chain_parent_recursive(m_final, b_parent, 1)  
            else:
                return mat
    
    
def Anchor_Parent_Recursive(mat, pose_bone, child_anchor = -1):
    try:
        rot_anchor = pose_bone["Rot_Anchor"]
    except:
        rot_anchor = -1
    
    b_parent = pose_bone.parent
    if b_parent.name.startswith("root_"):
        if rot_anchor == 1:
            return b_parent.matrix @ b_parent.bone.matrix_local.inverted() @ mat
        else:
            return mat
    
    if b_parent == None or not(("CTRL-") in b_parent.name) or rot_anchor == -1:
        return mat
    else:
        if rot_anchor == 1:
            if child_anchor == 1:
                return Matrix()
            else:
                pmat = b_parent.parent.matrix_basis.inverted() @ mat
                
                return Anchor_Parent_Recursive(pmat, b_parent, rot_anchor)
        else:
            if child_anchor == 1:
                return Anchor_Parent_Recursive(mat, b_parent, rot_anchor)
            else:
                pmat = b_parent.parent.matrix_basis.inverted() @ mat
                
                return Anchor_Parent_Recursive(pmat, b_parent, rot_anchor)
    
    
def get_pose_matrix_in_other_space(mat, pose_bone):
    """ Returns the transform matrix relative to the pose_bone's current
        transform space.  In other words, presuming that matrix is in
        armature space, assigning the returned matrix onto the pose_bone
        should give it the armature-space transforms of mat.
        TODO: try to handle cases with axis-scaled parents better.
    """
    rest = pose_bone.bone.matrix_local.copy()
    rest_inv = rest.inverted()
    
    if pose_bone.parent != None:
        par_mat = pose_bone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = pose_bone.parent.bone.matrix_local.copy()
    else:
        par_mat = Matrix()
        par_inv = Matrix()
        par_rest = Matrix()

    # Get matrix in bone's current transform space
    smat = rest_inv @ (par_rest @ (par_inv @ mat))

    return smat


def chain_rot_recursive(mat, pose_bone, m_bone, m_copy_rot, child_copy_rot = 0):
    b_parent = pose_bone.parent
    m_parent = m_bone.parent
    copy_rot = pose_bone["Copy_Rot"]
    
    # Get m_bone strand number 
    m_index = int(m_bone.name[len(m_bone.name)-4: len(m_bone.name)-3])
    
    # Get pose bone strand number 
    index = int(pose_bone.name[len(pose_bone.name)-4: len(pose_bone.name)-3])
    
    if index <= 3:
        return mat
    else:
        if copy_rot == 0:
            # Check if fk strand has less strands than master strand
            if child_copy_rot == 1:
                return mat
            else:
                return Matrix()
        else:
            # Check if fk strand has less strands than master strand
            if m_index != index:
                # Build matrix off last master bone
                m_final = mat @ chain_parent_recursive(Matrix(), m_bone, 1)
                return chain_rot_recursive(m_final, b_parent, m_bone, m_bone["Copy_Rot"], copy_rot)
            else:
                # Build matrix off master bone with the same index
                m_final = mat @ chain_parent_recursive(Matrix(), m_bone, 1) 
                return chain_rot_recursive(m_final, b_parent, m_parent, m_parent["Copy_Rot"], copy_rot)
            
        
def extra_bone_recursive(mat, pose_bone, m_bone):
    b_parent = pose_bone.parent
    
    # Get m_bone strand number 
    m_index = int(m_bone.name[len(m_bone.name)-4: len(m_bone.name)-3])
    
    # Get pose bone strand number 
    index = int(pose_bone.name[len(pose_bone.name)-4: len(pose_bone.name)-3])
    
    if m_index == index:
        return mat
    else:
        m_final = mat @ m_bone.matrix_basis.inverted()
        return extra_bone_recursive(m_final, b_parent, m_bone)