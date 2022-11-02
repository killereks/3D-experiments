#version 330 core

layout (location=0) in vec3 vPos;
layout (location=1) in vec3 vNormal;
layout (location=2) in vec2 vTexCoords;

uniform float time;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(){
    gl_Position = transpose(projection) * transpose(view) * transpose(model) * vec4(vPos, 1.0);

    Normal = vNormal;
    FragPos = vec3(model * vec4(vPos, 1.0));
    //Normal = normalize(mat3(transpose(inverse(model))) * vNormal);
    // we don't transpose because (A^T)^T = A
    Normal = normalize(mat3(inverse(model)) * vNormal);
    TexCoords = vTexCoords;
}