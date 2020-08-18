# Mesh Hair Autorig
> A Blender addon for rigging mesh-based strands of hair.

## Table of contents
* [General info](#general-info)
* [Features](#features)
* [Usage](#usage)
* [Setup](#setup)
* [Notes](#notes)

## General Info
Mesh Hair Autorig is a Blender addon for rigging mesh-based strands of hair. All it needs is a chain of bones and it will create FK, IK and Tweak bones off of it.

This addon could also be used for rigging ropes but its features are mostly tailored for rigging hair.  

## Features
List of features:
- Creates FK, IK, Tweak, Snap, Root Bones
- Creates custom bone properties
- FK/ IK snap functions
- Utility functions for managing, keyframing and hiding bones
- Custom bone objects organized into collections
- Master and child chains

## Usage

### Snap and root bones
In addition to the FK, IK and Tweak bones, there are snap bones and a root bone.
* Snap Bones
  - Used to correct bone positions when snapping from IK to FK
  - Needed due to multiple FK control bones and only 1 IK controller bone
  - Tweak bones copy snap bones when IK bones are used
  
* Root Bone
  - Created at the armature's origin point
  - If there is a Root parent specified, the bone will be created at that bone's location instead
 
### Master and Child chains
There are also master and child bone chains where the child bone chains will copy the transforms of the master bone chain. This is used to simplify the animation of multiple bone chains with one bone chain. This property of child strands can be toggled on and off.

### Root parents
Root parents and alternative root parents can be specified when creating the bones and constraints of the armature. This is if the hair rig needs to be parented to another bone in another object. If specified, the root bone of the rig will align itself with the root parent. These bones are optional and do not need to be specified when creating bones.
* Root parent
  - The root bone of the armature will copy transforms of this bone in another armature object
  
* Alt root parent
  - Used in specific cases where bones will copy this bone's transforms instead of the root parent's transforms (if the FK anchor and FK Copy Alt properties are 1.0)

### Properties
Bones will have properties that can be viewed under the Hair Autorig panel in the Properties panel. Depending on the bone that's selected, different properties will be displayed.
* FK to IK
  - Used to specify which type of bone would be used to deform the mesh
  - Value of 0 will indicate that FK bones will be used
  
* FK Copy Rot
  - Controls if the selected bone will double its rotations from its parent
  
* Chain Rot
  - Controls the influence of master bone chains on child bone chains

* FK/ IK Anchor
  - Controls the influence of the parent's transforms of the selected bone and bones down the chain

* FK Alt root
  - Controls the influence of the alternative root parent bone
  - Only works if the FK Anchor property is 1.0

* IK auto stretch
  - Auto stretch property for IK bones
  
### Utilities

Within the Hair Autorig main panel, there are utilities for managing bones
* Toggle Value
  - Toggles the specified property from 0 to 1 for selected bones
  - Tick on "Set property value" to set the property's value to a specific value
* Keyframe property
  - Keyframe the specified property for all selected bones on the current keyframe
* Isolate bones
  - Hides all other bones that are not part of the selected chain of bones
  - Will exclude hiding master or child chains if they are used

## Setup

### For general usage:
1. Create an armature object with chain of bones connected and parented to each other
2. Go into Edit mode and under The Hair Autorig Main panel in the properties panel, click "Create Bones"
3. Go into Pose Mode and click "Create Constraints"

### With Master and Child bone chains:
1. Create two bone chains
2. At the last bone of one of the chains, prepend a "m_" to its name to label it as a master chain
3. Put both bone chains into a bone group
4. Create bones and create constraints

### With Root parents and Alternative Root parents:
1. Under the "Create bones and constraints" panel, there is an armature object you can specify
2. After specifying an armature object, you must specify a root parent bone
3. (OPTIONAL) After specifying a root parent bone, you can specify an alternative root parent bone

## Notes

This addon has a few notes regarding its usage.
* Bones must only have a single child bone
* There can only be one master chain within a bone group
* When snapping FK to IK or from IK to FK with master and child strands, the master strand must be snapped first, then child strands
* The transforms of snap bones needs to be reset when using snapping functions

