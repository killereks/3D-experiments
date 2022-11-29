#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

in vec4 FragPosLightSpace;

out vec4 FragColor;

in mat3 TBN;

uniform float time;

uniform sampler2D _MainTex;
uniform sampler2D _RoughnessMap;
uniform sampler2D _NormalMap;

uniform samplerCube _Skybox;

uniform sampler2D shadowMap;

uniform vec2 tiling = vec2(1.0, 1.0);
uniform vec2 tiling_speed = vec2(0.0, 0.0);

uniform vec3 lightPos;
uniform vec3 lightDir;

uniform vec3 camPos;
uniform vec3 camFwd;

// material properties
uniform float Ka; // ambient
uniform float Kd; // diffuse
uniform float Ks; // specular

uniform float Ns; // shininess (specular exponent)
uniform float metallic; // refraction index

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

in vec3 fragWorldPos;

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
    for (int x = -size; x <= size; ++x){
        for (int y = -size; y <= size; ++y){
            vec2 offset = vec2(x, y) * texelSize;
            shadow += shadowCalc(dotLightNormal, offset);
        }
    }
    shadow /= (float(size) * 2.0 + 1.0) * (float(size) * 2.0 + 1.0);
    return shadow;
}

float distributionGGX(float NdotH, float roughness){
    float a = roughness * roughness;
    float a2 = a * a;
    float denom = NdotH * NdotH * (a2 - 1.0) + 1.0;
    denom = PI * denom * denom;

    return a2 / max(denom, 0.0001);
}

float geometrySmith(float NdotV, float NdotL, float roughness){
    float r = roughness + 1.0;
    float k = (r * r) / 8.0;
    float ggx1 = NdotV / (NdotV * (1.0 - k) + k);
    float ggx2 = NdotL / (NdotL * (1.0 - k) + k);
    return ggx1 * ggx2;
}

vec3 fresnelSchlick(float HdotV, vec3 baseReflectivity){
    return baseReflectivity + (1.0 - baseReflectivity) * pow(1.0 - HdotV, 5.0);
}

void main(){
    vec2 uv = TexCoords * tiling + time * tiling_speed;

    vec3 albedo = texture(_MainTex, uv).rgb;
    float alpha = texture(_MainTex, uv).a;
    float roughness = texture(_RoughnessMap, uv).r;

    if (alpha < 0.5) discard;

    vec3 normal = texture(_NormalMap, uv).rgb;
    normal = normal * 2.0 - 1.0;
    normal = normalize(TBN * normal);

    vec3 N = normalize(normal);
    vec3 V = normalize(camPos - fragWorldPos);

    vec3 baseReflectivity = mix(vec3(0.04), albedo, metallic);

    vec3 Lo = vec3(0.0);
    
    vec3 L = normalize(lightPos - fragWorldPos);
    vec3 H = normalize(V + L);
    
    float NdotV = max(dot(N, V), 0.0000001);
    float NdotL = max(dot(N, L), 0.0000001);
    float HdotV = max(dot(H, V), 0.0);
    float NdotH = max(dot(N, H), 0.0);

    float D = distributionGGX(NdotH, roughness);
    float G = geometrySmith(NdotV, NdotL, roughness);
    vec3 F = fresnelSchlick(HdotV, baseReflectivity);

    vec3 specular = D * G * F;
    specular /= 4.0 * NdotV * NdotL;
    // don't apply specular if in shadow
    float shadow = softShadows(NdotL);
    if (shadow < 1.0) specular = vec3(0.0);

    // diffuse
    vec3 kD = vec3(1.0) - F;

    // conserve energy
    kD *= 1.0 - metallic;

    // diffuse and ambient
    Lo += (kD * albedo / PI + specular) * NdotL;

    vec3 ambient = vec3(0.03) * albedo;

    vec3 color = ambient + Lo;
    
    //color = color / (color + vec3(1.0));

    // skybox reflection
    vec3 R = reflect(-V, N);
    vec3 envColor = texture(_Skybox, R).rgb;
    color = mix(color, envColor, metallic);

    // apply shadows
    color *= shadow;
    
    FragColor = vec4(color, 1.0);
}