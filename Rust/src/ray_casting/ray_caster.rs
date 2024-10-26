use crate::ray_casting::{Boundaries, Boundary, HEIGHT, WIDTH};
use bevy::prelude::*;
use bevy::window::PrimaryWindow;
use bevy_vector_shapes::prelude::*;
use noisy_bevy::simplex_noise_2d;

#[derive(PartialEq)]
enum MotionType {
    Mouse,
    Simplex,
}

const MOTION_TYPE: MotionType = MotionType::Simplex; // Change to Mouse for manual movement

pub struct RayCasterPlugin;

impl Plugin for RayCasterPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, setup_system)
            .add_systems(Update, change_position);
    }
}

#[derive(Component)]
pub struct RayCaster {
    position: Vec2,
}

impl RayCaster {
    fn new(position: Vec2) -> Self {
        RayCaster { position }
    }
}

#[derive(Component)]
pub struct Ray {
    position: Vec2,
    pub(crate) direction: Vec2,
}

impl Ray {
    pub(crate) fn new(position: Vec2, angle: f32) -> Self {
        Ray {
            position,
            direction: Vec2::from_angle(angle),
        }
    }

    pub fn look_at(&mut self, x: f32, y: f32) {
        self.direction.x = x - self.position.x;
        self.direction.y = y - self.position.y;
        self.direction = self.direction.normalize();
    }

    pub fn check_intersections(&self, boundary: &Boundary) -> Option<Vec2> {
        let x1 = boundary.start.x;
        let y1 = boundary.start.y;
        let x2 = boundary.end.x;
        let y2 = boundary.end.y;
        let x3 = self.position.x;
        let y3 = self.position.y;
        let x4 = self.position.x + self.direction.x;
        let y4 = self.position.y + self.direction.y;

        let denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);
        if denom == 0.0 {
            return None;
        }
        let t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4);
        let u_num = (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3);
        let t = t_num / denom;
        let u = -u_num / denom;
        if t > 0.0 && t < 1.0 && u > 0.0 {
            Some(self.position + self.direction * u)
        } else {
            None
        }
    }
}

fn setup_system(mut commands: Commands) {
    let x_pos = 0.0;
    let y_pos = 0.0;

    let particle = RayCaster::new(Vec2::new(x_pos, y_pos));
    for i in (0..360).step_by(5) {
        let ray = Ray::new(particle.position, (i as f32).to_radians());
        commands.spawn(()).insert(ray);
    }

    commands.spawn(()).insert(particle);
}

fn change_position(
    boundaries: Res<Boundaries>,
    time: Res<Time>,
    q_windows: Query<&Window, With<PrimaryWindow>>,
    mut ray_query: Query<&mut Ray, With<Ray>>,
    mut painter: ShapePainter,
) {
    let x_val = time.elapsed_seconds_wrapped() * 0.1;
    let y_val = time.elapsed_seconds_wrapped() * 0.1 + 12345.67;
    painter.hollow = false;
    painter.thickness = 0.4;
    painter.set_color(Color::srgba(1.0, 1.0, 1.0, 1.0));
    let painter_pos = painter.transform;
    let ray_caster_position = match MOTION_TYPE {
        MotionType::Mouse => {
            if let Some(mouse_position) = q_windows.single().cursor_position() {
                Vec2::new(
                    mouse_position.x - WIDTH * 0.5,
                    HEIGHT * 0.5 - mouse_position.y,
                )
            } else {
                Vec2::default()
            }
        }
        MotionType::Simplex => Vec2::new(
            simplex_noise_2d(Vec2::new(x_val, y_val)) * WIDTH * 0.5,
            simplex_noise_2d(Vec2::new(y_val, x_val)) * HEIGHT * 0.5,
        ),
    };

    for mut ray in ray_query.iter_mut() {
        let particle_pos = ray_caster_position;
        painter.transform = painter_pos;
        ray.position = particle_pos;
        let mut closest_point = Vec2::default();
        let mut closest_dist = f32::MAX;

        for boundary in boundaries.data.iter() {
            if let Some(p) = ray.check_intersections(boundary) {
                let dist = (particle_pos - p).length();
                if dist < closest_dist {
                    closest_dist = dist;
                    closest_point = p;
                }
            }
        }

        painter.line(
            Vec3::from((particle_pos, -0.1)),
            Vec3::from((closest_point, -0.1)),
        );
    }
}
