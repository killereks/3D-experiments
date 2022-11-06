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

in vec2 Position;
in vec4 FragPosLightSpace;

out vec4 FragColor;

float lineariseDepth(float depth){
    float near = 0.1;
    float far = 100.0;
    return (2.0 * near * far) / (far + near - (depth * 2.0 - 1.0) * (far - near));
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

float inShadow(){
    float bias = 0.005;
    vec3 pos = FragPosLightSpace.xyz * 0.5 + 0.5;
    float depth = texture(shadowMap, pos.xy).r;
    return depth + bias < pos.z ? 0.0 : 1.0;
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

void main(){
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
    color = ACES(color);

    color = Vignette(color, TexCoords);

    FragColor = vec4(color, 1.0);
}