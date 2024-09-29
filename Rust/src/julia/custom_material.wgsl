#import bevy_shader_utils::perlin_noise_2d

const NUM_COLOURS: i32 = 193;
const MAX_ITERATIONS: i32 = 100;
const SCREEN_WIDTH: f32 = 1200.0;
const SCREEN_HEIGHT: f32 = 900.0;
const THRESHOLD: f32 = 16.0;
const REAL_MIN: f32 = -2.0;
const REAL_MAX: f32 = 2.0;
const IMAG_MIN: f32 = -1.5;
const IMAG_MAX: f32 = 1.5;

@group(2) @binding(0)
var<uniform> colour_map: array<vec3<f32>, NUM_COLOURS>;
@group(2) @binding(1)
var<uniform> colour_offset: i32;
@group(2) @binding(2)
var<uniform> mouse_pos: vec2<f32>;

fn my_abs(x: f32) -> f32 {
    if x < 0.0 {
        return -x;
    } else {
        return x;
    }
}

fn map(value: f32, min1: f32, max1: f32, min2: f32, max2: f32) -> f32 {
  return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

@fragment
fn fragment(
    @builtin(position) coord: vec4<f32>,
    @location(0) world_position: vec4<f32>,
    @location(1) normals: vec3<f32>,
    @location(2) uv: vec2<f32>
    ) -> @location(0) vec4<f32> {
        var num_iterations = 0;
        var col = 0.0;

        var z_real = map(uv.x, 0.0, 1.0, REAL_MIN, REAL_MAX);
        var z_imag = map(uv.y, 0.0, 1.0, IMAG_MIN, IMAG_MAX);

        var c_real = mouse_pos.x;
        var c_imag = mouse_pos.y;

        while (num_iterations < MAX_ITERATIONS) {
            var z_squared_real = z_real * z_real - z_imag * z_imag;
            var z_squared_imag = 2 * z_real * z_imag;

            z_real = z_squared_real + c_real;
            z_imag = z_squared_imag + c_imag;

            if (my_abs(z_real + z_imag) > THRESHOLD) {
                break;
            }

            num_iterations += 1;
        }

        if (num_iterations == MAX_ITERATIONS) {
            return vec4<f32>(vec3(0.0), 1.0);
        } else {
            var temp = map(f32(num_iterations), 0.0, f32(MAX_ITERATIONS), 0.0, 1.0);
            var index = i32(temp * f32(NUM_COLOURS)) + colour_offset;
            index %= NUM_COLOURS;
            var col_vec = vec3(colour_map[index]);
            return vec4<f32>(col_vec[0], col_vec[1], col_vec[2], 1.0);
        }
    }
