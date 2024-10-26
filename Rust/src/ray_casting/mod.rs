mod ray_caster;

use crate::ray_casting::ray_caster::RayCasterPlugin;
use bevy::prelude::*;
use bevy_vector_shapes::prelude::*;
use rand::Rng;

const WIDTH: f32 = 1000.0;
const HEIGHT: f32 = 1000.0;
const NUM_BOUNDARIES: usize = 9;

pub struct Boundary {
    start: Vec2,
    end: Vec2,
}

#[derive(Resource)]
pub struct Boundaries {
    data: [Boundary; NUM_BOUNDARIES],
}

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.05, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Ray Casting".into(),
                resolution: (WIDTH, HEIGHT).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(Shape2dPlugin::default())
        .add_plugins(RayCasterPlugin)
        .add_systems(Startup, setup_system)
        .add_systems(Update, update_system)
        .run();
}

fn setup_system(mut commands: Commands) {
    // Camera
    commands.spawn(Camera2dBundle::default());

    // // Create walls
    let mut rng = rand::thread_rng();
    let mut boundaries: Boundaries = Boundaries {
        data: [
            Boundary {
                start: Vec2::new(-WIDTH * 0.5 - 1.0, -HEIGHT * 0.5 - 1.0),
                end: Vec2::new(-WIDTH * 0.5 - 1.0, HEIGHT * 0.5 + 1.0),
            },
            Boundary {
                start: Vec2::new(WIDTH * 0.5 + 1.0, -HEIGHT * 0.5 - 1.0),
                end: Vec2::new(WIDTH * 0.5 + 1.0, HEIGHT * 0.5 + 1.0),
            },
            Boundary {
                start: Vec2::new(-WIDTH * 0.5 - 1.0, HEIGHT * 0.5 + 1.0),
                end: Vec2::new(WIDTH * 0.5 + 1.0, HEIGHT * 0.5 + 1.0),
            },
            Boundary {
                start: Vec2::new(-WIDTH * 0.5 - 1.0, -HEIGHT * 0.5 - 1.0),
                end: Vec2::new(WIDTH * 0.5 + 1.0, -HEIGHT * 0.5 - 1.0),
            },
            Boundary {
                start: Vec2::default(),
                end: Vec2::default(),
            },
            Boundary {
                start: Vec2::default(),
                end: Vec2::default(),
            },
            Boundary {
                start: Vec2::default(),
                end: Vec2::default(),
            },
            Boundary {
                start: Vec2::default(),
                end: Vec2::default(),
            },
            Boundary {
                start: Vec2::default(),
                end: Vec2::default(),
            },
        ],
    };
    for i in 4..NUM_BOUNDARIES {
        let start_x = rng.gen_range(-WIDTH * 0.5..WIDTH * 0.5);
        let start_y = rng.gen_range(-HEIGHT * 0.5..HEIGHT * 0.5);
        let end_x = rng.gen_range(-WIDTH * 0.5..WIDTH * 0.5);
        let end_y = rng.gen_range(-HEIGHT * 0.5..HEIGHT * 0.5);
        let b = Boundary {
            start: Vec2::new(start_x, start_y),
            end: Vec2::new(end_x, end_y),
        };
        boundaries.data[i] = b;
    }
    commands.insert_resource(boundaries);
}

fn update_system(mut painter: ShapePainter, boundaries: Res<Boundaries>) {
    // Create walls
    painter.hollow = false;
    painter.thickness = 0.4;
    painter.set_color(Color::srgba(1.0, 0.5, 1.0, 1.0));
    let start_pos = painter.transform;
    for boundary in boundaries.data.iter() {
        painter.transform = start_pos;
        painter.line(
            Vec3::new(boundary.start.x, boundary.start.y, -0.1),
            Vec3::new(boundary.end.x, boundary.end.y, -0.1),
        );
    }
}
