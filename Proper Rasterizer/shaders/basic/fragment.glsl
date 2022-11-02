#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

out vec4 color;

uniform float time;

uniform sampler2D _MainTex;

vec3 ProceduralTexture(vec2 input){
    return vec3(sin(input.x * 10.0), cos(input.y * 10.0), 0.0);
}

void main(){
    // light direction with rotation
    // 45x, 60y, 0z
    vec3 lightDir = normalize(vec3(45.0, 60.0, 0.0));
    // diffuse shading
    float diff = max(dot(Normal, lightDir), 0.0);

    //color = vec4(ProceduralTexture(TexCoords), 1.0);
    //color = vec4(TexCoords, 1.0, 1.0);
    //color = vec4(Normal, 1.0);

    //color = vec4(Normal * intensity, 1.0);
    color = texture(_MainTex, TexCoords) * diff;
    //color = vec4(Normal, 1.0);
}
