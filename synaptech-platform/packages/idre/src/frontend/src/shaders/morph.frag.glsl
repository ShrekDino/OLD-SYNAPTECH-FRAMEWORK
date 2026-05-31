varying vec3 vColor;
varying float vMorphAmount;
varying float vSeed;

uniform float uTime;

void main() {
  vec2 center = gl_PointCoord - vec2(0.5);
  float dist = length(center);
  if (dist > 0.5) discard;

  float softness = 1.0 - smoothstep(0.0, 0.5, dist);
  float glow = softness * (0.6 + 0.4 * vMorphAmount);
  float ripple = 0.5 + 0.5 * sin(uTime * 3.0 + vSeed * 6.28);

  vec3 goldGlow = vec3(1.0, 0.702, 0.0) * glow * 0.5 * ripple;
  vec3 color = vColor + goldGlow;
  float alpha = glow * 0.85;

  gl_FragColor = vec4(color, alpha);
}
