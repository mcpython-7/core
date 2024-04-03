#version 330 core
in vec3 position;
in vec2 render_offset;
in vec2 tex_coords;
in vec4 colors;

out vec2 texture_coords;
out vec4 coloring;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    gl_Position = window.projection * model * window.view * vec4(position, 1.0);
    gl_Position.xy += render_offset; // Adding screen offset in pixels

    texture_coords = tex_coords;
    coloring = colors;
}