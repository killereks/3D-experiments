#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 vUV;
layout (location = 2) in vec3 inNormal;

uniform mat4 projection;
uniform mat4 view;

uniform sampler2D heightMap;

uniform mat4 lightSpaceMatrix;
uniform bool isShadowMap;

uniform vec2 worldYBounds;

uniform float time;
uniform float spawnRadius;

mat4 model;

out vec3 position;
out vec2 uv;
out vec3 normal;

out vec3 lightFragPos;

flat out int m_ID;

#define PHI 1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374
#define PI  3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
#define E   2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274

float random21(vec2 id){
    highp float a = 12.9898;
    highp float b = 78.233;
    highp float c = 43758.5453;
    highp float dt= dot(id.xy ,vec2(a,b));
    highp float sn= mod(dt,PI);
    highp float val = fract(sin(sn) * c);

    // make sure val is between 0-1
    return abs(val);
}

vec3 random13(int id){
    return vec3(sin(float(id)*12.9898), cos(float(id)*78.233), sin(float(id)*45.164));
}

float rand(vec2 c){
    return fract(sin(dot(c.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(vec2 p, float freq){
    float unit = 1.0/freq;
    vec2 ij = floor(p*unit);
    vec2 xy = fract(p*unit);
    xy = 0.5 * (1.0 - cos(PI * xy));

    float a = rand((ij + vec2(0.0, 0.0)));
    float b = rand((ij + vec2(1.0, 0.0)));
    float c = rand((ij + vec2(0.0, 1.0)));
    float d = rand((ij + vec2(1.0, 1.0)));
    
    float x1 = mix(a, b, xy.x);
    float x2 = mix(c, d, xy.x);
    float value = mix(x1, x2, xy.y);
    return value;
}

float pNoise(vec2 p, int res){
    float persistance = 0.5;
    float n = 0.0;
    float normK = 0.0;
    float f = 4.0;
    float amp = 1.0;
    int iCount = 0;
    for (int i = 0; i < 50; i++){
        n += amp * noise(p, f);
        f *= 2.0;
        normK += amp;
        amp *= persistance;
        if (iCount == res) break;
        iCount++;
    }

    float nf = n / normK;
    return nf * nf * nf * nf;
}

mat4 translateMatrix(vec3 v){
    return mat4(1, 0, 0, v.x,
                0, 1, 0, v.y,
                0, 0, 1, v.z,
                0, 0, 0, 1);
}

mat4 rotationYMatrix(float angle){
    float s = sin(angle);
    float c = cos(angle);

    return mat4(c, 0, s, 0,
                0, 1, 0, 0,
                -s, 0, c, 0,
                0, 0, 0, 1);
}

mat4 scaleMatrix(vec3 v){
    return mat4(v.x, 0, 0, 0,
                0, v.y, 0, 0,
                0, 0, v.z, 0,
                0, 0, 0, 1);
}

mat4 CreateModelMatrix(vec3 pos, float rotation, vec3 scale){
    // TRS
    // translate then rotate then scale
    return scaleMatrix(scale) * rotationYMatrix(rotation) * translateMatrix(pos);
}

float remap(float value, float min1, float max1, float min2, float max2){
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

void main(){
    vec2 id = vec2(gl_InstanceID * E * E, gl_InstanceID * PI);

    float size = 400.0;
    float halfSize = size * 0.5;

    float x = remap(random21(id), 0.0, 1.0, 0.5 - spawnRadius, 0.5 + spawnRadius);
    float z = remap(random21(id + random21(id)), 0.0, 1.0, 0.5 - spawnRadius, 0.5 + spawnRadius);

    // map from -size/2 - size/2 to 0 - heightMapSize
    float heightMapSize = textureSize(heightMap, 0).x;
    
    vec2 heightMapUV = vec2(x,1.0-z);

    // get height from heightmap
    //float height = remap(texture(heightMap, heightMapUV).r, 0.0, 1.0, worldYBounds.x, worldYBounds.y);
    float height = remap(texture(heightMap, heightMapUV).r, 0.0, 1.0, worldYBounds.x, worldYBounds.y);

    vec3 pos = vec3(x,0.0,z) * size - halfSize;
    pos.y = height;

    float rotation = random21(pos.xz) * PI * 2.0;
    float scale = rand(id) * 20.0 + 5.0;

    mat4 model = CreateModelMatrix(pos, rotation, vec3(scale));

    // simulate wind by moving the blades, the higher the wind the faster the blades move
    vec3 windDirection = vec3(1.0, 0.0, 1.0);

    // bottom of the blade moves less than the top
    // use UV to determine the position of the blade
    vec4 worldPos = transpose(model) * vec4(inPosition, 1.0);

    float noiseScale = pNoise(worldPos.xz * 2.0 + time * 10.0, 10) * 1.0;
    float windTurbulence = pNoise(worldPos.xz + time * 25.0, 10) * 0.1;

    float heightInfluence = scale / 15.0;

    worldPos.xyz += windDirection * (noiseScale + windTurbulence) * heightInfluence * max(vUV.y-0.1, 0.0);// * vUV.y;

    if (isShadowMap){
        gl_Position = lightSpaceMatrix * worldPos;
    } else {
        gl_Position = projection * view * worldPos;
    }

    position = pos;
    uv = vec2(vUV.x, vUV.y);
    // transform normals to world space
    // Normal = normalize(transpose(inverse(mat3(model))) * vNormal);
    normal = normalize(transpose(inverse(mat3(model))) * inNormal);
    m_ID = gl_InstanceID;

    lightFragPos = vec3(lightSpaceMatrix * worldPos);
}