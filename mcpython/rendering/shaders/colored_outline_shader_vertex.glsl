#version 330 core
in vec3 position;
in vec2 tex_coords;
in vec4 colors;

out vec2 texture_coords;
out vec3 vertex_position;
out vec4 coloring;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    vec4 pos = window.view * model * vec4(position, 1.0);
    gl_Position = window.projection * pos;

    vertex_position = pos.xyz;
    texture_coords = tex_coords;
    coloring = colors;
}