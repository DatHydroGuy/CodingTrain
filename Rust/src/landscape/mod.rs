use bevy::math::Vec3;
use bevy::prelude::*;
use bevy::render::mesh::{self, PrimitiveTopology};
use bevy::render::render_asset::RenderAssetUsages;
use noisy_bevy::simplex_noise_2d;
use std::f32::consts::PI;

const X_MIN: f32 = -2.0;
const X_MAX: f32 = 2.0;
const Y_MIN: f32 = -1.5;
const Y_MAX: f32 = 1.5;
const COLS: usize = 40;
const ROWS: usize = 30;
const NOISE_X_STEP: f32 = 0.05;
const NOISE_Y_STEP: f32 = 0.05;
const NOISE_MULTIPLIER: f32 = 0.5;

#[derive(Component)]
struct CameraMarker;

pub(crate) fn main() {
    App::new()
        .insert_resource(Msaa::Sample4)
        .insert_resource(ClearColor(Color::srgb(0.05, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Simplex Landscape".into(),
                resolution: (1000.0, 1000.0).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_systems(Startup, setup)
        .add_systems(Update, (move_light, move_terrain))
        .run();
}

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    let mut mesh = Mesh::new(
        PrimitiveTopology::TriangleList,
        RenderAssetUsages::default(),
    );

    let x_step = (X_MAX - X_MIN) / COLS as f32;
    let y_step = (Y_MAX - Y_MIN) / ROWS as f32;

    // Positions of the vertices
    let mut vertices: Vec<[f32; 3]> = Vec::new();

    for y in 0..ROWS {
        for x in 0..=COLS {
            let x_val = X_MIN + x_step * x as f32;
            let y_val = Y_MAX - y_step * y as f32;
            let z_value = simplex_noise_2d(Vec2::new(x_val, y_val)) * NOISE_MULTIPLIER;
            vertices.push([x_val, y_val, z_value]);
            let y_val = Y_MAX - y_step * (y + 1) as f32;
            let z_value = simplex_noise_2d(Vec2::new(x_val, y_val)) * NOISE_MULTIPLIER;
            vertices.push([x_val, y_val, z_value]);
        }
    }

    mesh.insert_attribute(Mesh::ATTRIBUTE_POSITION, vertices);

    // Note: order matters. Order the vertices anti-clockwise, or you won't see the triangle!
    let mut indices: Vec<u32> = Vec::new();
    for y in 0..ROWS {
        for x in 0..COLS {
            let offset = (y as u32 * (COLS as u32 + 1) * 2) + x as u32 * 2;
            indices.push(offset);
            indices.push(offset + 1);
            indices.push(offset + 2);
            indices.push(offset + 2);
            indices.push(offset + 1);
            indices.push(offset + 3);
        }
    }
    mesh.insert_indices(mesh::Indices::U32(indices));

    // Compute normals. Works for TriangleList, but not TriangleStrip
    mesh.compute_normals();

    commands.spawn(PbrBundle {
        mesh: meshes.add(mesh),
        material: materials.add(Color::srgb(0.3, 0.5, 0.3)),
        ..default()
    });

    commands.spawn(PointLightBundle {
        point_light: PointLight {
            intensity: 10000.0,
            shadows_enabled: true,
            ..default()
        },
        transform: Transform::from_xyz(-2.0, 2.0, 4.0),
        ..default()
    });

    commands
        .spawn(Camera3dBundle {
            transform: Transform::from_xyz(0.0, -2.0, 2.0).looking_at(Vec3::ZERO, Vec3::Y),
            ..default()
        })
        .insert(CameraMarker);
}

fn move_terrain(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    time: Res<Time>,
    mut query: Query<Entity, (With<Transform>, Without<PointLight>, Without<CameraMarker>)>,
) {
    if let Ok(entity) = query.get_single_mut() {
        commands.entity(entity).despawn();

        let mut mesh = Mesh::new(
            PrimitiveTopology::TriangleList,
            RenderAssetUsages::default(),
        );

        let x_step = (X_MAX - X_MIN) / COLS as f32;
        let y_step = (Y_MAX - Y_MIN) / ROWS as f32;

        // Positions of the vertices
        let mut vertices: Vec<[f32; 3]> = Vec::new();

        let mut y_noise = -time.elapsed_seconds();
        for y in 0..ROWS {
            let mut x_noise = 0.0;
            for x in 0..=COLS {
                let x_val = X_MIN + x_step * x as f32;
                let y_val = Y_MAX - y_step * y as f32;
                let z_value = simplex_noise_2d(Vec2::new(x_noise, y_noise)) * NOISE_MULTIPLIER;
                vertices.push([x_val, y_val, z_value]);
                let y_val = Y_MAX - y_step * (y + 1) as f32;
                let z_value =
                    simplex_noise_2d(Vec2::new(x_noise, y_noise + NOISE_Y_STEP)) * NOISE_MULTIPLIER;
                vertices.push([x_val, y_val, z_value]);
                x_noise += NOISE_X_STEP;
            }
            y_noise += NOISE_Y_STEP;
        }

        mesh.insert_attribute(Mesh::ATTRIBUTE_POSITION, vertices);

        // Note: order matters. Order the vertices anti-clockwise, or you won't see the triangle!
        let mut indices: Vec<u32> = Vec::new();
        for y in 0..ROWS {
            for x in 0..COLS {
                let offset = (y as u32 * (COLS as u32 + 1) * 2) + x as u32 * 2;
                indices.push(offset);
                indices.push(offset + 1);
                indices.push(offset + 2);
                indices.push(offset + 2);
                indices.push(offset + 1);
                indices.push(offset + 3);
            }
        }
        mesh.insert_indices(mesh::Indices::U32(indices));

        // Compute normals. Works for TriangleList, but not TriangleStrip
        mesh.compute_normals();

        commands.spawn(PbrBundle {
            mesh: meshes.add(mesh),
            material: materials.add(Color::srgb(0.3, 0.5, 0.3)),
            ..default()
        });
    }
}

fn move_light(time: Res<Time>, mut query: Query<&mut Transform, With<PointLight>>) {
    let angle = PI + time.elapsed_seconds();
    for mut transform in query.iter_mut() {
        transform.translation = Vec3::new(2.0 * angle.sin(), 2.0 * angle.cos(), 3.0 + angle.sin());
    }
}
