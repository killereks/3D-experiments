#version 330 core

layout (location=0) in vec3 vPos;
layout (location=1) in vec3 vNormal;
layout (location=2) in vec2 vTexCoords;

uniform float time;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;

out vec4 FragPosLightSpace;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 lightSpaceMatrix; // world space -> light space

void main(){
    gl_Position = projection * view * model * vec4(vPos, 1.0);

    Normal = normalize(transpose(inverse(mat3(model))) * vNormal);
    FragPos = vec3(model * vec4(vPos, 1.0));
    TexCoords = vTexCoords;

    FragPosLightSpace = lightSpaceMatrix * vec4(FragPos, 1.0);
}