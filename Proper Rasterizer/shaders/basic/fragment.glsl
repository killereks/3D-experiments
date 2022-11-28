#version 330 core

in vec3 Position;
in vec3 Normal;
in vec2 TexCoords;

in vec4 FragPosLightSpace;

out vec4 FragColor;

uniform float time;

uniform sampler2D _MainTex;
uniform sampler2D _NormalMap;
uniform sampler2D _RoughnessMap;
uniform sampler2D _DisplacementMap;

uniform samplerCube _Skybox;

uniform sampler2D shadowMap;

uniform vec2 tiling = vec2(1.0, 1.0);
uniform vec2 tiling_speed = vec2(0.0, 0.0);

uniform vec3 lightPos;
uniform vec3 viewDir;

// material properties
uniform float Ka; // ambient
uniform float Kd; // diffuse
uniform float Ks; // specular

uniform float Ns; // shininess (specular exponent)
uniform float Ni; // optical density (index of refraction)
uniform float d; // dissolve (opacity)
uniform int illum; // illumination model

#define PI 3.1415926535917932384626433832795

#define SHADOW_ALPHA 0.4

float random21(vec2 p){
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float shadowCalc(float dotLightNormal, vec2 offset){
    float bias = max(0.05 * (1.0 - dotLightNormal), 0.005);
    vec3 pos = FragPosLightSpace.xyz * 0.5 + 0.5;
    if (pos.z > 1.0) return SHADOW_ALPHA;
    float depth = texture(shadowMap, pos.xy + offset).r;
    return depth + bias < pos.z ? SHADOW_ALPHA : 1.0;
}

float softShadows(float dotLightNormal){
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    float shadow = 0.0;
    
    int size = 2;
    for (int x = -size; x <= size; ++x) {
        for (int y = -size; y <= size; ++y) {
            vec2 offset = vec2(x,y) * texelSize; //random21(vec2(x, y)) * texelSize;
            float pcfDepth = shadowCalc(dotLightNormal, offset);
            shadow += pcfDepth;
        }
    }

    return shadow / (float(size) * float(size) * 4);
}

float saturate(float x){
    return clamp(x, 0.0, 1.0);
}

float phong_diffuse(){
    return 1.0 / PI;
}

vec3 fresnel_factor(in vec3 f0, in float product){
    return mix(f0, vec3(1.0), pow(1.01 - product, 5.0));
}

float D_blinn(in float roughness, in float NdH){
    float m = roughness * roughness;
    float m2 = m * m;
    float n = 2.0 / m2 - 2.0;
    return (n+2.0) / (2.0 * PI) * pow(NdH, n);
}

float D_beckmann(in float roughness, in float NdH){
    float m = roughness * roughness;
    float m2 = m * m;
    float NdH2 = NdH * NdH;
    return exp((NdH2 - 1.0) / (m2 * NdH2)) / (PI * m2 * NdH2 * NdH2);
}

float D_GGX(in float roughness, in float NdH){
    float m = roughness * roughness;
    float m2 = m * m;
    float d = (NdH * m2 - NdH) * NdH + 1.0;
    return m2 / (PI * d * d);
}

float G_shlick(in float roughness, in float NdV, in float NdL){
    float k = roughness * roughness * 0.5;
    float V = NdV * (1.0 - k) + k;
    float L = NdL * (1.0 - k) + k;
    return 0.25 / (V * L);
}

vec3 phong_specular(in vec3 V, in vec3 L, in vec3 N, in vec3 specular, in float roughness){
    vec3 R = reflect(-L, N);
    float spec = max(0.0, dot(V,R));

    float k = 1.999 / (roughness * roughness);

    return min(1.0, 3.0 * 0.0398 * k) * pow(spec, min(10000.0, k)) * specular;
}

vec3 blinn_specular(in float NdH, in vec3 specular, in float roughness){
    float k = 1.999 / (roughness * roughness);

    return min(1.0, 3.0 * 0.0398 * k) * pow(NdH, min(10000.0, k)) * specular;
}

vec3 cooktorrance_specular(in float NdL, in float NdV, in float NdH, in vec3 specular, in float roughness){
    // if using cook_blinn
    // float D = D_blinn(roughness, NdH);
    // if using cook_beckmann
    // float D = D_beckmann(roughness, NdH);
    // if using cook_ggx
    float D = D_GGX(roughness, NdH);
    float G = G_shlick(roughness, NdV, NdL);

    float rim = mix(1.0 - roughness * 0.9, 1.0, NdV);

    return (1.0 / rim) * specular * G * D;
}

void main(){
    vec2 uv = TexCoords * tiling + tiling_speed * time;

    // PBR shading
    vec3 albedo = texture(_MainTex, uv).rgb;
    vec3 normal = texture(_NormalMap, uv).rgb;
    float roughness = texture(_RoughnessMap, uv).r;
    vec3 displacement = texture(_DisplacementMap, uv).rgb;

    float alpha = texture(_MainTex, uv).a;

    vec3 lightDir = normalize(lightPos - Position);
    float NdotL = max(dot(Normal, lightDir), 0.0);
    //vec3 color = albedo * softShadows(NdotL) * NdotL;
    
    float ambient = Ka;
    float diffuse = Kd * NdotL;
    float specular = Ks * pow(max(dot(reflect(-lightDir, Normal), normalize(viewDir)), 0.0), Ns);

    vec3 combined = (ambient + diffuse + specular) * albedo;
    vec3 color = combined * softShadows(NdotL);

    // apply reflections from the skybox
    /*vec3 reflectDir = reflect(-lightDir, Normal);
    vec3 skyColor = texture(_Skybox, reflectDir).rgb;
    color = mix(color, skyColor, 0.0);*/

    //if (alpha < 0.5) discard;

    FragColor = vec4(color, 1.0);
}