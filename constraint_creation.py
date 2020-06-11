import bpy, bmesh
import math
import mathutils
import sys
import os
from mathutils import Vector
from math import degrees, radians 
from mathutils import Matrix

# Custom modules

from . import utils

import imp
imp.reload(utils)

from .utils import *

# ------------------------------------------------------------------------
#    Functions
# ------------------------------------------------------------------------

def CreateConstraints(obj, sel_bones):
    b_chain_arr = []
    custom_bone_arr = []
    
    # Switch currently viewed layers
    obj.data.layers[1] = True
    obj.data.layers[2] = True
    obj.data.layers[17] = True
    obj.data.layers[18] = True
    obj.data.layers[16] = False
    
    # Check whether it's pose mode or not
    switch_bone_layers(obj, custom_bone_arr)
            
    # Add custom property to object
    
    add_custom_variable(obj, "rig_bool", "Shows the hair autorig panel", 1, 1, 1)
    
    #--------------------------------------------------------------------------------------------
    
    m_b_strands = []
    data_bones = obj.data.bones

    # Create array filled with arrays of bone chains
    create_bone_chains(obj, b_chain_arr, m_b_strands)

    # Get number of chains in the array
    chain_count = len(b_chain_arr)  
    
    #--------------------------------------------------------------------------------------------
    
    # Create objects
    bpy.ops.object.mode_set(mode='OBJECT')
    
    collect_name = obj.name + " Hair Widgets"
    collect_arr = []
    suffix = ""
    
    # Get all collections object is in
    obj_collect = obj.users_collection
    
    # Check if object is in any collections
    if len(obj_collect) > 0:
        # Object is in a collection
        parent_collection = obj_collect[0]
    else:
        # Use scene collection if the object isn't in a collection
        parent_collection = bpy.context.scene.collection

    widget_collect = create_collection(parent_collection, collect_name, collect_arr, suffix)
    print(widget_collect)
        
    #--------------------------------------------------------------------------------------------
    # Make sub collections for bone types
    
    # CTRL FK bone collection
    
    ctrl_collect_name = obj.name + " CTRL FK Bones"
    collect_arr = []
    suffix = ""
    
    ctrl_widget_collect = create_collection(widget_collect, ctrl_collect_name, collect_arr, suffix)
    
    #--------------------------------------------------------------------------------------------    
    # IK bone collection
    
    ik_collect_name = obj.name + " IK Target Bones"
    collect_arr = []
    suffix = ""
    
    ik_widget_collect = create_collection(widget_collect, ik_collect_name, collect_arr, suffix)
        
    #--------------------------------------------------------------------------------------------    
    # Tweak bone collection
    
    tk_collect_name = obj.name + " Tweak Bones"
    collect_arr = []
    suffix = ""
    
    tk_widget_collect = create_collection(widget_collect, tk_collect_name, collect_arr, suffix)
        
    #--------------------------------------------------------------------------------------------    
    # Snap bone collection

    snap_collect_name = obj.name + " MCH Snap Tweak Bones"
    collect_arr = []
    suffix = ""
    
    snap_widget_collect = create_collection(widget_collect, snap_collect_name, collect_arr, suffix)
    
    #--------------------------------------------------------------------------------------------
    # Set custom bone shape for every bone in array
    
    # CTRL FK bones
    for bone in custom_bone_arr:
        b_name = bone.name
        collect_name_arr = []

        if bone.name.startswith("CTRL"):
            wgt_name = "WGT-" + bone.name
            create_ctrl_bone(ctrl_widget_collect, obj, bone, wgt_name)
                
        #--------------------------------------------------------------------------------------------  
        # Create custom ik bones custom object
        
        if bone.name.startswith("IK"):
            wgt_name = "WGT-" + bone.name
            
            create_ik_bone(ik_widget_collect, obj, bone, wgt_name)
                
        #--------------------------------------------------------------------------------------------  
        # Create custom tweak bones custom object
        
        if bone.name.startswith("Tweak"):
            wgt_name = "WGT-" + bone.name
            
            create_tk_bone(tk_widget_collect, obj, bone, wgt_name)

        #--------------------------------------------------------------------------------------------  
        # Create custom MCH snap bones custom object
                
        if bone.name.startswith("MCH"):
            if bone.name.endswith(".snap"):
                wgt_name = "WGT-" + bone.name

                create_snap_bone(snap_widget_collect, obj, bone, wgt_name)
                    
    # Go back to pose mode to set up bone constraints
    bpy.ops.object.mode_set(mode='POSE')
    
    #--------------------------------------------------------------------------------------------
    # Create constraints
    
    # Retrieve scene armature and bone if there are any
    scene = bpy.context.scene
    
    # Get root parents and their objects
    try:
        scn_arm = scene.objects[scene.ArmatureObject]
    except:
        scn_arm = None
        
    if scn_arm != None:
        try:
            scn_root = scn_arm.pose.bones[scene.BoneRoot]
        except:
            scn_root = None
        try:
            scn_alt_root = scn_arm.pose.bones[scene.AltBoneRoot]
        except:
            scn_alt_root = None
    else:
        scn_alt_root = None
        scn_root = None
    
    #----------------------------------------------------------------------------
    # Create root_track bone constraints
    
    # Get the correct root bones
    root_bone = obj.pose.bones["root_bone"]
    trackTo_bone = obj.pose.bones["root_track_bone.track"]
    root_track_bone = obj.pose.bones["root_track_bone"]
    
    create_locked_track_constraint(root_track_bone, "Locked track", obj, trackTo_bone.name, 1.0, "TRACK_Z", "LOCK_Y")
    
    create_track_to_constraint(trackTo_bone, "Track to", obj, root_bone.name, True, 
                                "TRACK_Z", "UP_X", "POSE", "POSE")
    
    # For loop for every operation done once per chain
    for v in range(0, chain_count):
        b_name = b_chain_arr[v][0].name
        
        if b_name.startswith("m_"):
            index = [pos for pos, char in enumerate(b_name) if char == "_"][2]
        else:
            index = [pos for pos, char in enumerate(b_name) if char == "_"][1]
            
        #print(b_name)
        index2 = [pos for pos, char in enumerate(b_name) if char == "."][0]
            
        strand_num = b_name[index+1: index2]
        
        # Get number of bones in each chain
        b_num = len(b_chain_arr[v])
        
        # For loop for every operation done once per bone
        for y in range(1, b_num+1):
            # Get names of bones
            for bone in obj.pose.bones:
                if "ORG-hair_bone_" + strand_num + "." + str(y) in bone.name:
                    org_bone = obj.pose.bones[bone.name]
            
            fk_bone = check_bone_exists(obj, "FK-hair_bone_" + strand_num + "." + str(y))
            ik_bone = check_bone_exists(obj, "IK-hair_bone_" + strand_num + "." + str(y))
            tk_bone = check_bone_exists(obj, "Tweak-hair_bone_" + strand_num + "." + str(y))
            def_bone = check_bone_exists(obj, "DEF-hair_bone_" + strand_num + "." + str(y))
                
            # Get all the types of bones 
            mch_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".ik"]
            snap_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".ik.snap"]
            ctrl_fk_bone = obj.pose.bones["CTRL-hair_bone_" + strand_num + "." + str(y) + ".fk"]
            ik_target = obj.pose.bones["IK_hair_target_" + strand_num]
            fk_anchor = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".fk.anchor"]
            stretch_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".ik.stretch"]
            snap_bone2 = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(b_num+1) + ".ik.snap"]
            stretch_def_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(y) + ".ik.def"]
            
            b_group = org_bone.bone_group
            ik_target.bone_group = b_group
            ctrl_fk_bone.bone_group = b_group
            snap_bone.bone_group = b_group
            
            # Set the last snap bone's bone group
            snap_bone2.bone_group = b_group
            
            if tk_bone != None:
                tk_bone.bone_group = b_group
                
                # Set the last tk bone bone group
                tk_bone2 = obj.pose.bones["Tweak-hair_bone_" + strand_num + "." + str(b_num+1)]
                tk_bone2.bone_group = b_group
                
            # Sets the bone groups

            #--------------------------------------------------------------------------------------------
            # Get length of master bone and strand number
            f_bone = "CTRL-hair_bone_" + strand_num + ".1.fk"
            
            c = "_"
            d = "."
            
            # If the ORG bone group of a strand is equal to a master bone strand bone group
            if len(m_b_strands) > 0 and b_group != None:
                for m_bone in m_b_strands:
                    if b_group == m_bone.bone_group:
                        m_b_num = (len(m_bone.parent_recursive))+1
                        
                        index = [pos for pos, char in enumerate(m_bone.name) if char == "_"][2]
                        index2 = [pos for pos, char in enumerate(m_bone.name) if char == "."][0]
                        
                        m_strand_num = m_bone.name[index+1: index2]
                        #test = obj.pose.bones["CTRL-hair_bone_" + m_strand_num + "." + str(m_b_num) + ".fk"]
                        m_ik_target = "IK_hair_target_" + m_strand_num
                                                
                        try:
                            test = obj.pose.bones["CTRL-hair_bone_" + m_strand_num + "." + str(y) + ".fk"]
                            m_target = "CTRL-hair_bone_" + m_strand_num + "." + str(y) + ".fk"
                        except:
                            m_target = "CTRL-hair_bone_" + m_strand_num + "." + str(m_b_num) + ".fk"
            else:
                m_target = ""
                m_ik_target = ""
                
            #--------------------------------------------------------------------------------------------
            
            # Remove old constraints before adding new ones
            
            remove_constraints(fk_bone)
            remove_constraints(ik_bone)
            remove_constraints(def_bone)
            remove_constraints(mch_bone)
            remove_constraints(tk_bone)
            remove_constraints(ctrl_fk_bone)
            remove_constraints(snap_bone)
            
            #-----------------------------------------------------------------------------
            # Set custom shapes for CTRL and Tweak bones
            
            # Custom shape for last tweak bone
            if tk_bone != None: 
                if y == b_num:
                    tk_plus = y+1
                    tk_plus_bone = obj.pose.bones["Tweak-hair_bone_" + strand_num + "." + str(tk_plus)]
                    
                    cust_shape = bpy.data.objects["WGT-" + tk_plus_bone.name]
                    tk_plus_bone.custom_shape = cust_shape
                    tk_plus_bone.use_custom_shape_bone_size = False
                    tk_plus_bone.bone.show_wire = True
                
            
            #-----------------------------------------------------------------------------
            # Set up DEF bones
            
            if def_bone != None: 
                # Copy fk bone constraints
                create_copy_transform_constraint(def_bone, "Copy FK", obj, fk_bone.name)
                
                # Copy ik bone constraints
                create_copy_transform_constraint(def_bone, "Copy IK", obj, ik_bone.name)
                
                # Add drivers to constraint of top def bone to control FK IK 
                ik_driver = create_constraint_influence_driver(def_bone, "Copy IK")

                data_path = 'pose.bones["DEF-hair_bone_' + strand_num + '.1"]["FK_2_IK"]'
                create_driver_var(ik_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)

                # Have the master FK2IK slider control child FK2IK
                if ctrl_fk_bone.name != m_target and m_target != "":
                    data_path = 'pose.bones["CTRL-hair_bone_' + m_strand_num + '.1.fk"]["FK_2_IK"]'
                    create_driver_var(ik_driver, "SINGLE_PROP", "m_var", obj, data_path)

                    data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                    create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)
                    
                    ik_driver.type = "SCRIPTED"
                    ik_driver.expression = "cust_prop_var if chain_rot_var == 0 else m_var"
                else:
                    ik_driver.type = "AVERAGE"
            
            #-----------------------------------------------------------------------------
            # Set up Tweak Bones
            
            if tk_bone != None:
                create_copy_transform_constraint(tk_bone, "Copy IK", obj, snap_bone.name,
                    "AFTER", "LOCAL_WITH_PARENT", "LOCAL_WITH_PARENT")
                
                # Add drivers to constraint of tweak bones to control fk ik tweak bones
                ik_driver = create_constraint_influence_driver(tk_bone, "Copy IK")

                data_path = 'pose.bones["DEF-hair_bone_' + strand_num + '.1"]["FK_2_IK"]'
                create_driver_var(ik_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)
                
                if (ctrl_fk_bone.name != m_target and m_target != ""):
                    data_path = 'pose.bones["CTRL-hair_bone_' + m_strand_num + '.1.fk"]["FK_2_IK"]'
                    create_driver_var(ik_driver, "SINGLE_PROP", "m_var", obj, data_path)

                    data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                    create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)

                    ik_driver.type = "SCRIPTED"
                    ik_driver.expression = "cust_prop_var if chain_rot_var == 0 else m_var"
                else:
                    ik_driver.type = "AVERAGE"
            
                # Copy transforms of fk mch bone
                create_copy_transform_constraint(tk_bone, "Copy fk", obj, ctrl_fk_bone.name,
                    "AFTER", "LOCAL_WITH_PARENT", "LOCAL_WITH_PARENT")
                
                 # Add drivers to constraint of tweak bones to control fk ik tweak bones
                fk_driver = create_constraint_influence_driver(tk_bone, "Copy fk")

                data_path = 'pose.bones["DEF-hair_bone_' + strand_num + '.1"]["FK_2_IK"]'
                create_driver_var(fk_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)

                fk_driver.type = "SCRIPTED"
                
                if (ctrl_fk_bone.name != m_target and m_target != ""):
                    data_path = 'pose.bones["CTRL-hair_bone_' + m_strand_num + '.1.fk"]["FK_2_IK"]'
                    create_driver_var(fk_driver, "SINGLE_PROP", "m_var", obj, data_path)

                    data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                    create_driver_var(fk_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)

                    fk_driver.type = "SCRIPTED"
                    fk_driver.expression = "abs(cust_prop_var-1) if chain_rot_var == 0 else abs(m_var-1)"
                else:
                    fk_driver.expression = "abs(cust_prop_var-1)"
            
            #-----------------------------------------------------------------------------
            # Set up IK Bones
            
            if tk_bone != None:
                # Set up constraints
                # Copy transforms of tweak bone
                create_copy_transform_constraint(ik_bone, "Copy Transforms", obj, tk_bone.name,
                    "REPLACE", "LOCAL_WITH_PARENT", "LOCAL_WITH_PARENT")
                
                # Track to next tweak bone in line
                create_damped_track_constraint(ik_bone, obj, "Tweak-hair_bone_" + strand_num + "." + str(y+1))

                create_stretch_to_constraint(ik_bone, obj, "Tweak-hair_bone_" + strand_num + "." + str(y+1), fk_bone.bone.length)
            
            #-----------------------------------------------------------------------------
            # Set up MCH IK stretch bones
            
            create_copy_transform_constraint(stretch_bone, "Copy Transforms", obj, mch_bone.name,
                    "REPLACE", "LOCAL", "LOCAL")
            
            # Set the stretch property of IK to 1
            stretch_bone.ik_stretch = 1
            
            #-----------------------------------------------------------------------------
            # Set up MCH IK def stretch bones
            create_copy_transform_constraint(stretch_def_bone, "Copy Transforms", obj, stretch_bone.name,
                    "REPLACE", "POSE", "POSE")
            
            create_maintain_volume_constraint(stretch_def_bone, "POSE")
            
            #-----------------------------------------------------------------------------
            # Set up FK bones
            
            if tk_bone != None:    
                # Set up constraints
                # Copy transforms of tweak bone
                create_copy_transform_constraint(fk_bone, "Copy Transforms", obj, tk_bone.name)

                # Track to next tweak bone in line
                create_damped_track_constraint(fk_bone, obj, "Tweak-hair_bone_" + strand_num + "." + str(y+1))

                create_stretch_to_constraint(fk_bone, obj, "Tweak-hair_bone_" + strand_num + "." + str(y+1), fk_bone.bone.length)
            
            #-----------------------------------------------------------------------------
            # Set up CTRL_FK bones
            
            # Set up constraints
            
            # Try statement to check if the bone has a parent or not
            try:
                p_fk_bone = obj.pose.bones["CTRL-hair_bone_" + strand_num + "." + str(y-1) + ".fk"]
            except:
                p_fk_bone = None

            if p_fk_bone != None:
                # Copy rotation of parent
                create_copy_rot_constraint(ctrl_fk_bone, obj, p_fk_bone.name, "AFTER", "LOCAL", "LOCAL")
                
                # Add custom property to each FK CTRL bone
                add_custom_variable(ctrl_fk_bone, "Copy_Rot", "Parent Rotation Influence", 1, 0, 1)

                # Set custom variable settings
                if(ctrl_fk_bone.name != m_target and m_target != ""):
                    ctrl_fk_bone["Copy_Rot"] = 0.0
                else:
                    ctrl_fk_bone["Copy_Rot"] = 1.0
                
                # Add driver to constraint of ctrl_fk bone to turn it on and off
                fk_driver = create_constraint_influence_driver(ctrl_fk_bone, "Copy Rotation")

                data_path = 'pose.bones["' + ctrl_fk_bone.name + '"]["Copy_Rot"]'
                create_driver_var(fk_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)
                fk_driver.type = "MAX"

            else:
                # Add custom variable to the top of the fk bone
                
                # Makes sure the ctrl_fk bone is the first bone and isn't the master bone
                if ctrl_fk_bone.name == f_bone and (ctrl_fk_bone.name != m_target) and m_target != "":

                    add_custom_variable(ctrl_fk_bone, "Chain_Copy_Rot", "Master bone chain Rotation influence", 1, 0, 1)
                    
         
            # Constraints for non-master strands
            if (ctrl_fk_bone.name != m_target and m_target != ""):

                create_copy_rot_constraint(ctrl_fk_bone, obj, m_target, "AFTER", "LOCAL", "LOCAL", "Copy Master Rot")
                
                # Set up driver to not copy rot of master bone when IK's on
                if len(ctrl_fk_bone.constraints) > 1:
                    try:
                        ctrl_fk_bone.constraints["Copy Master Rot"].driver_remove('influence')
                    except:
                        pass
                else:
                    try:
                        ctrl_fk_bone.constraints["Copy Rotation"].driver_remove('influence')
                    except:
                        pass
                    
                # First bone of each strand (_1) has 1 less constraint than the other constraints
                try:
                    fcurve = ctrl_fk_bone.constraints["Copy Master Rot"].driver_add('influence')
                except:
                    fcurve = ctrl_fk_bone.constraints["Copy Rotation"].driver_add('influence')
                fk_driver = fcurve.driver

                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(fk_driver, "SINGLE_PROP", "var", obj, data_path)
                fk_driver.type = "AVERAGE"


            # Make Rot anchor variables and drivers for all fk bones
            add_custom_variable(ctrl_fk_bone, "Rot_Anchor", "Influence for parent rotations", 1, 0, 1)
            ctrl_fk_bone["Rot_Anchor"] = 0.0
                     
            if scn_alt_root != None:     
                add_custom_variable(ctrl_fk_bone, "Copy_Alt_Root", "Influence for copying alt root", 1, 0, 1)
                ctrl_fk_bone["Copy_Alt_Root"] = 0.0
            
            # Add driver to inherit rotation property of fk anchor bone
            fk_data_bone = obj.data.bones[fk_anchor.name]     
            
            cr_cnstr = create_child_of_constraint(fk_anchor, obj, fk_anchor.parent.name, "Copy Parent Rotation",
                False, False, False,
                True, True, True,
                False, False, False)

            # Set inverse on child of constraint
            mat_final = obj.matrix_world @ fk_anchor.parent.matrix
            cr_cnstr.inverse_matrix = mat_final.inverted()
            
            anchor_driver = create_constraint_influence_driver(fk_anchor, "Copy Parent Rotation")

            data_path = 'pose.bones["' + ctrl_fk_bone.name + '"]["Rot_Anchor"]'
            create_driver_var(anchor_driver, "SINGLE_PROP", "rot_anchor_var", obj, data_path)
            anchor_driver.type = "SCRIPTED"
            
            #------------------------------------------------------------------------------
            # Make bone copy the rotation of root track bone

            ctr_cnstr = create_child_of_constraint(fk_anchor, obj, root_track_bone.name, "Copy Root Track",
                False, False, False,
                True, True, True, 
                False, False, False)
            
            mat_rot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Y')
            
            # Set inverse on child of constraint
            mat_final = obj.matrix_world @ root_track_bone.matrix @ mat_rot
            ctr_cnstr.inverse_matrix = mat_final.inverted()
     
            # Create driver
            track_driver = create_constraint_influence_driver(fk_anchor, "Copy Root Track")

            data_path = 'pose.bones["' + ctrl_fk_bone.name + '"]["Rot_Anchor"]'
            create_driver_var(track_driver, "SINGLE_PROP", "rot_anchor_var", obj, data_path)
            track_driver.type = "SCRIPTED"
        
            # Add another child of constraint
            # Copy the alternative root bone if it's present
            if scn_alt_root != None:
                child_cnstr = create_child_of_constraint(fk_anchor, scn_arm, scn_alt_root.name, "Copy Alt Root Parent",
                    False, False, False,
                    True, True, True, 
                    False, False, False)
                
                # Get matrix of the fk bone
                rot_mat = scn_alt_root.matrix
                
                # Set inverse on child of constraint
                mat_final = obj.matrix_world @ rot_mat
                child_cnstr.inverse_matrix = mat_final.inverted()
                
                anchor_cnstr_driver = create_constraint_influence_driver(fk_anchor, "Copy Alt Root Parent")
                
                # Make a variable to control the influence from the rot anchor property
                data_path = 'pose.bones["' + ctrl_fk_bone.name + '"]["Rot_Anchor"]'
                create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "rot_anchor_var", obj, data_path)
                
                anchor_cnstr_driver.type = "SCRIPTED"
                
                # Get copy alt root property
                data_path = 'pose.bones["'+ ctrl_fk_bone.name +'"]["Copy_Alt_Root"]' 
                create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "copy_alt_var", obj, data_path)

            # For child strand bones
            if (ctrl_fk_bone.name != m_target and m_target != ""):
                # Get chain_copy_rot
                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(anchor_driver, "SINGLE_PROP", "chain_var", obj, data_path)

                # Get master strand rot anchor
                data_path = 'pose.bones["'+ m_target +'"]["Rot_Anchor"]'
                create_driver_var(anchor_driver, "SINGLE_PROP", "m_anchor_var", obj, data_path)
                               
                anchor_driver.expression = "abs(m_anchor_var-1) if chain_var > 0 else abs(rot_anchor_var-1)"
                
                #-------------------------------------------------------------------------------------------
                # Variables for track bones
                # Get chain_copy_rot
                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(track_driver, "SINGLE_PROP", "chain_var", obj, data_path)

                # Get master strand rot anchor
                data_path = 'pose.bones["'+ m_target +'"]["Rot_Anchor"]'
                create_driver_var(track_driver, "SINGLE_PROP", "m_anchor_var", obj, data_path)
                               
                track_driver.expression = "m_anchor_var if chain_var > 0 else rot_anchor_var"
                
                if scn_alt_root != None:
                    # Get copy alt root property
                    data_path = 'pose.bones["'+ ctrl_fk_bone.name +'"]["Copy_Alt_Root"]' 
                    create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "copy_alt_var", obj, data_path)
                    
                    # Make the same variables for the constraint driver
                    # Get chain_copy_rot
                    data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                    create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "chain_var", obj, data_path)

                    # Get master strand rot anchor
                    data_path = 'pose.bones["'+ m_target +'"]["Rot_Anchor"]'
                    create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "m_anchor_var", obj, data_path)
                    
                    # Get master copy alt root property
                    data_path = 'pose.bones["'+ m_target +'"]["Copy_Alt_Root"]' 
                    create_driver_var(anchor_cnstr_driver, "SINGLE_PROP", "m_copy_alt_var", obj, data_path)
                    
                    anchor_cnstr_driver.expression = "m_copy_alt_var if (chain_var > 0 and m_anchor_var > 0) else copy_alt_var if (rot_anchor_var > 0 and chain_var == 0) else 0"

            else:
                # For master strand bones and individual strand bones
                anchor_driver.expression = "abs(rot_anchor_var-1)"
                track_driver.expression = "rot_anchor_var"
                
                if scn_alt_root != None:
                    anchor_cnstr_driver.expression = "copy_alt_var if rot_anchor_var > 0 else 0"
            
                
        #-----------------------------------------------------------------------------
        # Operations run every strand
        
        # Per strand operation variables
        ik_target = obj.pose.bones["IK_hair_target_" + strand_num]
        fk_mch_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(b_num) + ".fk"]
        root_bone = obj.pose.bones["root_bone"]
        mch_def_ik_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(b_num) + ".ik.def"]
        l_str_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(b_num) + ".ik.stretch"]

        if tk_bone != None:
            l_tk_bone = obj.pose.bones["Tweak-hair_bone_" + strand_num + "." + str(b_num+1)]
            ik_mch_bone = "MCH-hair_bone_" + strand_num + "." + str(b_num+1) + ".ik.snap"
        

        #-----------------------------------------------------------------------------
        # Add FK_2_Ik custom property to every top DEF bone
        
        # The following is put at top to avoid reference before assignment
        # Add custom property to DEF bones or FK bones for Master bone strands
        if def_bone != None:
            b_top_def = obj.pose.bones["DEF-hair_bone_" + strand_num + ".1"]

            add_custom_variable(b_top_def, "FK_2_IK", "IK Influence", 1, 0, 1)
            b_top_def["FK_2_IK"] = 0.0
        else:
            b_top_fk = obj.pose.bones["CTRL-hair_bone_" + strand_num + ".1.fk"]

            add_custom_variable(b_top_fk, "FK_2_IK", "IK Influence", 1, 0, 1)
            b_top_fk["FK_2_IK"] = 0.0
        
        #-----------------------------------------------------------------------------
        # Add IK constraint to last MCH IK bone and copy transforms constraint to master bone target
        
        # Remove ik target constraints before adding new ones
        remove_constraints(ik_target)
        
        # Set IK constraint target and subtarget
        l_ik_bone = "MCH-hair_bone_" + strand_num + "." + str(b_num) + ".ik"
        cnstr_bone = obj.pose.bones[l_ik_bone]

        create_ik_constraint(cnstr_bone, obj, ik_target.name, b_num)
        
        #-----------------------------------------------------------------------------
        # Add IK constraint to last MCH IK stretch bone
        
        l_stretch_bone = "MCH-hair_bone_" + strand_num + "." + str(b_num) + ".ik.stretch"
        cnstr_bone = obj.pose.bones[l_stretch_bone]

        create_ik_constraint(cnstr_bone, obj, ik_target.name, b_num)
        
        #-----------------------------------------------------------------------------
        # Sets up IK target constraints and anchor property
        
        # Checks if there are alternate roots or roots selected                            
        scene = bpy.context.scene
        try:
            scn_arm = scene.objects[scene.ArmatureObject]
        except:
            scn_arm = None
               
        try:
            scn_root = scn_arm.pose.bones[scene.BoneRoot]
        except:
            scn_root = None
            
        try:
            scn_alt_root = scn_arm.pose.bones[scene.AltBoneRoot]
        except:
            scn_alt_root = None
        
        add_custom_variable(ik_target, "IK_Anchor", "Anchors to the selected bone if present", 1, 0, 1)
        ik_target["IK_Anchor"] = 0.0
                  
        add_custom_variable(ik_target, "Auto_Stretch", "Value for autostretching IK bones", 1, 0, 1)
        ik_target["Auto_Stretch"] = 1.0

        # Get master bone strands if there are any
        if len(m_b_strands) > 0 and b_group != None:
            for m_bone in m_b_strands:
                if b_group == m_bone.bone_group:
                    
                    index = [pos for pos, char in enumerate(m_bone.name) if char == "_"][2]
                    index2 = [pos for pos, char in enumerate(m_bone.name) if char == "."][0]
                    
                    m_strand_num = m_bone.name[index+1: index2]
                    
                    m_target = "IK_hair_target_" + m_strand_num
                    #mch_target = "IK_hair_target_" + strand_num + ".mch"
                    mch_m_target = "IK_hair_target_" + m_strand_num + ".mch"
                    
                    # Get FK master strand
                    #fk_m_target = "CTRL-hair_bone_" + m_strand_num + ".1.fk"

                    # Make Mch ik target constraints
                    if strand_num != m_strand_num:
                        pass
                    else:
  
                        # Make constraints for master mch ik targets
                        pose_mch_master = obj.pose.bones[mch_m_target]
                        m_target_bone = obj.pose.bones[m_target]
                    
                        # Child of constraint for the root bone
                        child_cnstr = create_child_of_constraint(pose_mch_master, obj, root_bone.name, "Copy Master IK Bone")
                        
                        # Set inverse on child of constraint
                        mat_final = obj.matrix_world @ root_bone.matrix
                        child_cnstr.inverse_matrix = mat_final.inverted()
                        
                        # Make child of constraint for alternative root and add drivers
                        if scn_alt_root != None:
                            # Child of constraint for the alternative root bone
                            child_cnstr = create_child_of_constraint(pose_mch_master, scn_arm, scn_alt_root.name, "Copy Alt Root Bone")
                            
                            # Set inverse on child of constraint
                            mat_final = scn_arm.matrix_world @ scn_alt_root.matrix
                            child_cnstr.inverse_matrix = mat_final.inverted()
                            
                            # Add drivers
                            ik_driver = create_constraint_influence_driver(pose_mch_master, "Copy Alt Root Bone")

                            data_path = 'pose.bones["'+ik_target.name+'"]["IK_Anchor"]'
                            create_driver_var(ik_driver, "SINGLE_PROP", "var", obj, data_path)
                            ik_driver.type = "SCRIPTED"
                            ik_driver.expression = "var" 
                            
                            
                        # Add copy location constraint to master bone IK target
                        create_copy_loc_constraint(pose_mch_master, obj, ik_target.name, "Copy IK Target Loc")

                        # Create driver for root_bone child of constraint
                        ik_driver = create_constraint_influence_driver(pose_mch_master, "Copy Master IK Bone")

                        data_path = 'pose.bones["'+ik_target.name+'"]["IK_Anchor"]'
                        create_driver_var(ik_driver, "SINGLE_PROP", "var", obj, data_path)
                        ik_driver.type = "SCRIPTED"
                        ik_driver.expression = "abs(var-1)"
        else:
            m_target = ""
            
        
        # Child strand ik targets copy master strand ik target if there are master bones
        if(ik_target.name != m_target and m_target != ""):
            #pose_mch_bone = obj.pose.bones[mch_target]
            pose_mch_master = obj.pose.bones[mch_m_target]
            
            child_cnstr = create_child_of_constraint(ik_target, obj, mch_m_target, "Copy Master MCH IK bone")
            
            # Set inverse on child of constraint
            mat_final = obj.matrix_world @ pose_mch_master.matrix
            child_cnstr.inverse_matrix = mat_final.inverted()
            
            # Add driver for ik target to turn on and off chain rot
            ik_driver = create_constraint_influence_driver(ik_target, "Copy Master MCH IK bone")

            data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "var", obj, data_path)
            ik_driver.type = "SCRIPTED"
            ik_driver.expression = "var"
            
            #-----------------------------------------------------------------------------------------
            # Add drivers to IK constraint
            ik_driver = create_constraint_influence_driver(l_str_bone, "IK")

            data_path = 'pose.bones["'+m_target+'"]["Auto_Stretch"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "m_auto_stretch", obj, data_path)
            
            data_path = 'pose.bones["'+ik_target.name+'"]["Auto_Stretch"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "auto_stretch", obj, data_path)
            
            data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)
            
            ik_driver.type = "SCRIPTED"
            ik_driver.expression = "m_auto_stretch if chain_rot_var > 0 else auto_stretch"
            
        else:
            #-----------------------------------------------------------------------------------------
            # Add drivers to IK constraint
            ik_driver = create_constraint_influence_driver(l_str_bone, "IK")

            data_path = 'pose.bones["'+ik_target.name+'"]["Auto_Stretch"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "auto_stretch", obj, data_path)

            ik_driver.type = "SCRIPTED"
            ik_driver.expression = "auto_stretch"
            
        #--------------------------------------------------------------------------------------------------------
        # Set up IK anchor and parent constraints
        cnstr_bone = obj.pose.bones[ik_target.name]

        child_cnstr = create_child_of_constraint(cnstr_bone, obj, root_bone.name, "Copy Root Bone")
    
        # Set inverse on child of constraint
        mat_final = obj.matrix_world @ root_bone.matrix
        child_cnstr.inverse_matrix = mat_final.inverted()
            
        # Drivers and variables for root bone child of constraint
        add_custom_variable(ik_target, "IK_Anchor", "Anchors to the selected bone if present", 1, 0, 1)
        ik_target["IK_Anchor"] = 0.0
        
        # Add driver for ik target to turn on and off anchor rot
        try:
            # Child strand IK targets have 1 more constraint than master IK strands
            if(ik_target.name != m_target and m_target != ""):
                ik_target.constraints["Copy Root Bone"].driver_remove('influence')
            else:
                ik_target.constraints["Copy Root Bone"].driver_remove('influence')
        except:
            pass
        
        if(ik_target.name != m_target and m_target != ""):
            fcurve = ik_target.constraints["Copy Root Bone"].driver_add('influence')
        else:
            fcurve = ik_target.constraints["Copy Root Bone"].driver_add('influence')
            
        # Create Variable for IK anchor
        ik_driver = fcurve.driver
        
        data_path = 'pose.bones["'+ik_target.name+'"]["IK_Anchor"]'
        create_driver_var(ik_driver, "SINGLE_PROP", "anchor_var", obj, data_path)

        # For only child strand bones
        if(ik_target.name != m_target and m_target != ""):
            # Create chain copy rot var
            data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)

            # Set IK driver expression
            ik_driver.type = "SCRIPTED"
            ik_driver.expression = "abs(anchor_var-1) if chain_rot_var == 0 else 0.0"
        else:
            ik_driver.type = "SCRIPTED"
            ik_driver.expression = "abs(anchor_var-1)"
        
        if scn_alt_root != None:  
            # Create constraints and drivers for parent bone
            child_cnstr2 = create_child_of_constraint(cnstr_bone, scn_arm, scn_alt_root.name, "Copy Root Parent")
            
            # Set inverse on child of constraint
            mat_final = obj.matrix_world @ scn_alt_root.matrix
            child_cnstr2.inverse_matrix = mat_final.inverted()
            
            # Add driver for ik target to turn on and off anchor rot
            try:
                if(ik_target.name != m_target and m_target != ""):
                    ik_target.constraints["Copy Root Parent"].driver_remove('influence')
                else:
                    ik_target.constraints["Copy Root Parent"].driver_remove('influence')
            except:
                pass
            
            if(ik_target.name != m_target and m_target != ""):
                fcurve = ik_target.constraints["Copy Root Parent"].driver_add('influence')
            else:
                fcurve = ik_target.constraints["Copy Root Parent"].driver_add('influence')
            
            # Create Variable for IK anchor
            ik_driver = fcurve.driver

            data_path = 'pose.bones["'+ik_target.name+'"]["IK_Anchor"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "anchor_var", obj, data_path)
            
            if(ik_target.name != m_target and m_target != ""):
                # Create chain copy rot var
                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)
                
                ik_driver.type = "SCRIPTED"
                ik_driver.expression = "anchor_var if chain_rot_var == 0 else 0.0"
            else:
                ik_driver.type = "SCRIPTED"
                ik_driver.expression = "anchor_var"
                
        #-----------------------------------------------------------------------------
        # Set Root bone constraints for selected armature bone
        if len( root_bone.constraints) == 0 and scn_root != None:
            create_copy_transform_constraint(root_bone, "Copy Transforms", scn_arm, scn_root.name)
        
        #-----------------------------------------------------------------------------
        # Add copy rotation of ik target for the top MCH IK bone
        
        t_mch_ik_bone = obj.pose.bones["MCH-hair_bone_" + strand_num + ".1"+ ".ik"]
        
        # Remove any pre-existing constraints
        remove_constraints(t_mch_ik_bone)
        
        # Copy rotation for ik target
        create_copy_rot_constraint(t_mch_ik_bone, obj, ik_target.name, "BEFORE", "LOCAL", "LOCAL")
        
        if(ik_target.name != m_target and m_target != ""):
            # Copy rotation of master IK target
            create_copy_rot_constraint(t_mch_ik_bone, obj, m_target, "AFTER", "LOCAL", "LOCAL")
        
        #-----------------------------------------------------------------------------
        # Add copy transform constraint for the last tweak bone
        
        if tk_bone != None:
            m_strand_num = ""
            
            # Get master strand if any
            if len(m_b_strands) > 0:
                for m_bone in m_b_strands:
                    if b_group == m_bone.bone_group:
                        m_b_num = (len(m_bone.parent_recursive))+1
                        
                        index = [pos for pos, char in enumerate(m_bone.name) if char == "_"][2]
                        index2 = [pos for pos, char in enumerate(m_bone.name) if char == "."][0]
                        
                        m_strand_num = m_bone.name[index+1: index2]
                        break
            
            # Remove constraints before adding new ones
            remove_constraints(l_tk_bone)
        
            # Copy transforms of ik mch bone
            tk_bone = obj.pose.bones["Tweak-hair_bone_" + strand_num + "." + str(b_num+1)]
            
            create_copy_transform_constraint(tk_bone, "Copy IK", obj, ik_mch_bone, "AFTER",
                 "LOCAL_WITH_PARENT", "LOCAL_WITH_PARENT")
            
            # Add drivers to constraint of tweak bones to control fk2ik tweak bones
            ik_driver = create_constraint_influence_driver(tk_bone, "Copy IK")

            data_path = 'pose.bones["DEF-hair_bone_' + strand_num + '.1"]["FK_2_IK"]'
            create_driver_var(ik_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)
            
            if (m_strand_num != strand_num and m_strand_num != ""):
                data_path = 'pose.bones["CTRL-hair_bone_' + m_strand_num + '.1.fk"]["FK_2_IK"]'
                create_driver_var(ik_driver, "SINGLE_PROP", "m_var", obj, data_path)
            
                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(ik_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)
                
                ik_driver.type = "SCRIPTED"
                ik_driver.expression = "cust_prop_var if chain_rot_var == 0 else m_var"
            else:
                ik_driver.type = "AVERAGE"
            
            mch_bone_fk = obj.pose.bones["MCH-hair_bone_" + strand_num + "." + str(b_num) + ".fk"]
            
            child_cnstr = create_child_of_constraint(tk_bone, obj, mch_bone_fk.name, "Copy FK")
            
            mat_final = obj.matrix_world @ mch_bone_fk.matrix
            child_cnstr.inverse_matrix = mat_final.inverted()
            
            # Add drivers to constraint of tweak bones to control fk2ik tweak bones
            fk_driver = create_constraint_influence_driver(tk_bone, "Copy FK")

            data_path = 'pose.bones["DEF-hair_bone_' + strand_num + '.1"]["FK_2_IK"]'
            create_driver_var(fk_driver, "SINGLE_PROP", "cust_prop_var", obj, data_path)

            fk_driver.type = "SCRIPTED"
            
            if (m_strand_num != strand_num and m_strand_num != ""):
                data_path = 'pose.bones["CTRL-hair_bone_' + m_strand_num + '.1.fk"]["FK_2_IK"]'
                create_driver_var(fk_driver, "SINGLE_PROP", "m_var", obj, data_path)
                
                data_path = 'pose.bones["CTRL-hair_bone_' + strand_num + '.1.fk"]["Chain_Copy_Rot"]'
                create_driver_var(fk_driver, "SINGLE_PROP", "chain_rot_var", obj, data_path)

                fk_driver.type = "SCRIPTED"
                fk_driver.expression = "abs(cust_prop_var-1) if chain_rot_var == 0 else abs(m_var-1)"
            else:
                fk_driver.expression = "abs(cust_prop_var-1)"
        