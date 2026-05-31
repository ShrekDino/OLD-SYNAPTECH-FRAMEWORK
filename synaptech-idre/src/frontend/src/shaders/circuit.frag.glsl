uniform float uTime;
uniform float uOpacity;

varying float vPulse;
varying float vDist;

void main() {
  float pulse = 0.5 + 0.5 * sin(uTime * 2.0 + vPulse * 6.28);
  float thickness = 0.3 + 0.7 * pulse;

  vec3 techBlue = vec3(0.161, 0.475, 1.0);
  vec3 circuitGold = vec3(1.0, 0.702, 0.0);
  vec3 color = mix(techBlue, circuitGold, pulse * 0.6);

  float alpha = uOpacity * (0.15 + 0.45 * pulse);
  alpha *= smoothstep(0.0, 0.5, thickness);

  gl_FragColor = vec4(color, alpha);
}
