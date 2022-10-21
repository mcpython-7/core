#version 330 core
in vec3 vertices;
in vec2 uvCoord;
in vec3 position;

out vec2 uvCoords;
out vec3 vertex_position;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    vec4 pos = window.view * model * vec4(vertices, 1.0);
    gl_Position = window.projection * pos;
    mat3 normal_matrix = transpose(inverse(mat3(model)));

    vertex_position = pos.xyz;
    uvCoords = uvCoord;
}