#version 330 core

uniform sampler2D screenTexture;
uniform sampler2D shadowMap;

in vec2 Position;

out vec4 color;

void main(){
    vec2 TexCoords = Position * 0.5 + 0.5;
    //color = texture(screenTexture, TexCoords);

    //float lum = 

    float amount = 0.4;
    float radius = 0.4;

    // vignete
    float distance = length(TexCoords - vec2(0.5, 0.5));
    float vignete = smoothstep(0.8, radius, distance);

    color = texture(screenTexture, TexCoords);

    color.rgb *= vignete;
}