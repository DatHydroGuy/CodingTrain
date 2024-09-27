use bevy::{
    math::Vec3,
    prelude::*,
    render::render_resource::{AsBindGroup, ShaderRef},
};
use rand::Rng;

const SCREEN_WIDTH: i16 = 1000;
const SCREEN_HEIGHT: i16 = 1000;
const NUM_METABALLS: usize = 10;

// This is the struct that will be passed to your shader
#[derive(Asset, AsBindGroup, TypePath, Debug, Clone)]
pub struct Metaballs {
    #[uniform(0)]
    pos_and_radius: [Vec3; NUM_METABALLS],
    velocity: [Vec3; NUM_METABALLS],
}

/// The Material trait is very configurable, but comes with sensible defaults for all methods.
/// You only need to implement functions for features that need non-default behavior. See the Material api docs for details!
impl Material for Metaballs {
    fn fragment_shader() -> ShaderRef {
        "..\\src\\metaballs\\custom_material.wgsl".into()
    }

    fn alpha_mode(&self) -> AlphaMode {
        AlphaMode::Blend
    }
}

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.03, 0.12, 0.24)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Metaballs".into(),
                resolution: (SCREEN_WIDTH, SCREEN_HEIGHT).into(),
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(MaterialPlugin::<Metaballs>::default())
        .add_systems(Startup, setup)
        .add_systems(Update, update_metaballs)
        .run();
}

/// set up a simple 3D scene
fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<Metaballs>>,
) {
    let mut rng = rand::thread_rng();
    let mut positions: [Vec3; NUM_METABALLS] = [Vec3::ZERO; NUM_METABALLS];
    let mut velocities: [Vec3; NUM_METABALLS] = [Vec3::ZERO; NUM_METABALLS];
    for i in 0..NUM_METABALLS {
        positions[i] = Vec3::new(rng.gen(), rng.gen(), rng.gen_range(0.01..0.2));
        velocities[i] = Vec3::new(
            rng.gen_range(-0.01..=0.01),
            rng.gen_range(-0.01..=0.01),
            0.0,
        );
    }
    commands.spawn(MaterialMeshBundle {
        mesh: meshes.add(Rectangle::default()),
        transform: Transform::default().with_scale(Vec3::splat(1.0)),
        material: materials.add(Metaballs {
            pos_and_radius: positions,
            velocity: velocities,
        }),
        ..default()
    });

    // camera
    commands.spawn(Camera3dBundle {
        transform: Transform::from_xyz(0.0, 0.0, 1.2).looking_at(Vec3::ZERO, Vec3::Y),
        ..default()
    });
}

fn update_metaballs(mut materials: ResMut<Assets<Metaballs>>) {
    for (_, metaballs) in materials.iter_mut() {
        for i in 0..NUM_METABALLS {
            metaballs.pos_and_radius[i] += metaballs.velocity[i];
            if metaballs.pos_and_radius[i].x < 0.0 || metaballs.pos_and_radius[i].x > 1.0 {
                metaballs.velocity[i].x *= -1.0;
            }
            if metaballs.pos_and_radius[i].y < 0.0 || metaballs.pos_and_radius[i].y > 1.0 {
                metaballs.velocity[i].y *= -1.0;
            }
        }
    }
}
