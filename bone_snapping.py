import bpy

from . import utils

import imp
imp.reload(utils)

from .utils import *

# ------------------------------------------------------------------------
#    Snapping Functions
# ------------------------------------------------------------------------

def FkToIkSnapping(obj,sel_bones):
    b_chain_arr = []
    sel_strand_nums = []
    t_strand_arr = []
    c = "_"
    d = "."
    b_strands = []
    m_strands = []
    
    # Get strand number for selected bones
    for bone in sel_bones:
        if("target" in bone.name and bone.name.startswith("IK")):
            # Creates a list with the positions of the variable c
            index = [pos for pos, char in enumerate(bone.name) if char == c][2]
            l_index = len(bone.name)
            
            # Gets the string between the index of the third "_" and the index above it (The strand number)
            strand_num = bone.name[index+1: l_index]
        else:
            # Does the same except if the bone has only 2 c variable (Every other bone besides the Ik target)
            index = [pos for pos, char in enumerate(bone.name) if char == c][1]
            
            # Get index of . to get all numbers between "_" and "."
            index2 = [pos for pos, char in enumerate(bone.name) if char == d][0]
            strand_num = bone.name[index+1: index2]
            
        sel_strand_nums.append(strand_num)                
    
    # Get bone strands
    for bone in obj.data.bones:
        if "_bot" in bone.name:
            
            # Check if master bone is selected, has extra "_"
            if(bone.name.startswith("m_")):
                index = [pos for pos, char in enumerate(bone.name) if char == c][2]
            else:
                index = [pos for pos, char in enumerate(bone.name) if char == c][1]
                
            index2 = [pos for pos, char in enumerate(bone.name) if char == d][0]
                
            t_strand_num = bone.name[index+1: index2]
            
            # Compare selected bone strand to strand in sel_strand_nums
            # Gets only strands with bones that are selected
            if t_strand_num in sel_strand_nums:
                parent_arr = bone.parent_recursive
   
                parent_arr.insert(0,bone)
                b_chain_arr.append(parent_arr)
                    
            # Get master bone strands
            if bone.name.startswith("m_"):
                m_parent_arr = bone.parent_recursive
                
                m_bone = obj.pose.bones[bone.name]
                b_strands.append(m_bone)
            
    # Get number of chains in the array
    chain_count = len(b_chain_arr)  
    
    # For loop for every operation done once per chain
    for x in range(0, chain_count):
        
        # Get number of bones in each chain
        b_num = len(b_chain_arr[x])
        for y in range(1, b_num+1):
            # Get ORG bone
            base_name = "ORG-hair_bone_" + sel_strand_nums[x] + "." + str(y)
            
            try:
                org_bone = obj.pose.bones[base_name]
            except:
                pass
            try:
                org_bone = obj.pose.bones[base_name + "_bot"]
            except:
                pass
            try:
                org_bone = obj.pose.bones["m_" + base_name + "_bot"]
            except:
                pass
            
            b_group = org_bone.bone_group
            
            # Get Ctrl Fk bone
            if len(b_strands) > 0:
                for m_bone in b_strands:
                    if b_group == m_bone.bone_group:
                        #m_b_num = (len(m_bone.parent_recursive))+1
                        m_b_num = (len(m_parent_arr))+1
                        
                        index = [pos for pos, char in enumerate(m_bone.name) if char == "_"][2]
                        index2 = [pos for pos, char in enumerate(m_bone.name) if char == "."][0]
                        
                        m_strand_num = m_bone.name[index+1 : index2]
                        m_target = "CTRL-hair_bone_" + m_strand_num + ".1.fk"
                        
                        # Select the last bone in the chain if there is no corresponding master bone
                        try:
                            m_target_bone = obj.pose.bones["CTRL-hair_bone_" + m_strand_num + "." + str(y) + ".fk"]
                        except:
                            m_target_bone = obj.pose.bones["CTRL-hair_bone_" + m_strand_num + "." + str(m_b_num) + ".fk"]
            else:
                m_target = ""
                
            try:
                if m_target == None:
                    m_target = ""
            except:
                m_target = ""
            
            # For loop for every operation done once per bone
            ik_bone =  obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".ik"]
            snap_bone = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".ik.snap"]
            fk_bone = obj.pose.bones["CTRL-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".fk"]
            top_fk_bone = obj.pose.bones["CTRL-hair_bone_" + sel_strand_nums[x] + ".1.fk"]
            
            if fk_bone.parent != None and y > 1:
                # Operations for bones without the suffix "_1"
                
                # Detect any bones that need to be offset
                b_mat = snap_bone.matrix @ parent_matrix(Matrix(), fk_bone, fk_bone["Copy_Rot"], 1, m_bool = True)

                try:
                    # Check if chain is parented to master chain
                    chain_rot = top_fk_bone["Chain_Copy_Rot"]
                except:
                    chain_rot = -1
                    
                try:
                    fk_anchor = fk_bone["Rot_Anchor"]
                except:
                    fk_anchor = -1
                    
               
                # Subtract matrix of master chain bones
                if chain_rot != -1 and fk_anchor != -1:
                    if chain_rot == 1:       
                        b_mat = snap_bone.matrix @ chain_parent_recursive(Matrix(), m_target_bone, 0, 1) 
                    else:
                        pass
                else:
                    b_mat = snap_bone.matrix @ parent_matrix(Matrix(), fk_bone, fk_bone["Copy_Rot"], 1, m_bool = True)

                mat = get_pose_matrix_in_other_space(b_mat, fk_bone)
                
            else:
                # May not need this part of the code anymore (no if statement)
                
                # Operations for bones with the suffix "_1"
                
                try:
                    # Check if chain is parented to master chain
                    chain_rot = top_fk_bone["Chain_Copy_Rot"]
                except:
                    chain_rot = -1
                    
                try:
                    fk_anchor = fk_bone["Rot_Anchor"]
                except:
                    fk_anchor = -1
                    
                if chain_rot != -1 and fk_anchor != -1:
                    # Check if chain is parented to master chain
                    if chain_rot == 1:
                        # If the bone strand is copying master strand transformations
                        
                        b_mat = snap_bone.matrix @ m_target_bone.matrix_basis.inverted()
                        
                        mat = get_pose_matrix_in_other_space(b_mat,fk_bone)
                    else:
                        # If the bone controls its own transformations
                        mat = get_pose_matrix_in_other_space(snap_bone.matrix, fk_bone)
                else:
                    # If the bone doesn't have a master strand
                    mat = get_pose_matrix_in_other_space(snap_bone.matrix, fk_bone)

            fk_bone.matrix = snap_bone.matrix
            
            q = mat.to_quaternion()
            
            fk_bone.rotation_quaternion = q
            
            # Update bone rotations
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            
    
def IkToFkSnapping(obj, sel_bones):
    b_chain_arr = []
    sel_strand_nums = []
    c = "_"
    d = "."
    b_strands = []
    
    # Get strand number for selected bones
    for bone in sel_bones:
        if("target" in bone.name and bone.name.startswith("IK")):
            # Creates a list with the positions of the variable c
            index = [pos for pos, char in enumerate(bone.name) if char == c][2]
            l_index = len(bone.name)
            
            # Gets the string between the index of the third "_" and the index above it (The strand number)
            strand_num = bone.name[index+1: l_index]
        else:
            # Does the same except if the bone has only 2 c variable (Every other bone besides the Ik target)
            index = [pos for pos, char in enumerate(bone.name) if char == c][1]
            
            # Get index of . to get all numbers between "_" and "."
            index2 = [pos for pos, char in enumerate(bone.name) if char == d][0]
            strand_num = bone.name[index+1: index2]
            
        sel_strand_nums.append(strand_num)
    
    # Get bone strands
    for bone in obj.data.bones:
        if "_bot" in bone.name:
            # Check if master bone is selected, has extra "_"
            if(bone.name.startswith("m_")):
                index = [pos for pos, char in enumerate(bone.name) if char == c][2]
            else:
                index = [pos for pos, char in enumerate(bone.name) if char == c][1]
                
            index2 = [pos for pos, char in enumerate(bone.name) if char == d][0]
                
            t_strand_num = bone.name[index+1: index2]

            # Compare selected bone strand to strand in sel_strand_nums
            # Gets only strands with bones that are selected
            if t_strand_num in sel_strand_nums:
                parent_arr = bone.parent_recursive
                parent_arr.insert(0,bone)
                b_chain_arr.append(parent_arr)
                
            
            # Get master bone strands
            if bone.name.startswith("m_"):
                m_parent_arr = bone.parent_recursive
                m_bone = obj.pose.bones[bone.name]
                b_strands.append(m_bone)
                
            
    # Get number of chains in the array
    chain_count = len(b_chain_arr)  
    
    # For loop for every operation done once per chain
    for x in range(0, chain_count):
        
        # Get number of bones in each chain
        b_num = len(b_chain_arr[x])
        for y in range(1, b_num+1):
            # Get ORG bones 
            # Last bone in chain names
            base_name = "ORG-hair_bone_" + sel_strand_nums[x] + "." + str(y)
            
            try:
                org_bone = obj.pose.bones[base_name]
            except:
                pass
            try:
                org_bone = obj.pose.bones[base_name + "_bot"]
            except:
                pass
            try:
                org_bone = obj.pose.bones["m_" + base_name + "_bot"]
            except:
                pass
            
            b_group = org_bone.bone_group
            
            # Get Ctrl Fk bone
            if len(b_strands) > 0:
                for m_bone in b_strands:
                    if b_group == m_bone.bone_group:
                        m_b_num = (len(m_bone.parent_recursive))+1
                        
                        index = [pos for pos, char in enumerate(m_bone.name) if char == c][2]
                        index2 = [pos for pos, char in enumerate(m_bone.name) if char == d][0]
                        
                        m_strand_num = m_bone.name[index +1: index2]
                        m_target = "MCH-hair_bone_" + m_strand_num + ".1.ik"
                        m_ik_target = "IK_hair_target_" + m_strand_num
                        mch_m_ik_target = obj.pose.bones["IK_hair_target_" + m_strand_num + ".mch"]
                        
                        try:
                            m_mch_fk_bone = obj.pose.bones["MCH-hair_bone_" + m_strand_num + "." + str(b_num) + ".fk"]
                        except:
                            m_mch_fk_bone = obj.pose.bones["MCH-hair_bone_" + m_strand_num + "." + str(m_b_num) + ".fk"]
                        
                        try:
                            m_target_bone = obj.pose.bones["MCH-hair_bone_" + m_strand_num + "." + str(y) + ".ik"]
                        except:
                            m_target_bone = obj.pose.bones["MCH-hair_bone_" + m_strand_num + "." + str(m_b_num) + ".ik"]
            else:
                m_target = ""
            
            try:
                if m_target == None:
                    m_target = ""
            except:
                m_target = ""
                
            # For loop for every operation done once per bone
            snap_bone = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".ik.snap"]
            ik_target =  obj.pose.bones["IK_hair_target_" + sel_strand_nums[x]]
            fk_bone = obj.pose.bones["CTRL-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".fk"]
            top_ik_bone = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + ".1.ik"]
            top_fk_bone = obj.pose.bones["CTRL-hair_bone_" + sel_strand_nums[x] + ".1.fk"]
            bot_fk_bone = obj.pose.bones["CTRL-hair_bone_" + sel_strand_nums[x] + "." + str(b_num) + ".fk"]
            ik_bone =  obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(y) + ".ik"]
            
            mch_fk_bone = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(b_num) + ".fk"]

            # Get world coords for fk_matrix
            fk_tail_loc = obj.location + bot_fk_bone.tail
            mw = Matrix() @ ik_target.bone.matrix_local
            mw.translation = fk_tail_loc
            
            # Test if strand is master strand or if strand isn't connected to one
            try:
                chain_cp_rot = top_fk_bone["Chain_Copy_Rot"]
            except:
                chain_cp_rot = -1
                
            if chain_cp_rot > 0:
                try:
                    ik_anchor = m_ik_target["IK_Anchor"]
                except:
                    ik_anchor = -1
            else:
                try:
                    ik_anchor = ik_target["IK_Anchor"]
                except:
                    ik_anchor = -1
                
            # Offset ik target matrix by master bone matrix to correctly snap to fk bone
            if m_target != "":
                if chain_cp_rot > 0:
                    m_ik_target = obj.pose.bones["IK_hair_target_" + m_strand_num]
                    mw = mw @ m_ik_target.matrix_basis.inverted()
            
            # Convert world matrix to pose matrix
            mp = obj.convert_space(pose_bone=ik_target, 
                matrix=mw, 
                from_space='WORLD', 
                to_space='POSE')

            try:
                root_bone = obj.pose.bones["root_bone"]
            except:
                root_bone = None
                
                
            if root_bone != None:
                # Uses the alternate root bone matrix if alt root is present
                try:
                    root_target = ik_target.constraints["Copy Root Parent"].target
                except:
                    root_target = None
                    
                if root_target != None:
                    # Get the alternative root matrix
                    if ik_anchor > 0:
                        alt_root_bone = ik_target.constraints["Copy Root Parent"].subtarget
                        root_bone = root_target.pose.bones[alt_root_bone]
                        
                    if m_target != "" and chain_cp_rot > 0:
                        # Get master mch ik target transform matrix
                        mch_ik_mat = mch_m_ik_target.bone.matrix_local @ mch_m_ik_target.matrix.inverted()

                        # Get the location transform matrix of he master ik target
                        mat2 = m_ik_target.matrix_basis.inverted().copy()
                        mat2.translation = (0,0,0)
                        
                        # This matrix takes into account the master bone transformations
                        #baseMat = mch_ik_mat @ mch_fk_bone.matrix @ mat2 @ m_ik_target.matrix_basis
                        baseMat = mch_ik_mat @ mch_fk_bone.matrix @ m_ik_target.matrix_basis 
                    else:
                        root_mat = (root_bone.bone.matrix_local @ root_bone.matrix.inverted()) 
                        baseMat = root_mat @ mch_fk_bone.matrix
                else:
                    # Don't subtract any matrix if there's only one constraint
                    if ik_anchor > 0:
                        baseMat = mch_fk_bone.matrix 
                    else:
                        root_mat = (root_bone.bone.matrix_local @ root_bone.matrix.inverted()) 
                        baseMat = root_mat @ mch_fk_bone.matrix 
            else:
                baseMat = mch_fk_bone.matrix 
            
            #baseMat = mch_fk_bone.matrix 
            
            
            if m_target != "":
                if chain_cp_rot > 0:
                    baseMat = baseMat @ m_ik_target.matrix_basis.inverted()
                    
            ik_target.matrix = baseMat 
            
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            
            # Set tweak bones
            fk_head_loc = obj.location + fk_bone.head
            mw = Matrix()
            mw.translation = fk_head_loc
            mp = obj.convert_space(pose_bone=snap_bone, 
                matrix=mw, 
                from_space='WORLD', 
                to_space='POSE')
            
            # Snap snap bones to fk bones
            mat = fk_bone.matrix
            
            if y == b_num:
                bot_snap_bone = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(b_num+1) + ".ik.snap"]
                bot_mch_fk = obj.pose.bones["MCH-hair_bone_" + sel_strand_nums[x] + "." + str(b_num) + ".fk"]
                mat2 = bot_mch_fk.matrix
                bot_snap_bone.matrix = mat2
                
            snap_bone.matrix = mat
            
            # Update bone rotations
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')