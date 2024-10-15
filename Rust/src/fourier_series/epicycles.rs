use bevy::prelude::*;
use bevy_vector_shapes::prelude::*;
use std::collections::VecDeque;
use std::f32::consts::PI;

const MARKER_SIZE: f32 = 5.0;
const NUM_TERMS: i32 = 20;

enum WaveType {
    Square,
    Saw,
}

const WAVE_TYPE: WaveType = WaveType::Square; // Change this between Square and Saw

#[derive(Component)]
pub struct Trace {
    pub points: VecDeque<f32>,
    pub length: usize,
}

impl Trace {
    fn new(num_points: usize) -> Self {
        Trace {
            points: VecDeque::new(),
            length: num_points,
        }
    }

    pub fn push(&mut self, point: f32) {
        self.points.push_front(point);
        if self.points.len() > self.length {
            self.points.pop_back();
        }
    }
}

#[derive(Component)]
pub struct Epicycle {
    x: f32,
    y: f32,
    radius: f32,
}

impl Default for Epicycle {
    fn default() -> Self {
        Epicycle {
            x: 0.0,
            y: 0.0,
            radius: 0.0,
        }
    }
}

impl Epicycle {
    pub fn new(x: f32, y: f32, radius: f32) -> Self {
        Epicycle { x, y, radius }
    }
}

pub struct EpicyclesPlugin;

impl Plugin for EpicyclesPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(PostStartup, setup_system)
            .add_systems(Update, update_circle)
            .add_systems(Update, update_radius.after(update_circle))
            .add_systems(Update, update_marker.after(update_radius));
    }
}

fn setup_system(mut commands: Commands) {
    commands.spawn(Trace::new(400));
}

fn update_marker(
    time: ResMut<Time>,
    mut painter: ShapePainter,
    mut epi_query: Query<&mut Epicycle>,
    mut trace_query: Query<&mut Trace>,
) {
    painter.hollow = false;
    painter.thickness = 0.4;
    painter.set_color(Color::srgba(1.0, 1.0, 1.0, 1.0));
    let start_pos = painter.transform;

    if let Ok(mut trace) = trace_query.get_single_mut() {
        let trace_start = 700.0 - trace.points.len() as f32;
        if let Ok(epi) = epi_query.get_single_mut() {
            let mut x = epi.x;
            let mut y = epi.y;

            for i in 0..NUM_TERMS {
                painter.transform = start_pos;

                let (n, radius) = configure_wave_parameters(epi.radius, i);
                x += radius * (n * time.elapsed_seconds()).cos();
                y += radius * (n * time.elapsed_seconds()).sin();

                // draw epicycle marker
                painter.translate(Vec3::new(x, y, -0.1));
                painter.circle(MARKER_SIZE);
            }

            painter.transform = start_pos;
            // Draw connector
            painter.set_color(Color::srgba(0.0, 1.0, 1.0, 1.0));
            painter.line(Vec3::new(x, y, -0.1), Vec3::new(trace_start, y, -0.1));

            // Draw trace
            painter.set_color(Color::srgba(1.0, 1.0, 1.0, 1.0));
            trace.push(y);
            for (idx, point) in trace.points.iter().enumerate() {
                if idx > 0 {
                    painter.line(
                        Vec3::new(
                            trace_start + idx as f32,
                            *trace.points.get(idx - 1).unwrap(),
                            -0.1,
                        ),
                        Vec3::new(trace_start + 1.0 + idx as f32, *point, -0.1),
                    );
                }
            }
        }
    }
}

fn configure_wave_parameters(epicycle_radius: f32, i: i32) -> (f32, f32) {
    let (n, radius) = match WAVE_TYPE {
        WaveType::Square => {
            let n = i as f32 * 2.0 + 1.0;
            let radius = epicycle_radius * (4.0 / (n * PI));
            (n, radius)
        }
        WaveType::Saw => {
            let n = i as f32 + 1.0;
            let radius = epicycle_radius * (2 * (-1_i32).pow(n as u32)) as f32 / (n * PI);
            (n, radius)
        }
    };
    (n, radius)
}

fn update_circle(
    time: ResMut<Time>,
    mut painter: ShapePainter,
    mut epi_query: Query<&mut Epicycle>,
) {
    painter.hollow = true;
    painter.thickness = 0.4;
    painter.set_color(Color::srgba(1.0, 0.0, 1.0, 1.0));
    let start_pos = painter.transform;

    if let Ok(epi) = epi_query.get_single_mut() {
        let mut x = epi.x;
        let mut y = epi.y;

        for i in 0..NUM_TERMS {
            painter.transform = start_pos;
            let prev_x = x;
            let prev_y = y;

            let (n, radius) = configure_wave_parameters(epi.radius, i);
            x += radius * (n * time.elapsed_seconds()).cos();
            y += radius * (n * time.elapsed_seconds()).sin();

            // draw epicycle marker
            painter.translate(Vec3::new(prev_x, prev_y, -0.1));
            painter.circle(radius);
        }
    }
}

fn update_radius(
    time: ResMut<Time>,
    mut painter: ShapePainter,
    mut epi_query: Query<&mut Epicycle>,
) {
    painter.hollow = true;
    painter.thickness = 0.4;
    painter.set_color(Color::srgba(1.0, 0.0, 1.0, 1.0));
    let start_pos = painter.transform;

    if let Ok(epi) = epi_query.get_single_mut() {
        let mut x = epi.x;
        let mut y = epi.y;

        for i in 0..NUM_TERMS {
            painter.transform = start_pos;
            let prev_x = x;
            let prev_y = y;

            let (n, radius) = configure_wave_parameters(epi.radius, i);
            x += radius * (n * time.elapsed_seconds()).cos();
            y += radius * (n * time.elapsed_seconds()).sin();

            // Draw radius
            painter.thickness = 0.4;
            painter.set_color(Color::srgba(1.0, 0.0, 1.0, 1.0));
            painter.line(Vec3::new(prev_x, prev_y, -0.1), Vec3::new(x, y, -0.1));
        }
    }
}
