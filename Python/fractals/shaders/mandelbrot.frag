#version 130
precision highp float;
uniform float screen_width;
uniform float screen_height;
uniform vec3 colour_map[193];

float my_abs(float x) {
    return (x < 0.0)? -x : x;
}

float map(float value, float min1, float max1, float min2, float max2) {
  return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

void main()
{
    const int max_iterations = 100;
    const float threshold = 16.0;
    int num_iterations = 0;
    float col = 0.0;

    float z_real = 2.0 * (gl_FragCoord.x / screen_width * 2 - 1) - 0.5;
    float z_imag = 1.5 * (gl_FragCoord.y / screen_height * 2 - 1);

    float c_real = z_real;
    float c_imag = z_imag;

    while (num_iterations < max_iterations) {
        float z_squared_real = z_real * z_real - z_imag * z_imag;
        float z_squared_imag = 2 * z_real * z_imag;

        z_real = z_squared_real + c_real;
        z_imag = z_squared_imag + c_imag;

        if (my_abs(z_real + z_imag) > threshold) {
            break;
        }

        num_iterations += 1;
    }

    if (num_iterations == max_iterations) {
        gl_FragColor = vec4(vec3(0.0), 1.0);
    } else {
        float temp = map(num_iterations, 0, max_iterations, 0, 1);
        int index = int(temp * colour_map.length() * 3);
        vec3 col_vec = vec3(colour_map[index]);
        gl_FragColor = vec4(col_vec[0], col_vec[1], col_vec[2], 1.0);
    }
}
