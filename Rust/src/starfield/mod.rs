use bevy::color::palettes::basic::WHITE;
use bevy::prelude::*;
use bevy::sprite::MaterialMesh2dBundle;
use rand::Rng;

const SCREEN_WIDTH: i16 = 1000;
const SCREEN_HEIGHT: i16 = 1000;
const NUM_STARS: usize = 1000;
const MAX_SPEED: i16 = 20;

#[derive(Resource)]
struct Variables {
    star_speed: i16,
}

#[derive(Component)]
struct Star {
    x_pos: f32,
    y_pos: f32,
    z_pos: i16,
}

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.05, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Starfield".into(),
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
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    let mut rng = rand::thread_rng();

    // Camera
    commands.spawn(Camera2dBundle::default());

    for _ in 0..NUM_STARS {
        let x_pos = rng.gen_range(-SCREEN_WIDTH / 2..=SCREEN_WIDTH / 2) as f32;
        let y_pos = rng.gen_range(-SCREEN_HEIGHT / 2..=SCREEN_HEIGHT / 2) as f32;
        let z_pos = rng.gen_range(0..SCREEN_WIDTH / 2);
        let radius = 10.0 - (z_pos as f32 * 10.0 / (SCREEN_WIDTH as f32 / 2.0));
        commands
            .spawn(MaterialMesh2dBundle {
                mesh: meshes.add(Circle::default()).into(),
                material: materials.add(Color::from(WHITE)),
                transform: Transform::from_translation(Vec3::new(x_pos, y_pos, 0.0))
                    .with_scale(Vec3::new(radius, radius, radius)),
                ..default()
            })
            .insert(Star {
                x_pos,
                y_pos,
                z_pos,
            });
    }

    let variables = Variables { star_speed: 10 };
    commands.insert_resource(variables);
}

fn update_stars_system(
    vars: Res<Variables>,
    mut query: Query<(&mut Transform, &mut Star), With<Star>>,
) {
    for (mut transform, mut star) in query.iter_mut() {
        let mut rng = rand::thread_rng();
        star.z_pos -= vars.star_speed;
        if star.z_pos < 1 {
            let x_pos = rng.gen_range(-SCREEN_WIDTH / 2..=SCREEN_WIDTH / 2) as f32;
            let y_pos = rng.gen_range(-SCREEN_HEIGHT / 2..=SCREEN_HEIGHT / 2) as f32;
            star.x_pos = x_pos;
            star.y_pos = y_pos;
            star.z_pos = SCREEN_WIDTH / 2;
            transform.translation.x = x_pos;
            transform.translation.y = y_pos;
            transform.scale = Vec3::new(0.0, 0.0, 0.0);
        }
        transform.translation.x = (SCREEN_WIDTH as f32 / 2.0) * star.x_pos / star.z_pos as f32;
        transform.translation.y = (SCREEN_HEIGHT as f32 / 2.0) * star.y_pos / star.z_pos as f32;
        let radius = 10.0 - (star.z_pos as f32 * 10.0 / (SCREEN_WIDTH as f32 / 2.0));
        transform.scale = Vec3::new(radius, radius, radius);
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
