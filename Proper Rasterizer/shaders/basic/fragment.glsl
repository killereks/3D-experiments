#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

in vec4 FragPosLightSpace;

out vec4 color;

uniform float time;

uniform sampler2D _MainTex;
uniform sampler2D shadowMap;

uniform vec2 tiling = vec2(10.0, 10.0);

uniform vec3 lightPos;
//uniform vec3 viewPos;

float shadowCalc(float dotLightNormal, vec2 offset){
    float bias = max(0.05 * (1.0 - dotLightNormal), 0.005);
    vec3 pos = FragPosLightSpace.xyz * 0.5 + 0.5;
    float depth = texture(shadowMap, pos.xy + offset).r;
    return depth + bias < pos.z ? 0.0 : 1.0;
}

float softShadows(float dotLightNormal){
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    float shadow = 0.0;
    
    int size = 2;
    for (int x = -size; x <= size; ++x) {
        for (int y = -size; y <= size; ++y) {
            float pcfDepth = shadowCalc(dotLightNormal, vec2(x, y) * texelSize);
            shadow += pcfDepth;
        }
    }

    return shadow / (float(size) * float(size) * 4);
}

void main(){
    vec3 texColor = texture(_MainTex, TexCoords * tiling).rgb;
    vec3 norm = normalize(Normal);

    vec3 lightDir = normalize(lightPos - Position);
    float dotLightNormal = max(dot(norm, lightDir), 0.0);

    float shadow = softShadows(dotLightNormal);
    vec3 lighting = shadow * dotLightNormal * texColor * 0.6;

    color = vec4(lighting, 1.0);
}
