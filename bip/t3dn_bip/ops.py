import bpy
from .utils import support_pillow, install_pillow


class InstallPillow:
    bl_label = 'Install Pillow'
    bl_description = 'Install the Python Imaging Library'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self: bpy.types.Operator, context: bpy.types.Context) -> set:
        if support_pillow():
            self.report({'INFO'}, 'Pillow is already installed')
            return {'CANCELLED'}
        else:
            install_pillow()

        if support_pillow():
            self.report({'INFO'}, 'Pillow was installed successfully')
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, 'Pillow failed to install')
            return {'CANCELLED'}
