# ------------------------------------------------------------------------
#    Strand Related Functions
# ------------------------------------------------------------------------

def ClearNamesButton(obj, sel_bones):
    # Operations for resetting names of selected bones and constraints
    for bone in sel_bones:
        IK_bone = obj.pose.bones[bone.name]
        if(len(IK_bone.constraints) > 0):
            IK_cnstr = IK_bone.constraints[0]
            
            IK_cnstr.mute = True
            IK_cnstr.mute = False

        # Clear names for bones to avoid errors
        if("hair_bone" in bone.name or "_bot" in bone.name or ".L" in bone.name or ".R" in bone.name):
            bone.name = "bone"

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