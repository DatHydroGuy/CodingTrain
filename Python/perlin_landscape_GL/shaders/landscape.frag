#version 130
in vec4 newColour;     // needs to have the same name as the output from vertex shader
out vec4 outColour;

void main()
{
   outColour = newColour;
}
