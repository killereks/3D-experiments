#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

out vec4 color;

uniform float time;

void main(){
    vec3 lightPos = vec3(sin(time), 0.0, cos(time));
    float dist = length(lightPos - Position);
    float attenuation = 1.0 / (dist * dist);
    float intensity = attenuation * max(0,dot(Normal, normalize(lightPos - Position)));

    color = vec4(Normal * intensity, 1.0);
}