#version 330 core
in vec2 position;
in vec2 tex_coords;

out vec2 texture_coords;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    gl_Position = window.projection * model * window.view * vec4(position, 0.0, 1.0);

    texture_coords = tex_coords;
}