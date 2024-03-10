# core

The core of the game, written for python 3.12+ and pyglet 2.0+

I have the following pyglet 2.0 OpenGL 3.3 Code setting up a perspective projection: self.projection = Mat4.perspective_projection(
    self.aspect_ratio, z_near=0.1, z_far=100, fov=45
)

glClear(GL_DEPTH_BUFFER_BIT)
self.view = (
    Mat4.look_at(Vec3(2, 2, 2), Vec3(0, 0, 0), Vec3(0, 1, 0))
    @ Mat4.from_scale(Vec3(0.1, 0.1, 0.1))
)  How can I offset the resulting render by an pixel amount on the window?

