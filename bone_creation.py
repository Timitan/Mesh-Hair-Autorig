import bpy

from . import utils

import imp
imp.reload(utils)

from .utils import *

def CreateBones(obj, sel_bones):
    b_chain_arr = []
    m_strand_arr = []
    m_strand_num_arr = []
    for bone in obj.data.bones:
        f_layer = bone.layers[0]
        
        if bone.parent == None and f_layer == True:
            child_arr = bone.children_recursive
            l_bone = child_arr[len(child_arr)-1]
            
            if not(("_bot") in l_bone.name): 
                if l_bone.name.endswith(".L") or l_bone.name.endswith(".R"):
                    index = len(l_bone.name) - 2
                    l_bone.name = l_bone.name[0:index] + "_bot" + l_bone.name[index:len(l_bone.name)]
                else:
                    l_bone.name = l_bone.name + "_bot"
            
    # Update bone names
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create array filled with arrays of bone chains
    for bone in obj.data.bones:
        if "_bot" in bone.name:
            parent_arr = bone.parent_recursive
            parent_arr.insert(0,bone)
            b_chain_arr.append(parent_arr)
            
            # Append strand number from master bone to an array
            if bone.name.startswith("m_"):

                m_strand_arr.append(parent_arr)
    
    # Get number of chains in the array
    chain_count = len(b_chain_arr)  

    # Retrieve Armature object inputted when script is run if there is any
    scene = bpy.context.scene
    
    try:
        scn_arm = scene.objects[scene.ArmatureObject]
        #scn_edit_bone = scn_arm.data.edit_bones[scene.BoneParentObject]
    except:
        scn_arm = None
    
    try:
        scn_root = scn_arm.pose.bones[scene.BoneRoot]
    except:
        scn_root = None
    
    # Move root bone to the targeted bone in another armature if there is any
    if scn_root != None:
        head = (scn_root.head[0],scn_root.head[1],scn_root.head[2])
        tail = (scn_root.tail[0],scn_root.tail[1],scn_root.tail[2])
        root_bone = create_bone(obj, "root_bone", head, tail, True, True)
    else:
        head = (obj.location[0],obj.location[1],obj.location[2])
        tail = (obj.location[0],obj.location[1],obj.location[2] -0.125)
        root_bone = create_bone(obj, "root_bone", head, tail, True, True)
        
    head = (root_bone.head[0],root_bone.head[1],root_bone.head[2])
    tail = (root_bone.tail[0],root_bone.tail[1],root_bone.tail[2])
    root_track_bone = create_bone(obj, "root_track_bone", head, tail)

    # Parent to root bone
    root_track_bone.parent = root_bone
    root_track_bone.use_inherit_rotation = False
    
    # Create trackTo bone 
    head = (root_bone.head[0],root_bone.head[1],root_bone.head[2])
    tail = (root_bone.head[0] - (root_bone.length),root_bone.head[1],root_bone.head[2])
    trackTo_bone = create_bone(obj, "root_track_bone.track", head, tail)

    # Parent to root bone
    trackTo_bone.parent = root_bone
    trackTo_bone.use_inherit_rotation = False
    
    # For loop for every operation done once per chain
    for x in range(0, chain_count):
        
        # Get number of bones in each chain
        b_num = len(b_chain_arr[x])
        
        # For loop for every operation done once per bone
        for y in range(0, b_num):
            # Rename ORG bone
            org_bone = obj.data.edit_bones[b_chain_arr[x][y].name]
            org_bone.use_deform = False
            
            if "_bot" in org_bone.name: #(org_bone.name.endswith("Top")):
                if(org_bone.name.startswith("m_")):
                    org_bone.name = "m_ORG-hair_bone_" + str(x) + "." + str(b_num - y) + "_bot" 
                else: 
                    org_bone.name = "ORG-hair_bone_" + str(x) + "." + str(b_num - y) + "_bot"
                        
            else:
                org_bone.name = "ORG-hair_bone_" + str(x) + "." + str(b_num - y)
                
            b_chain_arr[x][y] = org_bone
            
            # Create all DEF bones
            if b_chain_arr[x] in m_strand_arr:
                def_bone = None
            else:
                head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
                tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
                name = "DEF-hair_bone_" + str(x) + "." + str(b_num - y)
                def_bone = create_bone(obj, name, head, tail, True, True)
            
            if b_chain_arr[x] in m_strand_arr:
                ik_bone = None
                fk_bone = None
            else:
                # Create all IK Bones
                head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
                tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
                name = "IK-hair_bone_" + str(x) + "." + str(b_num - y)
                ik_bone = create_bone(obj, name, head, tail)
                
                # Create all FK Bones
                head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
                tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
                name = "FK-hair_bone_" + str(x) + "." + str(b_num - y)
                fk_bone = create_bone(obj, name, head, tail)
                fk_bone.roll = org_bone.roll
            
            # Create all tweak Bones
            if b_chain_arr[x] in m_strand_arr:
                tk_bone = None
            else:
                head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
                tail = (org_bone.center[0], org_bone.center[1], org_bone.center[2])
                name = "Tweak-hair_bone_" + str(x) + "." + str(b_num - y)
                tk_bone = create_bone(obj, name, head, tail)

            # Create all CTRL FK bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            name = "CTRL-hair_bone_" + str(x) + "." + str(b_num - y) + ".fk"
            ctrl_bone = create_bone(obj, name, head, tail)
            
            # Create MCH Anchor fk bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.head[0], org_bone.head[1], org_bone.tail[2])
            name = "MCH-hair_bone_" + str(x) + "." + str(b_num - y) + ".fk.anchor"
            fk_anc_bone = create_bone(obj, name, head, tail, False)
            fk_anc_bone.length = org_bone.length/2
            
            # Create all MCH IK bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            name = "MCH-hair_bone_" + str(x) + "." + str(b_num - y) + ".ik"
            mch_bone = create_bone(obj, name, head, tail, True, False, "FIX_SHEAR")
            
            # Create all MCH ik snap bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            name = "MCH-hair_bone_" + str(x) + "." + str(b_num - y) + ".ik.snap"
            snap_bone = create_bone(obj, name, head, tail, True, False, "NONE")
            
            # Create all MCH ik stretch bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            name = "MCH-hair_bone_" + str(x) + "." + str(b_num - y) + ".ik.stretch"
            stretch_bone = create_bone(obj, name, head, tail, True, False, "FIX_SHEAR")
            
            # Create all MCH ik def bones
            head = (org_bone.head[0], org_bone.head[1], org_bone.head[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            name = "MCH-hair_bone_" + str(x) + "." + str(b_num - y) + ".ik.def"
            stretch_bone = create_bone(obj, name, head, tail)
        
        #Parenting bones together
        for a in range(1, b_num+1):
            # Select the correct bone if it has a "_bot" in it or if it has a suffix attached
            base_name = "ORG-hair_bone_" + str(x) + "." + str(a)
            
            for bone in obj.data.edit_bones:
                if "ORG-hair_bone_" + str(x) + "." + str(a) in bone.name:
                    org_bone = obj.data.edit_bones[bone.name]
            
            # Parent bones to make a chain
            if org_bone.parent != None:
                if fk_bone != None:
                    # Parent FK bones to each other
                    child_bone = obj.data.edit_bones["FK-hair_bone_" + str(x) + "." + str(a)]
                    parent_bone = obj.data.edit_bones["FK-hair_bone_" + str(x) + "." + str(a - 1)]
                    parent_child_to_parent(child_bone, parent_bone, True)
                
                if def_bone != None:
                    child_bone = obj.data.edit_bones["DEF-hair_bone_" + str(x) + "." + str(a)]
                    parent_bone = obj.data.edit_bones["DEF-hair_bone_" + str(x) + "." + str(a - 1)]
                    parent_child_to_parent(child_bone, parent_bone, True)
                    
                if ik_bone != None:
                    # Parent IK bones to MCH ik bones, MCH IK bones will have the IK constraint, IK bones will copy it
                    child_bone = obj.data.edit_bones["IK-hair_bone_" + str(x) + "." + str(a)]
                    parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik"]
                    parent_child_to_parent(child_bone, parent_bone)

                # Parent MCH bones to each other
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik"]
                parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a - 1) + ".ik"]
                parent_child_to_parent(child_bone, parent_bone, True)
                    
                # Parent CTRL_FK bones to fk snap bones
                child_bone = obj.data.edit_bones["CTRL-hair_bone_" + str(x) + "." + str(a) + ".fk"]
                parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".fk.anchor"]
                parent_child_to_parent(child_bone, parent_bone)
                
                # Parent fk snap bones to the CTRL_fk bone one bone up
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".fk.anchor"]
                parent_bone = obj.data.edit_bones["CTRL-hair_bone_" + str(x) + "." + str(a - 1) + ".fk"]
                parent_child_to_parent(child_bone, parent_bone)
                
                # Parent ik stretch bones
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.stretch"]
                parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a - 1) + ".ik.stretch"]
                parent_child_to_parent(child_bone, parent_bone)
                
                # Parent ik def bones
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.def"]
                parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a - 1) + ".ik.def"]
                parent_child_to_parent(child_bone, parent_bone)
            else:
                # Parent top bones to root
                
                # Parent top of ik chain to root
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + ".1.ik"]
                parent_child_to_parent(child_bone, root_bone)
                
                # Parent top of stretch bones to root
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.stretch"]
                parent_child_to_parent(child_bone, root_bone)
                
                # Parent top of stretch bones to root
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.def"]
                parent_child_to_parent(child_bone, root_bone)
                
                # Parent top of ctrl fk bones to anchor bone
                child_bone = obj.data.edit_bones["CTRL-hair_bone_" + str(x) + ".1.fk"]
                parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + ".1.fk.anchor"]
                parent_child_to_parent(child_bone, parent_bone)
                
                # Parent fk anchor bones to root
                child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + ".1.fk.anchor"]
                parent_child_to_parent(child_bone, root_bone)  
                
            # Parent snap bones to mch ik
            child_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.snap"]
            parent_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(a) + ".ik.def"]
            parent_child_to_parent(child_bone, parent_bone)
           
                
        # Operations run each strand
        try:
            m_org_bone = obj.data.edit_bones["ORG-hair_bone_" + str(x) + "." + str(b_num) + "_bot"]
        except:
            try:
                m_org_bone = obj.data.edit_bones["ORG-hair_bone_" + str(x) + "." + str(b_num) + "_bot"]
            except:
                m_org_bone = obj.data.edit_bones["m_ORG-hair_bone_" + str(x) + "." + str(b_num) + "_bot"]
    
        l_bone = obj.data.edit_bones[b_chain_arr[x][0].name]
        t_bone = obj.data.edit_bones[b_chain_arr[x][b_num-1].name]
             
        x_offset = ((l_bone.head[0] - l_bone.tail[0]))
        y_offset = ((l_bone.head[1] - l_bone.tail[1]))
        z_offset = ((l_bone.head[2] - l_bone.tail[2]))

        # Create a bone for the last tweak bone to be parented to
        head = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
        tail = (org_bone.tail[0] - x_offset, org_bone.tail[1] - y_offset, org_bone.tail[2]- z_offset)
        name = "MCH-hair_bone_" + str(x) + "." + str(b_num) + ".fk"
        fk_mch_bone = create_bone(obj, name, head, tail)
        
        parent_bone = obj.data.edit_bones["CTRL-hair_bone_" + str(x) + "." + str(b_num) + ".fk"]
        parent_child_to_parent(fk_mch_bone, parent_bone)
        
        # Setting up IK bones
        head = (l_bone.tail[0], l_bone.tail[1], l_bone.tail[2])
        tail = ((l_bone.tail[0] - x_offset), (l_bone.tail[1]- y_offset), (l_bone.tail[2]- z_offset)) #- 0.075
        name = "IK_hair_target_" + str(x)
        ik_target = create_bone(obj, name, head, tail)

        ik_target.length = l_bone.length/2
        ik_target.roll = l_bone.roll

        l_bone_pose = obj.pose.bones[l_bone.name]
        b_group = l_bone_pose.bone_group
        
        if b_group != None:          
            if(m_org_bone.name.startswith("m_")):
                head = (l_bone.tail[0], l_bone.tail[1], l_bone.tail[2])
                tail = ((l_bone.tail[0] - x_offset), (l_bone.tail[1]- y_offset), (l_bone.tail[2]- z_offset))
                name = "IK_hair_target_" + str(x) + ".mch"
                mch_ik_tar = create_bone(obj, name, head, tail)

                mch_ik_tar.length = l_bone.length/2
                mch_ik_tar.roll = l_bone.roll

        # Create extra snap bone
        head = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
        tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2] - (org_bone.length/2))
        name = "MCH-hair_bone_" + str(x) + "." + str(b_num + 1) + ".ik.snap"
        snap_bone = create_bone(obj, name, head, tail)
        
        l_def_ik_bone = obj.data.edit_bones["MCH-hair_bone_" + str(x) + "." + str(b_num) + ".ik.def"]
        
        parent_child_to_parent(snap_bone, l_def_ik_bone)
              
        if tk_bone != None:
            # Create extra tweak bone for end of strand
            head = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2])
            tail = (org_bone.tail[0], org_bone.tail[1], org_bone.tail[2] - (org_bone.length/2))
            name = "Tweak-hair_bone_" + str(x) + "." + str(b_num + 1)
            tk_bone = create_bone(obj, name, head, tail)
