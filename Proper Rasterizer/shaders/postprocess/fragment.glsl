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

uniform float time;

in vec2 Position;

out vec4 color;

float lineariseDepth(float depth){
    float near = 0.1;
    float far = 100.0;
    return (2.0 * near * far) / (far + near - (depth * 2.0 - 1.0) * (far - near));
}

void main(){
    vec2 TexCoords = Position * 0.5 + 0.5;
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
    
    /*float intensity = 0.0;
    float radius = 0.1;
    float amount = 0.1;
    float decay = 0.9;
    float density = 0.9;
    float weight = 0.0;
    float illuminationDecay = 1.0;
    vec3 lightVector = normalize(lightPos - camPos);
    vec3 sampleRay = lightVector;
    vec3 samplePos = camPos;
    for(int i = 0; i < 100; i++){
        float depth = texture(shadowMap, samplePos.xy).r;
        float illumination = 1.0 - smoothstep(0.0, 1.0, depth - samplePos.z);
        illumination *= illuminationDecay;
        illuminationDecay *= decay;
        weight += (density * illumination);
        samplePos += sampleRay * radius;
    }
    intensity = weight * amount;

    vec3 pixelColor = texture(screenTexture, TexCoords).rgb;
    color = vec4(pixelColor + intensity, 1.0);*/

    float depth = lineariseDepth(texture(cameraDepthMap, TexCoords).r);
    
    // apply fog based on depth
    float fogAmount = 0.1;
    float fogDensity = 0.1;
    float fog = 1.0 - exp(-depth * fogDensity);
    fog = clamp(fog, 0.0, 1.0);
    fog = smoothstep(0.0, 1.0, fog);
    fog = fog * fogAmount;

    vec3 albedo = texture(screenTexture, TexCoords).rgb;
    color = vec4(albedo + fog, 1.0);
}