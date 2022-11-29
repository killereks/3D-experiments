#version 330 core

out vec4 FragColor;

in vec3 texCoords;

uniform samplerCube skybox;

uniform vec3 sunColor;

void main(){
    vec3 color = texture(skybox, texCoords).rgb * sunColor;
    FragColor = vec4(color, 1.0);
}