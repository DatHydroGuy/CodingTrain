use bevy::prelude::*;
use rand::Rng;

const SCREEN_WIDTH: i16 = 1000;
const SCREEN_HEIGHT: i16 = 1000;
const SCREEN_DEPTH: i16 = 1000;
const STAR_FADE_DISTANCE: f32 = 500.0;
const NUM_STARS: usize = 1000;
const MAX_SPEED: i16 = 20;

#[derive(Resource)]
struct Variables {
    star_speed: i16,
}

#[derive(Component)]
struct Star {}

pub fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.0, 0.0, 0.0)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Starfield 3D".into(),
                resolution: (SCREEN_WIDTH, SCREEN_HEIGHT).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_systems(Startup, setup_system)
        .add_systems(Update, (update_stars_system, keyboard_event_system))
        .run();
}

fn setup_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    let mut rng = rand::thread_rng();

    // Camera
    commands.spawn(Camera3dBundle {
        transform: Transform::from_xyz(0.0, 0.0, SCREEN_DEPTH as f32)
            .looking_at(Vec3::ZERO, Vec3::Y),
        ..default()
    });

    commands.spawn(DirectionalLightBundle {
        directional_light: DirectionalLight {
            illuminance: light_consts::lux::DIRECT_SUNLIGHT,
            ..default()
        },
        transform: Transform {
            translation: Vec3::new(0.0, 0.0, SCREEN_DEPTH as f32 + 10.0),
            ..default()
        },
        ..default()
    });

    for _ in 0..NUM_STARS {
        let x_pos = rng.gen_range(-SCREEN_WIDTH / 2..=SCREEN_WIDTH / 2) as f32;
        let y_pos = rng.gen_range(-SCREEN_HEIGHT / 2..=SCREEN_HEIGHT / 2) as f32;
        let z_pos = rng.gen_range(-SCREEN_HEIGHT..=SCREEN_DEPTH) as f32;
        commands
            .spawn(PbrBundle {
                mesh: meshes.add(Circle::default()),
                material: materials.add(Color::BLACK),
                transform: Transform::from_translation(Vec3::new(x_pos, y_pos, z_pos)),
                ..default()
            })
            .insert(Star {});
    }

    let variables = Variables { star_speed: 10 };
    commands.insert_resource(variables);
}

fn update_stars_system(
    mut commands: Commands,
    vars: Res<Variables>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut query: Query<(Entity, &mut Transform), With<Star>>,
) {
    for (entity, mut transform) in query.iter_mut() {
        // Move stars towards camera
        transform.translation.z += vars.star_speed as f32;
        if transform.translation.z >= SCREEN_DEPTH as f32 {
            let mut rng = rand::thread_rng();
            transform.translation.x = rng.gen_range(-SCREEN_WIDTH / 2..=SCREEN_WIDTH / 2) as f32;
            transform.translation.y = rng.gen_range(-SCREEN_HEIGHT / 2..=SCREEN_HEIGHT / 2) as f32;
            transform.translation.z = -SCREEN_DEPTH as f32;
        }

        // Fade in new stars from black to white over STAR_FADE_DISTANCE pixels
        let mut dist = transform.translation.z + SCREEN_DEPTH as f32;
        if dist > STAR_FADE_DISTANCE {
            dist = STAR_FADE_DISTANCE;
        }
        dist /= STAR_FADE_DISTANCE;
        let new_col = Color::srgba(dist, dist, dist, dist);
        commands
            .entity(entity)
            .insert(materials.add(StandardMaterial::from_color(new_col)));
    }
}

fn keyboard_event_system(
    key: Res<ButtonInput<KeyCode>>,
    mut exit: EventWriter<AppExit>,
    mut vars: ResMut<Variables>,
) {
    if key.pressed(KeyCode::Escape) {
        exit.send(AppExit::Success);
    } else if key.pressed(KeyCode::ArrowUp) {
        vars.star_speed += 1;
        if vars.star_speed > MAX_SPEED {
            vars.star_speed = MAX_SPEED;
        }
    } else if key.pressed(KeyCode::ArrowDown) {
        vars.star_speed -= 1;
        if vars.star_speed < 1 {
            vars.star_speed = 1;
        }
    }
}
