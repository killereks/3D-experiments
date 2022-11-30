#version 330 core

in vec3 Position;

in vec3 Normal;
in vec2 TexCoord;

uniform vec3 sunPos;
uniform vec3 sunDir;

uniform vec3 camPos;
uniform vec3 camFwd;

uniform sampler2D albedo;
uniform samplerCube _Skybox;
uniform sampler2D heightMap;

out vec4 FragColor;

void main(){
    float diffuse = max(dot(Normal, normalize(-sunDir)), 0.0);

    // shallow = 84e4f1
    // deep = 246189
    vec3 shallow = vec3(0.52, 0.89, 0.94);
    vec3 deep = vec3(0.14, 0.38, 0.53);

    vec3 viewDir = normalize(camPos - Position);
    // refract water and use albedo as color
    //vec3 refracted = refract(viewDir, Normal, 1.33);
    //vec3 color = texture(albedo, refracted.xy * 0.5 + 0.5).rgb;

    // reflect skybox
    vec3 reflected = reflect(viewDir, Normal);
    vec3 skybox = texture(_Skybox, reflected).rgb;

    // mix colors
    vec3 finalColor = mix(shallow, deep, diffuse);
    finalColor = mix(finalColor, skybox, 0.2);

    // refract sun direction vector with normal
    vec3 sunDirRefracted = refract(sunDir, Normal, 1.33);
    // get height from heightmap
    float height = texture(heightMap, TexCoord).r;

    vec3 samplePoint = sunDirRefracted * height + Position;
    vec3 groundColor = texture(albedo, samplePoint.xy).rgb;

    finalColor = mix(finalColor, groundColor, 0.5);

    //vec3 dir = normalize(sunPos - Position);
    // refract and apply color of the albedo
    //vec3 refractDir = refract(dir, Normal, 1.0/1.33);
    //vec3 refractColor = texture(albedo, refractDir.xy * 0.5 + 0.5).rgb;

    // specular with sun and camera
    //vec3 viewDir = normalize(camPos - Position);
    //vec3 reflectDir = reflect(-dir, Normal);
    //float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);

    //vec3 color = deep * refractColor * diffuse;// + spec * refractColor;

    FragColor = vec4(finalColor, 0.4);
}