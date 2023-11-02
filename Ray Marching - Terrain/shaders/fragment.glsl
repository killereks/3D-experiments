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
#define MAX_DIST 2000.
#define SURF_DIST 0.01

#define PI 3.14159265359

float rand(vec2 c){
	return fract(sin(dot(c.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float noise(vec2 p, float freq ){
	float unit = 1920/freq;
	vec2 ij = floor(p/unit);
	vec2 xy = mod(p,unit)/unit;
	//xy = 3.*xy*xy-2.*xy*xy*xy;
	xy = .5*(1.-cos(PI*xy));
	float a = rand((ij+vec2(0.,0.)));
	float b = rand((ij+vec2(1.,0.)));
	float c = rand((ij+vec2(0.,1.)));
	float d = rand((ij+vec2(1.,1.)));
	float x1 = mix(a, b, xy.x);
	float x2 = mix(c, d, xy.x);
	return mix(x1, x2, xy.y);
}

float pNoise(vec2 p, int res){
	float persistance = .5;
	float n = 0.;
	float normK = 0.;
	float f = 4.;
	float amp = 1.;
	int iCount = 0;
	for (int i = 0; i<50; i++){
		n+=amp*noise(p, f);
		f*=2.;
		normK+=amp;
		amp*=persistance;
		if (iCount == res) break;
		iCount++;
	}
	float nf = n/normK;
	return nf*nf*nf*nf;
}

float distSphere(vec3 p, float r){
    return length(p) - r;
}

float distBoxFrame(vec3 p, vec3 b, float e){
    p = abs(p  )-b;
    vec3 q = abs(p+e)-e;
    return min(min(
        length(max(vec3(p.x,q.y,q.z),0.0))+min(max(p.x,max(q.y,q.z)),0.0),
        length(max(vec3(q.x,p.y,q.z),0.0))+min(max(q.x,max(p.y,q.z)),0.0)),
        length(max(vec3(q.x,q.y,p.z),0.0))+min(max(q.x,max(q.y,p.z)),0.0));
}

float GetDist(vec3 p){
    
    float height = pNoise(p.xz, 32) * 1000.0;
    
    // plane at y = -200
    float planeDist = p.y + 200.0;

    // create ground
    return min(p.y + height, planeDist);
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
    vec2 e = vec2(0.001, 0);

    vec3 n = d - vec3(
        GetDist(p - e.xyy),
        GetDist(p - e.yxy),
        GetDist(p - e.yyx)
    );

    return normalize(n);
}

float softshadow( in vec3 ro, in vec3 rd, float mint, float maxt, float w )
{
    float res = 1.0;
    float ph = 1e20;
    float t = mint;
    for( int i=0; i<512 && t<maxt; i++ )
    {
        float h = GetDist(ro + rd*t);
        if( h<0.001 )
            return 0.0;
        float y = h*h/(2.0*ph);
        float d = sqrt(h*h-y*y);
        res = min( res, d/(w*max(0.0,t-y)) );
        ph = h;
        t += h;
    }
    return res;
}

void main(){
    vec2 uv = vec2((pixelPos.x + 1.0) / 2.0, (pixelPos.y + 1.0) / 2.0);

    vec3 cameraUp = cross(cameraFwd, cameraRight);

    vec3 ro = cameraPos;
    vec3 rd = normalize(cameraFwd + cameraUp * pixelPos.y + cameraRight * pixelPos.x);

    vec3 lightDir = normalize(vec3(1.0, 1.0, 0.0));

    vec3 col = vec3(0.0, 0.0, 0.0);
    float d = RayMarch(ro, rd);

    if (d < MAX_DIST){
        vec3 p = ro + rd * d;
        
        vec3 normal = GetNormal(p);
        float diff = max(dot(normal, lightDir), 0.0);

        diff = max(diff, 0.5);

        float shadow = softshadow(p, lightDir, 0.01, 10.0, 0.5);

        float deviation = noise(p.xz, 3.0);

        // colour based on normal
        // we want grass and rocks
        if (normal.y > 0.5){
            col = vec3(0.3, 1.0, 0.2) * diff * shadow * deviation;
        } else {
            col = vec3(0.5, 0.5, 0.5) * diff * shadow * deviation;
        }

        if (p.y < -199.0){
            col = vec3(0.2, 0.2, 0.7) * diff * shadow * deviation;
        }

        rd = reflect(rd, normal);
        ro = p + normal * 0.1;
    }

    
    FragColor = vec4(col, 1.0);
}