#version 330 core
out vec4 FragColor;
  
in vec4 vertexColor; // the input variable from the vertex shader (same name and same type)
in vec2 pixelPos;

uniform float time;
uniform vec2 resolution;

struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
};

bool IntersectRaySphere(vec3 rayOrigin, vec3 rayDirection, Sphere sphere, out vec3 hitPoint){
    
    vec3 L = sphere.center - rayOrigin;
    float tca = dot(L, rayDirection);
    float d2 = dot(L, L) - tca * tca;

    if (d2 > sphere.radius * sphere.radius) return false;
    float thc = sqrt(sphere.radius * sphere.radius - d2);

    float t0 = tca - thc;
    float t1 = tca + thc;

    if (t0 < 0) t0 = t1;
    if (t0 < 0) return false;

    hitPoint = rayOrigin + rayDirection * t0;

    return true;
}

bool IntersectRayPlane(vec3 rayOrigin, vec3 rayDirection, vec3 planeNormal, vec3 planePoint, out vec3 hitPoint){
    float denom = dot(rayDirection, planeNormal);
    if (abs(denom) > 0.0001){
        vec3 p0l0 = planePoint - rayOrigin;
        float t = dot(p0l0, planeNormal) / denom;
        hitPoint = rayOrigin + rayDirection * t;
        return true;
    }
    return false;
}

Sphere CreateSphere(vec3 center, float radius, vec3 color){
    Sphere sphere;
    sphere.center = center;
    sphere.radius = radius;
    sphere.color = color;
    return sphere;
}

Sphere spheres[3];

void SetupSpheres(){
    vec3 pos = vec3(cos(time), 0, sin(time)) * 2.0;
    vec3 pos1 = vec3(cos(time + 0.3), sin(time + 0.3), 0) * 2.0;

    spheres[0] = CreateSphere(vec3(0, 0, 0), 1, vec3(1, 0, 0));
    spheres[1] = CreateSphere(pos, 0.5, vec3(0, 1, 0));
    spheres[2] = CreateSphere(pos1, 0.5, vec3(0, 0, 1));
}

vec3 CalculateLighting(vec3 baseColor, vec3 lightPos, vec3 lightColor, vec3 normal, vec3 hitPoint){
    float range = 10.0;
    
    vec3 lightDir = normalize(lightPos - hitPoint);
    float diffuse = max(dot(normal, lightDir), 0.0);
    float attenuation = 1.0 - (length(lightPos - hitPoint) / range);
    vec3 diffuseColor = baseColor * lightColor * diffuse * attenuation;
    return diffuseColor;
}

vec4 GetColor(int bounces, vec3 rayOrigin, vec3 rayDirection){
    if (bounces > 3) return vec4(0.1, 0.2, 0.3, 1.0);

    //vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);
    
    vec3 spherePos = vec3(0.0, 0.0, 1.0);
    float sphereRadius = 0.5;
    
    float closestDistance = 1000.0;
    vec3 closestHitPoint = vec3(0.0);
    vec3 closestColor = vec3(0.1, 0.2, 0.3);
    vec3 closestNormal = vec3(0.0);

    vec3 pointLightPos = vec3(2.0, 2.0, -2.0);
    vec3 pointLightColor = vec3(1.0, 1.0, 1.0);

    bool hitSomething = false;

    for (int i = 0; i < 3; i++){
        vec3 hitPoint;
        if (IntersectRaySphere(rayOrigin, rayDirection, spheres[i], hitPoint)){
            hitSomething = true;
            float distance = length(hitPoint - rayOrigin);
            if (distance < closestDistance){
                closestDistance = distance;
                closestHitPoint = hitPoint;
                closestNormal = normalize(hitPoint - spheres[i].center);
                closestColor = CalculateLighting(spheres[i].color, pointLightPos, pointLightColor, closestNormal, hitPoint);

                for (int j = 0; j < 3; j++){                
                    // shadow
                    vec3 shadowRay = normalize(pointLightPos - hitPoint);
                    vec3 shadowHitPoint;
                    if (IntersectRaySphere(hitPoint + shadowRay * 0.001, shadowRay, spheres[j], shadowHitPoint)){
                        closestColor *= 0.2;
                    }
                }
            }
        }
    }

    /*vec3 planeNormal = vec3(0.0, 1.0, 0.0);
    vec3 planePoint = vec3(0.0, -5.0, 0.0);
    vec3 hitPoint;
    if (IntersectRayPlane(rayOrigin, rayDirection, planeNormal, planePoint, hitPoint)){
        hitSomething = true;
        float distance = length(hitPoint - rayOrigin);
        if (distance < closestDistance){
            closestDistance = distance;
            closestHitPoint = hitPoint;
            closestNormal = normalize(planeNormal);
            closestColor = CalculateLighting(vec3(0.5, 0.5, 0.5), pointLightPos, pointLightColor, planeNormal, hitPoint);
        }
    }*/
    
    /*if (hitSomething){
        vec3 newRayOrigin = closestHitPoint + closestNormal * 0.001;
        vec3 newRayDirection = reflect(rayDirection, closestNormal);
        return vec4(closestColor, 1.0) + GetColor(bounces + 1, newRayOrigin, newRayDirection);
    }*/

    return vec4(closestColor, 1.0);
}

void main(){
    SetupSpheres();
    
    vec3 rayOrigin = vec3(0.0, 0.0, -3.0);
    vec3 rayDirection = normalize(vec3(pixelPos.x, pixelPos.y, 1.0));

    FragColor = GetColor(0, rayOrigin, rayDirection);
} 