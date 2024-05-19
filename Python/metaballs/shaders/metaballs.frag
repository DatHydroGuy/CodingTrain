#version 130
precision highp float;
uniform vec3 metaballs[15];
const float WIDTH = 800.0;
const float HEIGHT = 600.0;

void main()
{
    float x = gl_FragCoord.x;
    float y = gl_FragCoord.y;
    float v = 0.0;
    for (int i = 0; i < 15; i++) {
        vec3 mb = metaballs[i];
        float dx = mb.x - x;
        float dy = mb.y - y;
        float r = mb.z;
        v += r * r / (dx * dx + dy * dy);
        if (v > 15.0) {
            gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
        } else if (v > 5.0) {
            gl_FragColor = vec4(1.0, 1.0, 0.0, 1.0);
        } else if (v > 2.0) {
            gl_FragColor = vec4(1.0, 0.5, 0.0, 1.0);
        } else if (v > 1.0) {
            gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        } else {
            gl_FragColor = vec4(v, 0.0, 0.0, 1.0);
        }
    }
}
