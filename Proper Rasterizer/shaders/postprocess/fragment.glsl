#version 330 core

uniform sampler2D screenTexture;
uniform sampler2D shadowMap;
uniform sampler2D cameraDepthMap;

uniform vec3 lightPos;
uniform vec3 lightDir;

uniform vec3 camPos;
uniform vec3 camFwd;
uniform vec3 camUp;
uniform vec3 camRight;

uniform mat4 projection;
uniform mat4 view;

uniform float time;

#define USE_ACES 1
#define USE_VIGNETTE 1

#define USE_VOLUMETRIC_LIGHT 1
#define VL_STEP_COUNT 64.0
#define VL_DISTANCE 50.0

#define USE_FILM_GRAIN 0
#define FILM_GRAIN_INTENSITY 0.1
#define FILM_GRAIN_SCANLINE 1

#define PI 3.1415926535897932384626433832795

in vec2 Position;
in vec4 FragPosLightSpace;

uniform mat4 lightModel;
uniform mat4 lightSpaceMatrix;

out vec4 FragColor;

float lineariseDepth(float depth){
    float near = 0.1;
    float far = 500.0;
    return (2.0 * near * far) / (far + near - (depth * 2.0 - 1.0) * (far - near));
}

float random(vec2 st){
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453);
}

vec3 getWorldPosition(vec2 TexCoord){
    float depth = texture(cameraDepthMap, TexCoord).r;

    float z = depth * 2.0 - 1.0;

    vec4 clipSpacePosition = vec4(TexCoord * 2.0 - 1.0, z, 1.0);
    vec4 viewSpacePosition = inverse(projection) * clipSpacePosition;

    viewSpacePosition /= viewSpacePosition.w;

    vec4 worldSpacePosition = inverse(view) * viewSpacePosition;

    return worldSpacePosition.xyz;
}

float worldToShadow(vec3 worldPos){
    // returns if world position is in shadow
    vec4 lightSpacePos = lightSpaceMatrix * vec4(worldPos, 1.0);
    lightSpacePos /= lightSpacePos.w;

    lightSpacePos = lightSpacePos * 0.5 + 0.5;

    float shadow = 1.0;

    float bias = 0.005;

    float closestDepth = texture(shadowMap, lightSpacePos.xy).r;
    float currentDepth = lightSpacePos.z;

    if(currentDepth - bias > closestDepth){
        shadow = 0.0;
    }

    return shadow;
}

vec3 ACES(vec3 colorInput){
    mat3x3 rgb2aces = mat3x3(
        1.0498110175, 0.0000000000, -0.0000974845,
        -0.4959030231, 1.3733130458, 0.0982400361,
        0.0000000000, 0.0000000000, 0.9912520182
    );

    return colorInput * rgb2aces;
}

vec3 Vignette(vec3 colorInput, vec2 uv){
    float vignette = 0.5;
    float vignetteRadius = 0.5;
    float vignetteSoftness = 0.5;

    vec2 vignetteCenter = vec2(0.5, 0.5);
    vec2 vignetteDelta = uv - vignetteCenter;
    float vignetteDistance = length(vignetteDelta);
    float vignetteIntensity = smoothstep(vignetteRadius, vignetteRadius + vignetteSoftness, vignetteDistance);
    vignetteIntensity = 1.0 - vignetteIntensity * vignette;

    return colorInput * vignetteIntensity;
}

// UV = [0,1]
// screenPos = [-1,1]
vec3 VolumetricLighting(vec3 color, vec2 uv, vec2 screenPos){    
    float lum = 0.0;

    float camDepth = lineariseDepth(texture(cameraDepthMap, uv).r);
    vec3 disp = normalize(camFwd + camUp * screenPos.y + camRight * screenPos.x);
    float stepSize = 1.0 / VL_STEP_COUNT;
    float sampleDepth = random(uv + time * 0.01) * stepSize * VL_DISTANCE;

    float iters = 0;

    for (int i = 0; i < VL_STEP_COUNT; i++){
        vec3 pos = camPos + disp * sampleDepth;

        float shadow = worldToShadow(pos);

        if (sampleDepth >= camDepth) break;

        lum += shadow * stepSize;
        //lum += shadow;

        sampleDepth += stepSize * VL_DISTANCE;

        //iters++;
    }

    //lum = lum / iters;


    // clamp lum
    lum = clamp(lum, 0.0, 0.2);
    
    return color + lum;
}

vec3 FilmGrain(vec3 color, vec2 uv){
    // add random noise
    float grain = random(uv + time * 0.01);
    color += grain * FILM_GRAIN_INTENSITY;

    // add scanlines
    float scanline = sin((uv.y + time) * 1000.0) * 0.05;
    color += scanline * FILM_GRAIN_SCANLINE;

    return color;
}

void main(){
    vec2 UV = Position;
    vec2 TexCoords = Position * 0.5 + 0.5;
    vec3 albedo = texture(screenTexture, TexCoords).rgb;
    //color = texture(screenTexture, TexCoords);

    //float lum = 

    // float amount = 0.4;
    // float radius = 0.4;

    // // vignete
    // float distance = length(TexCoords - vec2(0.5, 0.5));
    // float vignete = smoothstep(0.8, radius, distance);

    // mat3x3 rgb2aces = mat3x3(
    //     1.0498110175, 0.0000000000, -0.0000974845,
    //     -0.4959030231, 1.3733130458, 0.0982400361,
    //     0.0000000000, 0.0000000000, 0.9912520182
    // );

    // color = texture(screenTexture, TexCoords);
    // color.rgb *= rgb2aces;
    
    // volumetric lighting
    
    vec3 color = albedo;

    #if USE_VOLUMETRIC_LIGHT
        color = VolumetricLighting(color, TexCoords, Position);
    #endif

    # if USE_FILM_GRAIN
        color = FilmGrain(color, TexCoords);
    # endif

    # if USE_ACES
        color = ACES(color);
    # endif
    
    # if USE_VIGNETTE
        color = Vignette(color, TexCoords);
    # endif
    //FragColor = vec4(color, 1.0);

    //vec3 pos = getWorldPosition(TexCoords);

    float depth = texture(cameraDepthMap, TexCoords).r;
    //FragColor.rgb = vec3(depth);

    //FragColor = vec4(pos, 1.0);

    FragColor = vec4(color, 1.0);

    //FragColor = vec4(length, length, length, 1.0);
    //FragColor = vec4(pos, 1.0);
}