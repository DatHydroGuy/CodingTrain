#version 130
precision highp float;
uniform float screen_width;
uniform float screen_height;

float map(float value, float min1, float max1, float min2, float max2) {
  return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

void main(void) {
    const float scale = 12.0;
    float aspect = screen_height / screen_width;
    float scaled_x = map(gl_FragCoord.x, 0, screen_width, -0.5, 0.5);
    float scaled_y = map(gl_FragCoord.y, 0, screen_height, -0.5 * aspect, 0.5 * aspect);
    vec2 v = scale * vec2(scaled_x, scaled_y);
    const vec2 p = vec2(4.0, 3.0);
    float alpha = 0.0;
    vec2 g;

    float n = 0.5 + 0.5 * psrdnoise(v, p, alpha, g);
    vec3 ncolor = vec3(n);
    gl_FragColor = vec4(ncolor, 1.0);
}