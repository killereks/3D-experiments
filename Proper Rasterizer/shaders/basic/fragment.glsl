#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

out vec4 color;

uniform float time;

vec3 ProceduralTexture(vec2 input){
    return vec3(sin(input.x * 10.0), cos(input.y * 10.0), 0.0);
}

void main(){
    //vec3 lightPos = vec3(sin(time), 1.0, cos(time));
    vec3 lightPos = vec3(-1.0, 0.0, 0.0);
    float dist = length(lightPos - Position);
    float attenuation = 1.0 / (dist * dist);
    float intensity = attenuation * max(0,dot(Normal, normalize(lightPos - Position)));

    color = vec4(ProceduralTexture(TexCoords), 1.0);

    //color = vec4(Normal * intensity, 1.0);
    //color = vec4(Normal, 1.0);
}
