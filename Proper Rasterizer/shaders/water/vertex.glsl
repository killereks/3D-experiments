#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 Position;
out vec2 TexCoord;
out vec3 Normal;

// gerstner waves
uniform float time;

#define PI 3.1415926535897932384626433832795

// taken from https://catlikecoding.com/unity/tutorials/flow/waves/
vec4 GerstnerWave(vec3 worldPos, float time, float amplitude, float wavelength, float speed, float steepness, vec2 direction){
    // returns height in w
    // and normal in xyz

    vec4 output = vec4(0.0);
    
    float k = 2.0 * PI / wavelength;
    float c = sqrt(9.81 / k);
    float phi = k * (dot(worldPos.xz, direction) - c * time);

    output.w = amplitude * cos(phi);
    output.xyz = -steepness * amplitude * k * speed * sin(phi) * vec3(direction.x, 0.0, direction.y);

    return output;
}

vec4 MultipleGertsnerWaves(vec3 worldPos, float time){
    vec4 output = vec4(0.0);
    
    output += GerstnerWave(worldPos, time, 0.2, 20.0, 1.0, 0.5, vec2(1.0, 0.0));
    output += GerstnerWave(worldPos, time, 0.3, 30.0, 1.0, 0.5, vec2(0.0, 1.0));
    output += GerstnerWave(worldPos, time, 0.1, 40.0, 1.0, 0.5, vec2(1.0, 1.0));
    output += GerstnerWave(worldPos, time, 0.3, 80.0, 1.0, 0.5, vec2(-1.0, 1.0));
    output += GerstnerWave(worldPos, time, 0.2, 60.0, 1.0, 0.5, vec2(1.0, -1.0));

    //output += GerstnerWave(worldPos, time, 0.2, 30.0, 1.0, 0.5, vec2(1.0, 0.0));
    //output += GerstnerWave(worldPos, time, 0.1, 25.0, 0.5, 0.7, vec2(0.0, 1.0));
    //output += GerstnerWave(worldPos, time, 0.16, 34.0, 0.3, 0.1, vec2(1.0, 1.0));
    //output += GerstnerWave(worldPos, time, 0.12, 29.0, 1.5, 0.2, vec2(-1.0, 1.0));
    //output += GerstnerWave(worldPos, time, 0.1, 14.0, 3.0, 0.3, vec2(1.0, -1.0));
    //output += GerstnerWave(worldPos, time, 0.17, 68.0, 0.7, 0.4, vec2(-1.0, -1.0));

    return output;
}

void main(){
    vec4 worldPos = model * vec4(aPos, 1.0);
    
    vec4 wave = MultipleGertsnerWaves(worldPos.xyz, time);
    worldPos.y += wave.w;

    gl_Position = projection * view * worldPos;

    Position = worldPos.xyz;
    Normal = normalize(wave.xyz);
    TexCoord = aTexCoord;
}