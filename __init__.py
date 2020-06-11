'''
Copyright (C) 2020 TIMOTHY TAN
tim.tan5145@gmail.com

Created by TIMOTHY TAN

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name" : "Mesh Hair Strand AutoRig",
    "author" : "Timothy Tan",
    "version" : (1, 2, 7),
    "blender" : (2, 83, 0),
    "location" : "View3D > Properties > Mesh Hair Strand AutoRig",
    "description" : "Automatically rig mesh-based hair with a skeleton",
    "category" : "Armature"
}

import bpy

if 'ui' in locals():
    import importlib

    importlib.reload(ui)
else:
    from . import ui

def register():
    ui.register()

def unregister():
    ui.unregister()

if __name__ == "__main__":
    register()


