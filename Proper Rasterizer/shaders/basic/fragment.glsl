#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

in vec4 FragPosLightSpace;

out vec4 color;

uniform float time;

uniform sampler2D _MainTex;
uniform sampler2D _NormalMap;
uniform sampler2D _RoughnessMap;

uniform sampler2D shadowMap;

uniform vec2 tiling = vec2(10.0, 10.0);

uniform vec3 lightPos;
uniform vec3 viewDir;

const float M_PI = 3.1415926535897932384626433832795;

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
    // PBR shading
    vec3 albedo = texture(_MainTex, TexCoords * tiling).rgb;
    vec3 normal = texture(_NormalMap, TexCoords * tiling).rgb;
    float roughness = texture(_RoughnessMap, TexCoords * tiling).r;
    float metalness = 0.0;

    float lightDot = max(0.0, dot(Normal, normalize(lightPos - Position)));
    
    vec3 outColor = albedo * softShadows(lightDot) * lightDot;

    color = vec4(outColor, 1.0);
}
