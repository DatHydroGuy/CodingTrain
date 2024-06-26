#version 130
in vec4 position;
in vec4 colour;
uniform mat4 transformation;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 newColour;

void main()
{
   gl_Position = projection * view * model * transformation * position;
   newColour = colour;
}
