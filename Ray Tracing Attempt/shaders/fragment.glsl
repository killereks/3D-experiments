#version 330 core
out vec4 FragColor;
  
in vec4 vertexColor; // the input variable from the vertex shader (same name and same type)
in vec2 pixelPos;

uniform float time;
uniform vec2 resolution;

uniform vec3 cameraPos;
uniform vec3 cameraFwd;
uniform vec3 cameraRight;

struct HitInfo {
    vec3 HitPoint;
    vec3 Normal;
    vec3 Color;
    bool Hit;
};

struct Sphere {
    vec3 Center;
    float Radius;
    vec3 Color;
};

Sphere spheres[3];

float SphereIntersect(vec3 origin, vec3 direction, Sphere sphere){
    vec3 oc = origin - sphere.Center;

    float a = dot(direction, direction);
    float b = 2.0 * dot(oc, direction);
    float c = dot(oc, oc) - sphere.Radius * sphere.Radius;

    float discriminant = b * b - 4.0 * a * c;

    if(discriminant < 0.0){
        return -1.0;
    }

    return (-b - sqrt(discriminant)) / (2.0 * a);
}

HitInfo TraceRay(vec3 origin, vec3 direction){
    HitInfo hitInfo;
    hitInfo.HitPoint = vec3(0.0);
    hitInfo.Normal = vec3(0.0);
    hitInfo.Color = vec3(0.0);
    hitInfo.Hit = false;

    float t = 0.0;
    float tMin = 100000.0;
    vec3 normal = vec3(0.0);

    for(int i = 0; i < spheres.length(); i++){
        t = SphereIntersect(origin, direction, spheres[i]);
        if(t > 0.0 && t < tMin){
            tMin = t;
            
            vec3 hitPoint = origin + direction * t;

            normal = normalize(hitPoint - spheres[i].Center);
            hitInfo.Color = spheres[i].Color;

            hitInfo.Hit = true;
        }
    }

    if(tMin < 100000.0){
        hitInfo.HitPoint = origin + direction * tMin;
        hitInfo.Normal = normal;

        hitInfo.Hit = true;
    }

    return hitInfo;
}

vec3 TraceRays(vec3 origin, vec3 direction){
    int bounces = 2;

    float multiplier = 0.7;

    vec3 color = vec3(0.0);

    vec3 lightPos = vec3(cos(time) * 5.0, 6.0, sin(time) * 5.0);
    
    for (int i = 0; i < bounces; i++){
        HitInfo hitInfo = TraceRay(origin, direction);
        
        if(!hitInfo.Hit){
            break;
        }

        vec3 lightDir = normalize(lightPos - hitInfo.HitPoint);

        // calculate shadow
        HitInfo shadowHitInfo = TraceRay(hitInfo.HitPoint, lightDir);
        if(shadowHitInfo.Hit){
            color *= 0.1;
            break;
        }

        float distance = length(lightPos - hitInfo.HitPoint);

        float attenuation = 1.0 / (distance * distance) * 10.0;

        color += dot(hitInfo.Normal, lightDir) * hitInfo.Color * attenuation * multiplier;

        origin = hitInfo.HitPoint;
        direction = reflect(direction, hitInfo.Normal);

        multiplier *= 0.3;
    }

    return color;
}

void main(){
    spheres[0].Center = vec3(0.0, 2.0, 6.0);
    spheres[0].Radius = 2.0;
    spheres[0].Color = vec3(1.0, 1.0, 1.0);

    spheres[1].Center = vec3(0.0, 3.0, 1.0);
    spheres[1].Radius = 0.5;
    spheres[1].Color = vec3(0.0, 0.0, 1.0);

    // sphere as a plane
    spheres[2].Center = vec3(0.0, -1000.5, 0.0);
    spheres[2].Radius = 1000.0;
    spheres[2].Color = vec3(1.0, 1.0, 1.0);

    vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);

    vec3 cameraUp = cross(cameraFwd, cameraRight);
    vec3 ro = cameraPos;
    vec3 rd = normalize(cameraFwd + cameraUp * pixelPos.y + cameraRight * pixelPos.x);

    vec3 color = TraceRays(ro, rd);

    FragColor = vec4(color, 1.0);
} 