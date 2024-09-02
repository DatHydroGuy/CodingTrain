use bevy::prelude::*;
use bevy::sprite::MaterialMesh2dBundle;
use std::f32::consts::PI;

const DEFAULT_ROD_LENGTH: f32 = 200.0;
const DEFAULT_MASS: f32 = 20.0;
const INITIAL_ANGLE: f32 = PI * 0.5;
const GRAVITY: f32 = 1.0;

pub struct RodPlugin;

impl Plugin for RodPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(PostStartup, rod_spawn_system)
            .add_systems(Update, rod_animate_system);
    }
}

#[derive(Component)]
struct BaseRodWeight {}

#[derive(Component)]
struct EndRodWeight {}

#[derive(Component)]
pub struct BaseRod {}

#[derive(Component)]
pub struct EndRod {}

#[derive(Component)]
pub struct Rod {
    length: f32,
    mass: f32,
    angle: f32,
    angle_vel: f32,
}

fn rod_spawn_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    let initial_x: f32 = DEFAULT_ROD_LENGTH * INITIAL_ANGLE.sin();
    let initial_y: f32 = DEFAULT_ROD_LENGTH * INITIAL_ANGLE.cos();
    let base_mass = DEFAULT_MASS;
    let end_mass = DEFAULT_MASS;

    commands
        .spawn(SpriteBundle {
            sprite: Sprite {
                color: Color::srgb(1.0, 1.0, 0.5),
                custom_size: Some(Vec2::new(1.0, DEFAULT_ROD_LENGTH)),
                ..Default::default()
            },
            transform: Transform {
                translation: Vec3::new(initial_x * 0.5, -initial_y * 0.5, 0.0),
                rotation: Quat::from_rotation_z(PI * 0.5),
                ..Default::default()
            },
            ..Default::default()
        })
        .insert(BaseRod {})
        .insert(Rod {
            length: DEFAULT_ROD_LENGTH,
            mass: base_mass,
            angle: PI * 0.5,
            angle_vel: 0.0,
        });

    commands
        .spawn(MaterialMesh2dBundle {
            mesh: meshes.add(Circle::default()).into(),
            material: materials.add(Color::srgb(1.0, 1.0, 0.5)),
            transform: Transform::from_translation(Vec3::new(initial_x, initial_y, 0.))
                .with_scale(Vec3::new(base_mass, base_mass, base_mass)),
            ..default()
        })
        .insert(BaseRodWeight {});

    commands
        .spawn(SpriteBundle {
            sprite: Sprite {
                color: Color::srgb(1.0, 1.0, 0.5),
                custom_size: Some(Vec2::new(1.0, DEFAULT_ROD_LENGTH)),
                ..Default::default()
            },
            transform: Transform {
                translation: Vec3::new(initial_x * 1.5, -initial_y * 1.5, 0.0),
                rotation: Quat::from_rotation_z(PI * 0.5),
                ..Default::default()
            },
            ..Default::default()
        })
        .insert(EndRod {})
        .insert(Rod {
            length: DEFAULT_ROD_LENGTH,
            mass: end_mass,
            angle: PI * 0.5,
            angle_vel: 0.0,
        });

    commands
        .spawn(MaterialMesh2dBundle {
            mesh: meshes.add(Circle::default()).into(),
            material: materials.add(Color::srgb(1.0, 1.0, 0.5)),
            transform: Transform::from_translation(Vec3::new(initial_x * 2.0, initial_y * 2.0, 0.))
                .with_scale(Vec3::new(end_mass, end_mass, end_mass)),
            ..default()
        })
        .insert(EndRodWeight {});
}

fn rod_animate_system(
    commands: Commands,
    mut base_rod_weight: Query<&mut Transform, (With<BaseRodWeight>, Without<Rod>)>,
    mut end_rod_weight: Query<
        &mut Transform,
        (With<EndRodWeight>, Without<BaseRodWeight>, Without<Rod>),
    >,
    mut base_query: Query<(&mut Transform, &mut Rod), With<BaseRod>>,
    mut end_query: Query<(&mut Transform, &mut Rod), (With<EndRod>, Without<BaseRod>)>,
) {
    if let Ok((mut end_rod_transform, mut end_rod_data)) = end_query.get_single_mut() {
        if let Ok((mut base_rod_transform, mut base_rod_data)) = base_query.get_single_mut() {
            let x1 = base_rod_data.length * base_rod_data.angle.sin();
            let y1 = base_rod_data.length * base_rod_data.angle.cos();

            let x2 = end_rod_data.length * end_rod_data.angle.sin();
            let y2 = end_rod_data.length * end_rod_data.angle.cos();

            base_rod_transform.rotation = Quat::from_rotation_z(base_rod_data.angle);
            end_rod_transform.rotation = Quat::from_rotation_z(end_rod_data.angle);

            base_rod_transform.translation = Vec3::new(x1 * 0.5, -y1 * 0.5, 0.0);
            end_rod_transform.translation = Vec3::new(x1 + x2 * 0.5, -y1 - y2 * 0.5, 0.0);

            // Update BaseRodWeight
            if let Ok(mut base_weight_transform) = base_rod_weight.get_single_mut() {
                base_weight_transform.translation.x = x1;
                base_weight_transform.translation.y = -y1;
            }

            // Update EndRodWeight
            if let Ok(mut end_weight_transform) = end_rod_weight.get_single_mut() {
                let old_pos = end_weight_transform.translation.xy();
                end_weight_transform.translation.x = x1 + x2;
                end_weight_transform.translation.y = -y1 - y2;
                let new_pos = end_weight_transform.translation.xy();
                draw_line(old_pos, new_pos, commands);
            }

            // get rotation of base rod around z axis
            let angle1 = base_rod_transform.rotation.to_euler(EulerRot::ZYX).0;

            // get rotation of base rod around z axis
            let angle2 = end_rod_transform.rotation.to_euler(EulerRot::ZYX).0;

            let num11 = -GRAVITY * (2.0 * base_rod_data.mass + end_rod_data.mass) * angle1.sin();
            let num12 = -end_rod_data.mass * GRAVITY * (angle1 - 2.0 * angle2).sin();
            let num13 = -2.0 * (angle1 - angle2).sin() * end_rod_data.mass;
            let num14 = end_rod_data.angle_vel * end_rod_data.angle_vel * end_rod_data.length
                + base_rod_data.angle_vel
                    * base_rod_data.angle_vel
                    * base_rod_data.length
                    * (angle1 - angle2).cos();
            let numerator1 = num11 + num12 + num13 * num14;
            let den1 = base_rod_data.length
                * (2.0 * base_rod_data.mass + end_rod_data.mass
                    - end_rod_data.mass * (2.0 * angle1 - 2.0 * angle2).cos());
            let angle1_acc = numerator1 / den1;

            let num21 = 2.0 * (angle1 - angle2).sin();
            let num22 = base_rod_data.angle_vel
                * base_rod_data.angle_vel
                * base_rod_data.length
                * (base_rod_data.mass + end_rod_data.mass);
            let num23 = GRAVITY * (base_rod_data.mass + end_rod_data.mass) * angle1.cos();
            let num24 = end_rod_data.angle_vel
                * end_rod_data.angle_vel
                * end_rod_data.length
                * end_rod_data.mass
                * (angle1 - angle2).cos();
            let numerator2 = num21 * (num22 + num23 + num24);
            let den2 = end_rod_data.length
                * (2.0 * base_rod_data.mass + end_rod_data.mass
                    - end_rod_data.mass * (2.0 * angle1 - 2.0 * angle2).cos());
            let angle2_acc = numerator2 / den2;

            base_rod_data.angle_vel += angle1_acc;
            end_rod_data.angle_vel += angle2_acc;

            base_rod_data.angle += base_rod_data.angle_vel;
            end_rod_data.angle += end_rod_data.angle_vel;
        }
    }
}

fn draw_line(start_pos: Vec2, end_pos: Vec2, mut commands: Commands) {
    let mid_x = (start_pos.x + end_pos.x) * 0.5;
    let mid_y = (start_pos.y + end_pos.y) * 0.5;
    let length = ((end_pos.x - start_pos.x) * (end_pos.x - start_pos.x)
        + (end_pos.y - start_pos.y) * (end_pos.y - start_pos.y))
        .sqrt();
    let angle = (start_pos.x - end_pos.x).atan2(end_pos.y - start_pos.y);

    commands.spawn(SpriteBundle {
        sprite: Sprite {
            color: Color::srgba(0.75, 0.5, 1.0, 0.1),
            custom_size: Some(Vec2::new(1.0, length)),
            ..Default::default()
        },
        transform: Transform {
            translation: Vec3::new(mid_x, mid_y, 0.0),
            rotation: Quat::from_rotation_z(angle),
            ..Default::default()
        },
        ..Default::default()
    });
}
