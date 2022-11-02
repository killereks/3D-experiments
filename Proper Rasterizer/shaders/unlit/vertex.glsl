#version 330 core

layout (location=0) in vec3 vPos;
layout (location=1) in vec3 vFragColor;

out vec3 Position;
out vec3 FragColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(){
    gl_Position = transpose(projection) * transpose(view) * transpose(model) * vec4(vPos, 1.0);

    Position = vPos;
    FragColor = vFragColor;
}