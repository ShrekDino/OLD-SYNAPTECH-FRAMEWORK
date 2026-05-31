attribute vec3 aFractalPos;
attribute vec3 aNeuronPos;
attribute float aSeed;

uniform float uMorph;
uniform float uTime;
uniform float uJitterIntensity;

varying vec3 vColor;
varying float vMorphAmount;
varying float vSeed;

void main() {
  float jitter = (1.0 - uMorph) * uJitterIntensity;
  float ax = uTime * 1.7 + aSeed * 13.37;
  float ay = uTime * 2.1 + aSeed * 7.11;
  vec3 jitterOffset = vec3(
    sin(ax) * jitter,
    cos(ay) * jitter,
    sin(ax + ay) * jitter * 0.7
  );

  vec3 pos = mix(aFractalPos, aNeuronPos, uMorph) + jitterOffset;

  vec4 worldPos = instanceMatrix * vec4(pos, 1.0);
  vec4 mvPos = viewMatrix * worldPos;

  vec3 techBlue = vec3(0.161, 0.475, 1.0);
  vec3 circuitGold = vec3(1.0, 0.702, 0.0);
  vColor = mix(techBlue, circuitGold, uMorph * 0.3);
  vMorphAmount = uMorph;
  vSeed = aSeed;

  gl_Position = projectionMatrix * mvPos;
  gl_PointSize = 2.5 + uMorph * 2.0;
}
