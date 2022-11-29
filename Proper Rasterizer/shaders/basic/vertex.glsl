#version 330 core

layout (location=0) in vec3 vPos;
layout (location=1) in vec3 vNormal;
layout (location=2) in vec2 vTexCoords;
layout (location=3) in vec3 tangent;
layout (location=4) in vec3 bitangent;

uniform float time;

out vec3 FragPos;
out vec2 TexCoords;
out vec3 Normal;
out vec4 FragPosLightSpace;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 lightSpaceMatrix; // world space -> light space

out vec3 fragWorldPos;

out mat3 TBN;

void main(){
    fragWorldPos = vec3(model * vec4(vPos, 1.0));

    gl_Position = projection * view * model * vec4(vPos, 1.0);

    FragPos = vec3(model * vec4(vPos, 1.0));
    Normal = normalize(transpose(inverse(mat3(model))) * vNormal);
    TexCoords = vTexCoords;

    TBN = mat3(tangent, bitangent, vNormal);
    TBN = transpose(TBN);

    FragPosLightSpace = lightSpaceMatrix * vec4(FragPos, 1.0);
}