#version 330 core
out vec4 FragColor;
 
in vec4 vertexColor; // the input variable from the vertex shader (same name and same type)
in vec2 pixelPos;

uniform float time;
uniform vec2 resolution;

uniform vec3 cameraPos;
uniform vec3 cameraFwd;
uniform vec3 cameraRight;

#define MAX_STEPS 150
#define MAX_DIST 1000.
#define SURF_DIST 0.01

mat4 rotationX( in float angle ) {
    return mat4(1.0, 0, 0, 0,
                0, cos(angle), -sin(angle), 0,
                0, sin(angle),  cos(angle), 0,
                0, 0, 0, 1);
}

mat4 rotationY( in float angle ) {
    return mat4(1.0,  0,  0,  0,
                0, cos(angle), -sin(angle), 0,
                0, sin(angle), cos(angle), 0,
                0, 0, 0, 1);
}

float sdBox(vec3 pt, vec3 b) {
    vec3 box = abs(pt) - b;
    return length(max(box, 0.0)) + min(max(box.x, max(box.y, box.z)), 0.0);
}

float DE(vec3 pos){
    int Iterations = 128;
    float bailout = 3;
    float power = 1 * time * 0.5;

    vec3 z = pos;
    float dr = 1.0;
    float r = 1.0;

    for (int i = 0; i < Iterations; i++){
        r = length(z);
        if (r > bailout) break;

        float theta = acos(z.z/r);
        float phi = atan(z.y,z.x);
        dr = pow(r, power-1.0) * power * dr + 1.0;

        float zr = pow(r, power);
        theta = theta * power;
        phi = phi * power;

        z = zr * vec3(sin(theta)*cos(phi), sin(phi)*sin(theta),cos(theta));
        z += pos;
    }

    return 0.5 * log(r) * r/dr;
}

float sierpinskiPyramidFold(vec3 pt) {
    float r;
    float offset = 1.;
    float scale = 2.;
    pt.y -= 2.5;
    int n = 0;
    while(n < 15) {
        if(pt.x + pt.y < 0.) pt.xy = -pt.yx;
        if(pt.x + pt.z < 0.) pt.xz = -pt.zx;
        if(pt.y + pt.z < 0.) pt.zy = -pt.yz;
        pt = pt * scale - offset*(scale - 1.0);
        n++;
    }
   
    return (length(pt) * pow(scale, -float(n)));
}

float mengerSponge(vec3 pt) {
    float scale = 1.0;
    float offset = -2.;
    float iterations = 4;

    float dist = sdBox(vec3(pt.x, pt.y+offset, pt.z), vec3(scale));
   
    float s = 1.;
   
    float da, db, dc;
   
    for(int i = 0; i < 4; i++) {
        vec3 a = mod(pt * s, 2.0) - 1.0;
        s *= iterations;
        vec3 r = abs(1.0 - 3.0*abs(a));
       
        da = max(r.x, r.y);
        db = max(r.y, r.z);
        dc = max(r.z, r.x);
       
        float c = (min(da, min(db, dc)) - 1.) / s;
        if ( c > dist) dist = c;
    }
   
    return dist;
}

float alteredMenger(vec3 pt){
    float scale = 1.0;
    float offset = -2.;
    float iterations = 3.;

    float dist = sdBox(vec3(pt.x, pt.y+offset, pt.z), vec3(scale));
   
    float s = 2.;
   
    float da, db, dc;
   
    for(int i = 0; i < 4; i++) {
        vec3 a = mod(pt * s, 2.0) - 1.0;
        s *= iterations;
        vec3 r = abs(1.0 - 3.0*abs(a));
       
        r = (vec4(r, 1.0) * rotationX(20.)).xyz;
        da = max(r.x+1.5, r.y);
        r = (vec4(r, 1.0) * rotationY(80.)).xyz;
       
        da = max(da + r.x-0.5, r.y);
        db = max(r.y, r.z);
        dc = max(r.z+0.5, r.x);
       
        float c = (min(da, min(db, dc)) - 1.) / s;
        if ( c > dist) dist = c;
    }
   
    return dist;
}

float sierpinskiPyramid(vec3 pt){
    vec3 ori = vec3(0, 2.5, 0);
    vec3 a1 = vec3(1,1,1)+ori;
    vec3 a2 = vec3(-1,-1,1)+ori;
    vec3 a3 = vec3(1,-1,-1)+ori;
    vec3 a4 = vec3(-1,1,-1)+ori;

    vec3 c;
    int n = 0;
    float dist, d;
    float scale = 2.;
    while (n < 16){
        c = a1;
        dist = length(pt - a1);
        d = length(pt - a2);
        if (d < dist){
            c = a2;
            dist = d;
        }
        d = length(pt - a3);
        if (d < dist){
            c = a3;
            dist = d;
        }
        d = length(pt - a4);
        if (d < dist){
            c = a4;
            dist = d;
        }
        pt = scale * pt - c * (scale - 1.);
        n++;
    }

    return length(pt) * pow(scale, float(-n));
}

mat4 rotationMatrix(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
   
    return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                0.0,                                0.0,                                0.0,                                1.0);
}

vec3 rotatePt(vec3 pt, vec3 axis, float angle) {
    mat4 m = rotationMatrix(axis, angle);
    return (m * vec4(pt, 1.0)).xyz;
}

float evolvingFractal(vec3 pt) {
    //vec3 off = vec3(0.7, 0.5, 0.15);
    //vec3 off = vec3(0.5, 0.85, 1.25);
    vec3 off = vec3(1.);
    float scale = 2.;
    pt.y -= 2.5;
    int n = 0;

    while(n < 8) {
        //pt = rotatePt(pt, vec3(1.), 31.); // snowflake
        pt = rotatePt(pt, vec3(1), cos(10.+time*0.1));
       
        pt = abs(pt); // for cube
       
        if(pt.x + pt.y < 0.) pt.xy = -pt.yx;
        if(pt.x + pt.z < 0.) pt.xz = -pt.zx;
        if(pt.y + pt.z < 0.) pt.zy = -pt.yz;
         
        pt = rotatePt(pt, vec3(0.35,0.2,0.3), -90.+time*0.1);
       
        pt.x = pt.x * scale - off.x*(scale - 1.0);
        pt.y = pt.y * scale - off.y*(scale - 1.0);
        pt.z = pt.z * scale - off.z*(scale - 1.0);
       
        pt = rotatePt(pt, vec3(0.3,0.1,0.25), -70.+time*0.1);
       
        n++;
    }
    return (length(pt) * pow(scale, -float(n)));
}

float evolvingFractal2(vec3 pt) {
    vec3 off = vec3(1.25);
    float scale = 2.;
    pt.y -= 2.5;
    int n = 0;

    while(n < 10) {
        //pt = rotatePt(pt, vec3(1.), 31.); // snowflake
        pt = rotatePt(pt, vec3(1.), sin(0.+time*0.1));
       
        pt = abs(pt); // for cube
       
        if(pt.x + pt.y < 0.) pt.xy = -pt.yx;
        if(pt.x + pt.z < 0.) pt.xz = -pt.zx;
        if(pt.y + pt.z < 0.) pt.zy = -pt.yz;
         
        pt = rotatePt(pt, vec3(0.35,0.2,0.3), -90.+time*0.1);
       
        pt.x = pt.x * scale - off.x*(scale - 1.0);
        pt.y = pt.y * scale - off.y*(scale - 1.0);
        pt.z = pt.z * scale - off.z*(scale - 1.0);
       
        pt = rotatePt(pt, vec3(0.3,0.1,0.25), -70.+time*0.1);
       
        n++;
    }
    return (length(pt) * pow(scale, -float(n)));
}

float random31(vec3 st) {
    return fract(sin(dot(st, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

float smin(float a, float b, float k){
    // polynomial mixing
    float h = clamp(0.5 + 0.5 * (b-a)/k, 0.0, 1.0);
    return mix(b,a,h) - k*h*(1.0 - h);
}

float GetDist(vec3 p){
    float spacing = 15.0;
    vec4 s = vec4(0, 1, 6, 1.5);
   
    float planeDist = p.y + 3.0;

    //p = mod(p, spacing) - vec3(spacing * 0.5);

    float frequency = 3;
    float offset = time * 3;

    float displacement = sin(frequency * p.x + offset) * sin(frequency * p.y + offset) * sin(frequency * p.z + offset) * 0.25;
    
    float sphereDist = length(p - s.xyz) - s.w + displacement;
    float boxDist = sdBox(p - vec3(0.0, 10.0, 6.0), vec3(1.0, 1.0, 1.0));

    //float d = min(sphereDist, planeDist);
    //return min(sphereDist, planeDist);
    float repeatedSphereDist = length(p) - 4.0 + displacement;
    
    //return min(sphereDist, planeDist);

    //return min(smin(sphereDist, boxDist, 32), planeDist);
    return min(smin(sphereDist, boxDist - 0.2, time), planeDist);
   
    //return repeatedSphereDist;
    //return min(planeDist, evolvingFractal(p));
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
    vec3 lightPos = vec3(0, 5, -6);
    lightPos.xz += vec2(sin(time), cos(time)) * 2;
    vec3 l = normalize(lightPos - p);
    vec3 n = GetNormal(p);

    float dif = clamp(dot(n, l), 0., 1.);

    float d = RayMarch(p+n*SURF_DIST*3, l);
    // in shadow
    if (d < length(lightPos - p)) dif *= 0.1;

    float specular = 0.0;
    if (dif > 0.0){
        vec3 r = reflect(-l, n);
        specular = pow(clamp(dot(r, normalize(-cameraFwd)), 0.0, 1.0), 32.0);
    }

    return dif + specular;
}

vec3 GetColor(float t){
    return mix(vec3(0.5, 0.6, 0.7), vec3(0.8, 0.6, 0.3), t);
}

void main(){
    vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);

    vec3 cameraUp = cross(cameraFwd, cameraRight);

    vec3 ro = cameraPos;
    vec3 rd = normalize(cameraFwd + cameraUp * pixelPos.y + cameraRight * pixelPos.x);

    vec3 col = vec3(0.1, 0.2, 0.3);

    float d = RayMarch(ro, rd);
    if (d < MAX_DIST){
        vec3 p = ro + rd * d;
       
        float dif = GetLight(p);
        vec3 normal = GetNormal(p);

        vec3 materialColor = GetColor(length(p) / 10.0);

        col = materialColor * dif;
    }
    FragColor = vec4(col, 1.0);
}