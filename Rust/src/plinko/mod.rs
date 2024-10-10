use bevy::prelude::*;
use bevy_rapier2d::prelude::*;
use rand::Rng;
use std::f32::consts::PI;
use std::time::Duration;

// Plinko board measurements taken from https://www.instructables.com/PLINKO/
const HX: f32 = 300.0;
const HY: f32 = 500.0;
const DIVIDER_HX: f32 = 5.0;
const PEG_RADIUS: f32 = 3.0;
const XGAP: f32 = HX * 0.2;
const YGAP: f32 = XGAP * 0.8660254; // sqrt(3.0) / 2.0
const BALL_RADIUS: f32 = (XGAP - DIVIDER_HX * 2.0) * 0.5 * 0.8; // 80% of gap size
const DIVIDER_HY: f32 = BALL_RADIUS * 3.0;

pub fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Plinko".into(),
                resolution: (HX * 2.0, HY * 2.0).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(RapierPhysicsPlugin::<NoUserData>::pixels_per_meter(450.0))
        .add_plugins(RapierDebugRenderPlugin::default())
        .add_systems(
            Startup,
            (
                setup_graphics,
                setup_ground,
                setup_sides,
                setup_pegs,
                setup_resources,
            ),
        )
        .add_systems(Update, spawn_balls)
        .run();
}

#[derive(Resource)]
struct BallSpawnConfig {
    /// How often to spawn a new ball? (repeating timer)
    timer: Timer,
}

fn setup_graphics(mut commands: Commands) {
    // Add a camera so we can see the debug-render.
    commands.spawn(Camera2dBundle::default());
}

fn setup_ground(mut commands: Commands) {
    /* Create the ground. */
    commands
        .spawn(Collider::cuboid(HX * 2.0, DIVIDER_HX))
        .insert(TransformBundle::from(Transform::from_xyz(0.0, -HY, 0.0)));

    /* Create the slots */
    let x_min = -5;
    let x_max = 5;
    for i in x_min..=x_max {
        let mut divider_length = DIVIDER_HY;
        let mut divider_middle = -HY + DIVIDER_HY + DIVIDER_HX;
        if i == x_min || i == x_max {
            divider_length = HY * 2.0;
            divider_middle = HY;
        }
        commands
            .spawn(Collider::cuboid(DIVIDER_HX, divider_length))
            .insert(Restitution::coefficient(0.7))
            .insert(Friction::coefficient(0.1))
            .insert(TransformBundle::from(Transform::from_xyz(
                XGAP * i as f32,
                divider_middle,
                0.0,
            )));
    }
}

fn setup_sides(mut commands: Commands) {
    /* Create the angled sides. */
    for i in -2..=4 {
        commands
            .spawn(Collider::cuboid(XGAP * 0.62, XGAP * 0.62))
            .insert(Restitution::coefficient(0.7))
            .insert(Friction::coefficient(0.1))
            .insert(TransformBundle::from(
                Transform::from_xyz(
                    -HX + DIVIDER_HX,
                    DIVIDER_HX + YGAP * (i as f32 * 2.0 - 1.0),
                    0.0,
                )
                .with_rotation(Quat::from_rotation_z(PI * 0.25)),
            ));
        commands
            .spawn(Collider::cuboid(XGAP * 0.62, XGAP * 0.62))
            .insert(Restitution::coefficient(0.7))
            .insert(Friction::coefficient(0.1))
            .insert(TransformBundle::from(
                Transform::from_xyz(
                    HX - DIVIDER_HX,
                    DIVIDER_HX + YGAP * (i as f32 * 2.0 - 1.0),
                    0.0,
                )
                .with_rotation(Quat::from_rotation_z(PI * 0.25)),
            ));
    }
}

fn setup_pegs(mut commands: Commands) {
    /* Create the pegs */
    let peg_adjustment = -45.0_f32;
    let y_min = -6i32;
    let y_max = 8i32;
    for y_pos in y_min..=y_max {
        let mut x_min = -4;
        let mut x_max = 4;
        let mut offset = 0.0;
        if y_pos.abs() % 2i32 == 1i32 {
            offset += XGAP * 0.5;
        } else if y_pos == y_min {
            x_max += 1;
        } else {
            x_min += 1;
        }
        for x_pos in x_min..x_max {
            commands
                .spawn(Collider::ball(PEG_RADIUS))
                .insert(Restitution::coefficient(0.7))
                .insert(Friction::coefficient(0.1))
                .insert(TransformBundle::from(Transform::from_xyz(
                    offset + XGAP * x_pos as f32,
                    YGAP * y_pos as f32 + peg_adjustment,
                    0.0,
                )));
        }
    }
}

fn setup_resources(mut commands: Commands) {
    // Create & insert the ball spawning timer resource
    commands.insert_resource(BallSpawnConfig {
        // create the repeating timer
        timer: Timer::new(Duration::from_secs(2), TimerMode::Repeating),
    })
}

fn spawn_balls(mut commands: Commands, time: Res<Time>, mut config: ResMut<BallSpawnConfig>) {
    /* Create the bouncing ball. */

    // tick the timer
    config.timer.tick(time.delta());

    if config.timer.finished() {
        let mut rng = rand::thread_rng();
        let x_offset = rng.gen_range(-0.1..=0.1) as f32;
        commands
            .spawn(RigidBody::Dynamic)
            .insert(Collider::ball(BALL_RADIUS))
            .insert(Restitution::coefficient(0.7))
            .insert(Friction::coefficient(0.1))
            .insert(TransformBundle::from(Transform::from_xyz(
                x_offset, 500.0, 0.0,
            )));
    }
}
