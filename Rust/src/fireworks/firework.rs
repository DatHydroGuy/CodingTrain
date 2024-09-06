use crate::fireworks::{GRAVITY, SCREEN_HEIGHT, SCREEN_WIDTH};
use bevy::app::App;
use bevy::math::{Vec2, Vec3};
use bevy::prelude::*;
use bevy::sprite::MaterialMesh2dBundle;
use rand::{random, Rng};
use std::f32::consts::PI;

const NUM_PARTICLES_IN_BURST: usize = 100;
pub struct FireworkPlugin;

impl Plugin for FireworkPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(
            Update,
            spawn_system
                .before(update_system)
                .run_if(firework_spawn_criteria),
        )
        .add_systems(Update, (update_system, burst_system, cleanup_system));
    }
}

fn firework_spawn_criteria() -> bool {
    rand::thread_rng().gen_bool(1.0 / 20.0)
}

#[derive(Component, Debug)]
pub struct Firework {
    pub pos: Vec2,
    vel: Vec2,
    acc: Vec2,
    is_burst: bool,
    lifespan: i16,
    hue: f32,
}

impl Default for Firework {
    fn default() -> Self {
        Firework {
            pos: Vec2::ZERO,
            vel: Vec2::ZERO,
            acc: Vec2::ZERO,
            is_burst: false,
            lifespan: 255,
            hue: 0.0,
        }
    }
}

impl Firework {
    pub fn new(
        pos: Vec2,
        vel: Option<Vec2>,
        acc: Option<Vec2>,
        is_burst: bool,
        lifespan: i16,
        hue: f32,
    ) -> Self {
        let mut new_firework = Firework {
            pos,
            vel: Vec2::ZERO,
            acc: Vec2::ZERO,
            is_burst,
            lifespan,
            hue,
        };

        if let Some(velocity) = vel {
            new_firework.vel = velocity;
        } else {
            new_firework.vel = Vec2::ZERO;
        }

        if let Some(acceleration) = acc {
            new_firework.acc = acceleration;
        } else {
            new_firework.acc = Vec2::ZERO;
        }

        new_firework
    }

    fn update(&mut self) {
        self.vel += self.acc;
        self.pos += self.vel;
        self.acc = Vec2::ZERO;
    }

    fn apply_force(&mut self, force: Vec2) {
        self.acc += force;
    }
}

#[derive(Component)]
pub struct Burst {}

fn spawn_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    let mut rng = rand::thread_rng();
    let x_pos = rng.gen_range(-SCREEN_WIDTH / 2..=SCREEN_WIDTH / 2) as f32;
    let y_pos = -SCREEN_HEIGHT as f32 / 2.0;

    let firework = Firework::new(
        Vec2::new(x_pos, y_pos),
        Some(Vec2::new(
            rng.gen_range(-4.0..=4.0),
            rng.gen_range(15.0..=20.0),
        )),
        Some(GRAVITY),
        false,
        255,
        random::<f32>() * 360.0,
    );
    commands
        .spawn(MaterialMesh2dBundle {
            mesh: meshes.add(Circle::default()).into(),
            material: materials.add(Color::from(Hsla::new(firework.hue, 1.0, 0.5, 0.7))),
            transform: Transform::from_translation(Vec3::new(firework.pos.x, firework.pos.y, 0.0))
                .with_scale(Vec3::splat(10.0)),
            ..default()
        })
        .insert(firework);
}

fn update_system(
    mut commands: Commands,
    mut materials: ResMut<Assets<ColorMaterial>>,
    mut query: Query<(Entity, &mut Transform, &mut Firework), With<Firework>>,
) {
    for (entity, mut transform, mut firework) in query.iter_mut() {
        firework.apply_force(GRAVITY);
        if firework.is_burst {
            firework.vel *= 0.98;
            firework.lifespan -= 4;
            if firework.lifespan < 0 {
                firework.lifespan = 0;
            }
        }
        firework.update();
        transform.translation = Vec3::from((firework.pos, 0.0));
        let new_col = Color::from(Hsla::new(
            firework.hue,
            1.0,
            0.5,
            firework.lifespan as f32 / 255.0,
        ));
        commands
            .entity(entity)
            .insert(materials.add(ColorMaterial::from_color(new_col)));
    }
}

fn burst_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
    query: Query<(Entity, &Firework), (With<Firework>, Without<Burst>)>,
) {
    let mut rng = rand::thread_rng();

    for (entity, firework) in query.iter() {
        if firework.vel.y <= 0.0 {
            commands.entity(entity).despawn();
            for _ in 0..NUM_PARTICLES_IN_BURST {
                let new_firework = Firework::new(
                    firework.pos,
                    Some(Vec2::from_angle(rng.gen_range(-PI..PI)) * rng.gen_range(1.0..=7.0)),
                    Some(GRAVITY),
                    true,
                    rng.gen_range(200..300),
                    firework.hue,
                );
                commands
                    .spawn(MaterialMesh2dBundle {
                        mesh: meshes.add(Circle::default()).into(),
                        material: materials.add(Color::from(Hsla::new(
                            firework.hue,
                            1.0,
                            0.5,
                            firework.lifespan as f32 / 255.0,
                        ))),
                        transform: Transform::from_translation(Vec3::new(
                            new_firework.pos.x,
                            new_firework.pos.y,
                            0.0,
                        ))
                        .with_scale(Vec3::splat(6.0)),
                        ..default()
                    })
                    .insert(new_firework)
                    .insert(Burst {});
            }
        }
    }
}

fn cleanup_system(mut commands: Commands, query: Query<(Entity, &Firework), With<Firework>>) {
    for (entity, firework) in query.iter() {
        if firework.pos.y <= -SCREEN_HEIGHT as f32 / 2.0 || firework.lifespan <= 0 {
            commands.entity(entity).despawn();
        }
    }
}
