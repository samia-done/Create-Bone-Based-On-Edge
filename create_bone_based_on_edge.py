# Copyright (c) 2019 Samia
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh
import copy
import math
from bpy.types import Operator, AddonPreferences
from bpy.props import *

bl_info = {
    "name": "Create Bone Based On Edge",
    "author": "Samia",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "3D View > Mesh Editor Mode > Ctrl + E",
    "description": "Creates a bone based on the selected edge.",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"
}


class Edge2BonePreferences(AddonPreferences):

    bl_idname = __name__

    bone_name = bpy.props.StringProperty(
        name="BoneName",
        description="Bone name",
        default="Bone"
    )

    bone_name_junction = bpy.props.StringProperty(
        name="BoneNameSeparator",
        description="Bone name separator",
        default="."
    )

    bone_name_suffix = bpy.props.StringProperty(
        name="BoneNameSuffix",
        description="Bone name suffix",
        default=""
    )

    zero_padding = IntProperty(
        name="Zeropadding",
        description="Number of digits of bone name zero padding",
        default=3,
        min=0,
        max=6
    )

    is_reverse = bpy.props.BoolProperty(
        name="Reverse",
        description="Change the bone order to the reverse order",
        default=False
    )

    is_parent = bpy.props.BoolProperty(
        name="Parent",
        description="Set parent bone",
        default=True
    )

    use_connect = bpy.props.BoolProperty(
        name="Connected",
        description="When Bone has a parent,bone's head is stuck tp the parent's tail",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Create Bone Settings")
        layout.prop(self, "bone_name")
        layout.prop(self, "bone_name_junction")
        layout.prop(self, "bone_name_suffix")
        layout.prop(self, "zero_padding")
        layout.prop(self, "is_reverse")
        layout.prop(self, "is_parent")
        layout.prop(self, "use_connect")


class Edge2BoneSettingsOperator(bpy.types.Operator):

    bl_idname = "object.edge_to_borne_settings"
    bl_label = "Create Bone Settings"
    bl_description = "Display the bone setting dialog"
    bl_options = {'REGISTER', 'UNDO'}

    bone_name = bpy.props.StringProperty(
        name="BoneName",
        description="Bone name",
        default="Bone"
    )

    bone_name_junction = bpy.props.StringProperty(
        name="BoneNameSeparator",
        description="Bone name separator",
        default="."
    )

    bone_name_suffix = bpy.props.StringProperty(
        name="BoneNameSuffix",
        description="Bone name suffix",
        default=""
    )

    zero_padding = IntProperty(
        name="Zeropadding",
        description="Number of digits of bone name zero padding",
        default=3,
        min=0,
        max=6
    )

    is_reverse = bpy.props.BoolProperty(
        name="Reverse",
        description="Change the bone order to the reverse order",
        default=False
    )

    is_parent = bpy.props.BoolProperty(
        name="Parent",
        description="Set parent bone",
        default=True
    )

    use_connect = bpy.props.BoolProperty(
        name="Connected",
        description="When Bone has a parent,bone's head is stuck tp the parent's tail",
        default=True
    )

    @staticmethod
    def set_user_pref(self):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        addon_prefs.bone_name = copy.copy(self.bone_name)
        addon_prefs.bone_name_suffix = copy.copy(self.bone_name_suffix)
        addon_prefs.bone_name_junction = copy.copy(self.bone_name_junction)
        addon_prefs.zero_padding = int(copy.copy(self.zero_padding))

        addon_prefs.is_reverse = copy.copy(self.is_reverse)
        addon_prefs.is_parent = copy.copy(self.is_parent)
        addon_prefs.use_connect = copy.copy(self.use_connect)

    @staticmethod
    def get_user_pref(self):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        self.bone_name = copy.copy(addon_prefs.bone_name)
        self.bone_name_suffix = copy.copy(addon_prefs.bone_name_suffix)
        self.bone_name_junction = copy.copy(addon_prefs.bone_name_junction)
        self.zero_padding = int(copy.copy(addon_prefs.zero_padding))

        self.is_reverse = copy.copy(addon_prefs.is_reverse)
        self.is_parent = copy.copy(addon_prefs.is_parent)
        self.use_connect = copy.copy(addon_prefs.use_connect)

    def __init__(self):
        self.get_user_pref(self)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and (obj.mode == 'EDIT'):
            # Check if select_mode is 'Edge Select'.
            if context.scene.tool_settings.mesh_select_mode[1]:
                return True
        return False

    def invoke(self, context, event):
        scene = context.scene
        wm = context.window_manager

        return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.set_user_pref(self)

        return {'FINISHED'}


class Edge2BoneBase(bpy.types.Operator):

    def __init__(self):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        self.bone_name = copy.copy(addon_prefs.bone_name)
        self.bone_name_junction = copy.copy(addon_prefs.bone_name_junction)
        self.bone_name_suffix = copy.copy(addon_prefs.bone_name_suffix)
        self.zero_padding = int(copy.copy(addon_prefs.zero_padding))

        self.is_reverse = copy.copy(addon_prefs.is_reverse)
        self.is_parent = copy.copy(addon_prefs.is_parent)
        self.use_connect = copy.copy(addon_prefs.use_connect)

        self.active = None
        self.bm = None
        self.location = (0, 0, 0)
        self.new_bones = []

    @staticmethod
    def _get_distance(vector0, vector1):
        distance = math.sqrt((vector0[0]-vector1[0])**2 +
                             (vector0[1]-vector1[1])**2 +
                             (vector0[2]-vector1[2])**2)
        return distance

    @staticmethod
    def _get_select_edge_location(self, context, bm):
        new_bones = []
        head = None
        tail = None

        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            bm.edges.ensure_lookup_table()

        for e in bm.select_history:
            if isinstance(e, bmesh.types.BMEdge) and e.select:
                v0 = copy.copy(e.verts[0].co)
                v1 = copy.copy(e.verts[1].co)
                if(head):
                    if self._get_distance(head, v0) > self._get_distance(head, v1):
                        v0, v1 = v1, v0
                    if(not self.use_connect):
                        head = copy.copy(v0)
                    tail = copy.copy(v1)
                else:
                    if(self.is_reverse):
                        v0, v1 = v1, v0
                    head = copy.copy(v0)
                    tail = copy.copy(v1)

                new_bones.append({"head": head, "tail": tail, "roll": 0})
                head = tail

        return new_bones

    @staticmethod
    def _get_select_edge_loops_location(self, context, bm):
        current_local = False
        current_cursor = copy.copy(context.scene.cursor_location)
        edge_indexes = []
        new_bones = []
        head = None
        tail = None

        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            bm.edges.ensure_lookup_table()

        for select_edge in bm.select_history:
            if isinstance(select_edge, bmesh.types.BMEdge) and select_edge.select:
                edge_indexes.append(copy.copy(select_edge.index))

        bpy.ops.mesh.select_all(action='DESELECT')

        # Check if local view is enabled
        if context.space_data.local_view:

            # Disable local view
            bpy.ops.view3d.localview()
            current_local = True

        for i in range(len(edge_indexes)):
            for e in bm.edges:
                if(e.index == edge_indexes[i]):
                    e.select = True
                    bmesh.update_edit_mesh(self.active.data, True)

                    bpy.ops.mesh.loop_multi_select(ring=False)
                    bpy.ops.view3d.snap_cursor_to_selected()

                    if(i == 0):
                        head = copy.copy(context.scene.cursor_location)
                    else:
                        tail = copy.copy(context.scene.cursor_location)
                        new_bones.append({"head": head, "tail": tail, "roll": 0})
                        head = tail

                    print(head, tail)

                    bpy.ops.mesh.select_all(action='DESELECT')

        if current_local:
            bpy.ops.view3d.localview()

        context.scene.cursor_location = current_cursor

        return new_bones

    def main(self, obj):
        current_cursor = copy.copy(bpy.context.scene.cursor_location)
        parentBone = None
        bone_name = self.bone_name+self.bone_name_junction
        bone_name_suffix = ""

        if (self.bone_name_suffix != ""):
            bone_name_suffix = self.bone_name_junction+self.bone_name_suffix

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=self.location)

        for i in range(len(self.new_bones)):
            bone = bpy.context.object.data.edit_bones.new(bone_name+str(i+1).rjust(self.zero_padding, '0')+bone_name_suffix)
            bone.head = self.new_bones[i]['head']
            bone.tail = self.new_bones[i]['tail']
            bone.roll = self.new_bones[i]['roll']
            if(parentBone):
                bone.parent = parentBone
                bone.use_connect = self.use_connect
            if(self.is_parent):
                parentBone = bone

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        bpy.context.scene.cursor_location = current_cursor

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and (obj.mode == 'EDIT'):
            # Check if select_mode is 'EDGE'
            if context.scene.tool_settings.mesh_select_mode[1]:
                return True
        return False

    def invoke(self, context, event):

        self.active = context.scene.objects.active
        self.active.update_from_editmode()

        self.bm = bmesh.new()
        self.bm = bmesh.from_edit_mesh(self.active.data)

        if len(self.active.data.edges) < 1:
            self.report({'ERROR'}, "This mesh has no edges.")
            return

    def execute(self, context):

        obj = context.object

        if obj.type != 'MESH':
            raise TypeError("Active object is not a Mesh.")

        if obj:
            self.main(obj)

        return {'FINISHED'}


class Edge2BoneOperator(Edge2BoneBase):
    bl_idname = "rigging.edge_to_borne"
    bl_label = "Create Bone From Edge"
    bl_description = "Creates a new bone from the selected edge location"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        self.active = context.scene.objects.active
        self.active.update_from_editmode()

        self.bm = bmesh.new()
        self.bm = bmesh.from_edit_mesh(self.active.data)

        if len(self.active.data.edges) < 1:
            self.report({'ERROR'}, "This mesh has no edges.")
            return

        self.location = self.active.location
        self.new_bones = self._get_select_edge_location(self, context, self.bm)

        # --- if none report an error and quit
        if not self.new_bones:
            self.report({'ERROR'}, "You must select one or more sides.")
            return

        return self.execute(context)


class EdgeLoops2BoneOperator(Edge2BoneBase):
    bl_idname = "rigging.edge_loop_to_borne"
    bl_label = "Create Bone From Edge Loops Midpoint"
    bl_description = "Creates a new bone from the midpoints of two or more selected edge loops"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        self.active = context.scene.objects.active
        self.active.update_from_editmode()

        self.bm = bmesh.new()
        self.bm = bmesh.from_edit_mesh(self.active.data)

        if len(self.active.data.edges) < 1:
            self.report({'ERROR'}, "This mesh has no edges.")
            return

        self.new_bones = self._get_select_edge_loops_location(self, context, self.bm)

        # --- if none report an error and quit
        if not self.new_bones:
            self.report({'ERROR'}, "You must select two or more sides.")
            return

        return self.execute(context)


classes = (
    Edge2BonePreferences,
    Edge2BoneSettingsOperator,
    Edge2BoneOperator,
    EdgeLoops2BoneOperator
)


def edit_mesh_edge_menu(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.separator()
    self.layout.operator(Edge2BoneSettingsOperator.bl_idname, icon="PLUGIN")

    self.layout.separator()
    self.layout.operator(Edge2BoneOperator.bl_idname, icon="PLUGIN")
    self.layout.operator(EdgeLoops2BoneOperator.bl_idname, icon="PLUGIN")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_edges.append(edit_mesh_edge_menu)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(edit_mesh_edge_menu)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
