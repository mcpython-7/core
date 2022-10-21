#version 330 core
uniform sampler2D texture;
in vec2 uvCoords;

out vec4 fragColor;
void main()
{
    fragColor.rgb = texture(texture, uvCoords).rgb;
}
