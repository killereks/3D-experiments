#version 330 core
out vec4 FragColor;
  
in vec4 vertexColor; // the input variable from the vertex shader (same name and same type)
in vec2 pixelPos;

uniform float time;
uniform vec2 resolution;
uniform vec3 cameraPos;
uniform vec3 cameraDir;

struct Sphere {
    vec3 color;
    vec3 position;
    float radius;
} sphere;

struct Light {
    vec3 direction;
} light;

struct Material {
    float diffuse;
    float ambience;
    float specular;
    float shininess;
} material;

void setupScene(){
    sphere.position = vec3(0.0, 0.0, 0.0);
    sphere.radius = 0.3;
    sphere.color = vec3(0.9, 0.2, 0.1);

    light.direction = normalize(vec3(-1, -1, 1));

    material.ambience = 0.2;
    material.diffuse = 0.7;
    material.specular = 0.5;
    material.shininess = 10.0;
}

bool solveQuadratic(float a, float b, float c, out float t0, out float t1){
    float delta = b * b - 4 * a * c;
    if(delta < 0.0) return false;
    t0 = (-b - sqrt(delta)) / (2.0 * a);
    t1 = (-b + sqrt(delta)) / (2.0 * a);
    return true;
}

bool intersect(vec3 direction, out vec3 surfaceNormal){
    vec3 L = cameraPos - sphere.position;

    float a = dot(direction, direction);
    float b = 2.0 * dot(L, direction);
    float c = dot(L, L) - sphere.radius * sphere.radius;

    float t0;
    float t1;

    if (solveQuadratic(a, b, c, t0, t1)){
        float t = t0;
        if (t1 < t0){
            t = t1;
        }

        vec3 pointHit = cameraPos + t * direction;
        surfaceNormal = normalize(pointHit - sphere.position);

        return true;
    }

    return false;
}

vec3 rayTrace(vec3 direction){
    vec3 surfaceNormal;

    if (intersect(direction, surfaceNormal)){
        float coeff = -dot(light.direction, surfaceNormal);

        vec3 ambient = material.ambience * sphere.color;
        vec3 diffuse = material.diffuse * max(coeff, 0) * sphere.color;

        float shininessInfluence = -dot(direction, reflect(light.direction, surfaceNormal));
        float shininess = pow(max(shininessInfluence, 0), material.shininess);
        vec3 specular = material.specular * shininess * sphere.color;

        return ambient + diffuse + specular;
    }
    return vec3(0.1, 0.2, 0.3);
}

void main(){
    setupScene();

    vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);

    vec3 rayDirection = normalize(cameraDir + vec3(pixelPos.x, pixelPos.y, 1.0));

    vec3 col = rayTrace(rayDirection);

    FragColor = vec4(col, 1.0);
} 