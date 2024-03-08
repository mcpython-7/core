#version 330 core
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform sampler2D our_texture;

void main()
{
    final_colors = (texture(our_texture, texture_coords));
}