#version 330 core

layout (location = 0) in vec2 aPos;

out vec2 Position;
out vec4 FragPosLightSpace;

uniform mat4 lightModel;
uniform mat4 lightSpaceMatrix;

void main(){
    gl_Position = vec4(aPos, 0.0, 1.0);
    Position = aPos;

    FragPosLightSpace = lightSpaceMatrix * lightModel * vec4(aPos, 0.0, 1.0);
}