attribute vec3 aSourcePos;
attribute vec3 aTargetPos;
attribute float aDistance;
attribute float aSeed;

uniform float uMorph;
uniform float uTime;

varying float vPulse;
varying float vDist;

void main() {
  vec3 pos = mix(aSourcePos, aTargetPos, uMorph);

  vec4 worldPos = instanceMatrix * vec4(pos, 1.0);
  vDist = aDistance;
  vPulse = aSeed;

  vec4 mvPos = viewMatrix * worldPos;
  gl_Position = projectionMatrix * mvPos;
}
