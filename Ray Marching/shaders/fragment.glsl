#version 330 core
out vec4 FragColor;
  
in vec4 vertexColor; // the input variable from the vertex shader (same name and same type)
in vec2 pixelPos;

uniform float time;
uniform vec2 resolution;
uniform vec3 cameraPos;
uniform vec3 cameraDir;

#define MAX_STEPS 100
#define MAX_DIST 100.
#define SURF_DIST 0.01

float GetDist(vec3 p){
    vec4 s = vec4(0, 1, 6, 1.5);

    float displacement = sin(5.0 * p.x) * sin(5.0 * p.y) * sin(5.0 * p.z) * time * 0.1;
    float sphereDist = length(p - s.xyz) - s.w + displacement;

    float planeDist = p.y + sin(p.x) * sin(p.z) * 0.1;

    float d = min(sphereDist, planeDist);
    return d;
}

float RayMarch(vec3 ro, vec3 rd){
    float dO = 0;

    for (int i = 0; i < MAX_STEPS; i++){
        vec3 p = ro + rd * dO;
        float dS = GetDist(p);
        dO += dS;

        if (dO > MAX_DIST || dS < SURF_DIST) break;
    }

    return dO;
}

vec3 GetNormal(vec3 p){
    float d = GetDist(p);
    vec2 e = vec2(0.01, 0);

    vec3 n = d - vec3(
        GetDist(p - e.xyy),
        GetDist(p - e.yxy),
        GetDist(p - e.yyx)
    );

    return normalize(n);
}

float GetLight(vec3 p){
    vec3 lightPos = vec3(0, 5, 6);
    lightPos.xz += vec2(sin(time), cos(time)) * 2;
    vec3 l = normalize(lightPos - p);
    vec3 n = GetNormal(p);

    float dif = clamp(dot(n, l), 0., 1.);

    float d = RayMarch(p+n*SURF_DIST*2, l);
    if (d < length(lightPos - p)) dif *= 0.1;

    return dif;
}

void main(){
    vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);
    
    vec3 ro = cameraPos;
    vec3 rd = normalize(cameraDir + vec3(pixelPos.x, pixelPos.y, 0));
    //vec3 rd = normalize(vec3(uv.x, uv.y, 1));

    vec3 col = vec3(0.1, 0.2, 0.3);

    float d = RayMarch(ro, rd);
    if (d < MAX_DIST){
        vec3 p = ro + rd * d;
        
        float dif = GetLight(p);

        col = vec3(dif);
    }
    FragColor = vec4(col, 1.0);
} 