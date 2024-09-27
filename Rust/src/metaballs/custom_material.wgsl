#import bevy_shader_utils::perlin_noise_2d

const NUM_METABALLS: i32 = 10;
const WHITE: f32 = 12.0;
const YELLOW: f32 = 5.0;
const RED: f32 = 2.0;
const BLACK: f32 = 0.2;

@group(2) @binding(0)
var<uniform> pos_and_radius: array<vec3<f32>, NUM_METABALLS>;

@fragment
fn fragment(
    @builtin(position) coord: vec4<f32>,
    @location(0) world_position: vec4<f32>,
    @location(1) normals: vec3<f32>,
    @location(2) uv: vec2<f32>
    ) -> @location(0) vec4<f32> {
        var threshold = 0.0;
        for (var i = 0; i < NUM_METABALLS; i++) {
            var metaball: vec3<f32> = pos_and_radius[i];
            var dx = metaball.x - uv.x;
            var dy = metaball.y - uv.y;
            var r = metaball.z;
            threshold += r * r / (dx * dx + dy * dy);
        }
        if (threshold > WHITE) {
            return vec4<f32>(1.0, 1.0, 1.0, 1.0);
        } else if (threshold > YELLOW) {
            var blue = smoothstep(YELLOW, WHITE, threshold);
            return vec4<f32>(1.0, 1.0, blue, 1.0);
        } else if (threshold > RED) {
            var green = smoothstep(RED, YELLOW, threshold);
            return vec4<f32>(1.0, green, 0.0, 1.0);
        } else if (threshold > BLACK) {
            var red = smoothstep(BLACK, RED, threshold);
            return vec4<f32>(red, 0.0, 0.0, 1.0);
        } else {
            return vec4<f32>(0.0, 0.0, 0.0, 1.0);
        }
    }
