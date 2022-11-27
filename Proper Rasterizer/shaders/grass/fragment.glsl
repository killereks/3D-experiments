#version 330 core

out vec4 FragColor;

uniform vec3 sunPosition;
uniform vec3 sunDirection;

in vec3 position;
in vec2 uv;
in vec3 normal;
flat in int m_ID;

#define PHI 1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374
#define PI  3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
#define E   2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274

float random21(vec2 id){
    highp float a = 12.9898;
    highp float b = 78.233;
    highp float c = 43758.5453;
    highp float dt= dot(id.xy ,vec2(a,b));
    highp float sn= mod(dt,PI);
    return fract(sin(sn) * c);
}

void main(){
    // 567D46
    vec3 grassColor1 = vec3(0.337, 0.490, 0.271);
    // 4E7A3E
    vec3 grassColor2 = vec3(0.306, 0.478, 0.243);
    // 3E6A2E
    vec3 grassColor3 = vec3(0.243, 0.416, 0.180);
    // 2E5A1E
    vec3 grassColor4 = vec3(0.180, 0.353, 0.118);

    // pick grass color based on UV using mix
    vec3 grassColor = mix(mix(grassColor1, grassColor2, uv.y), mix(grassColor3, grassColor4, uv.y), uv.x);

    float shade = random21(vec2(m_ID, m_ID * 5.0)) * 0.3 + 0.7;

    // calculate light intensity
    //float lightIntensity = dot(normal, -sunDirection);
    //grassColor *= lightIntensity;

    // set fragment color
    FragColor = vec4(grassColor * shade, 1.0);
}