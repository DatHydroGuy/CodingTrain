use bevy::prelude::*;
use bevy::sprite::MaterialMesh2dBundle;
use bevy::window::PrimaryWindow;

const BALL_RADIUS: f32 = 10.0;
const SPEEDUP: u8 = 10;

#[derive(Resource)]
struct WinSize {
    width: f32,
    height: f32,
    half_diagonal: f32,
}

#[derive(Resource)]
struct Variables {
    pub n: f32,
    c: f32,
    angle: f32,
}

#[derive(Component)]
pub struct Pip {}

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.05, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Double Pendulum".into(),
                resolution: (1000.0, 1000.0).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_systems(Startup, setup_system)
        .add_systems(
            Update,
            (draw_pips_system, despawn_all_pips.run_if(reset_criteria)),
        )
        .run();
}

fn setup_system(mut commands: Commands, query: Query<&Window, With<PrimaryWindow>>) {
    // Camera
    commands.spawn(Camera2dBundle::default());

    // Capture window size
    let Ok(primary_window_size) = query.get_single() else {
        return;
    };
    let (window_width, window_height) = (primary_window_size.width(), primary_window_size.height());

    // Add WinSize resource
    let win_size = WinSize {
        width: window_width,
        height: window_height,
        half_diagonal: (window_width * window_width + window_height * window_height).sqrt() * 0.5,
    };
    commands.insert_resource(win_size);

    // Add Variables resource
    let vars = Variables {
        n: 0.0,
        c: 8.0,
        angle: 137.5_f32.to_radians(),
    };
    commands.insert_resource(vars);
}

fn draw_pips_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
    win_size: Res<WinSize>,
    mut vars: ResMut<Variables>,
) {
    for _ in 0..SPEEDUP {
        let angle = vars.n * vars.angle;
        let radius = vars.c * vars.n.sqrt();
        let x = radius * angle.cos();
        let y = radius * angle.sin();
        let saturation = (win_size.half_diagonal - radius).abs() / win_size.half_diagonal;
        let colour = Hsla::new(angle.to_degrees() % 360.0, saturation, 0.5, 1.0);

        commands
            .spawn(MaterialMesh2dBundle {
                mesh: meshes.add(Circle::default()).into(),
                material: materials.add(Color::from(colour)),
                transform: Transform::from_translation(Vec3::new(x, y, 0.)).with_scale(Vec3::new(
                    BALL_RADIUS,
                    BALL_RADIUS,
                    BALL_RADIUS,
                )),
                ..default()
            })
            .insert(Pip {});

        vars.n += 1.0;
    }
}

fn reset_criteria(win_size: Res<WinSize>, vars: Res<Variables>) -> bool {
    vars.c * vars.n.sqrt() > win_size.half_diagonal
}

fn despawn_all_pips(
    mut commands: Commands,
    mut vars: ResMut<Variables>,
    query: Query<Entity, With<Pip>>,
) {
    vars.n = 0.0;
    for entity in query.iter() {
        commands.entity(entity).despawn();
    }
}
