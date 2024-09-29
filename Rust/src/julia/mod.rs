use bevy::{
    math::{Vec2, Vec3},
    prelude::*,
    render::render_resource::{AsBindGroup, ShaderRef},
    window::PrimaryWindow,
};

const SCREEN_WIDTH: i16 = 1200;
const SCREEN_HEIGHT: i16 = 900;
const NUM_COLOURS: usize = 193;

#[derive(Resource)]
struct ColourData {
    colour_map: [Vec3; NUM_COLOURS],
    is_cycling: bool,
}

#[derive(Resource)]
struct MousePosition {
    x: f32,
    y: f32,
}

// This is the struct that will be passed to your shader
#[derive(Asset, AsBindGroup, TypePath, Debug, Clone)]
pub struct Julia {
    #[uniform(0)]
    colour_map: [Vec3; NUM_COLOURS],
    #[uniform(1)]
    colour_offset: i32,
    #[uniform(2)]
    mouse_pos: Vec2,
}

/// The Material trait is very configurable, but comes with sensible defaults for all methods.
/// You only need to implement functions for features that need non-default behavior. See the Material api docs for details!
impl Material for Julia {
    fn fragment_shader() -> ShaderRef {
        "..\\src\\julia\\custom_material.wgsl".into()
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
                title: "Bevy Julia Fractal".into(),
                resolution: (SCREEN_WIDTH, SCREEN_HEIGHT).into(),
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(MaterialPlugin::<Julia>::default())
        .add_systems(Startup, setup)
        .add_systems(Update, update_colour_cycling)
        .add_systems(Update, (keyboard_event_system, mouse_position_system))
        .run();
}

/// set up a simple 3D scene
fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<Julia>>,
) {
    let mut colours: [Vec3; NUM_COLOURS] = [Vec3::ZERO; NUM_COLOURS];
    let colour_step = (NUM_COLOURS - 1) / 3;
    for i in 0..colour_step {
        colours[i] = Vec3::new(i as f32 * 4.0 / 255.0, 0.0, 0.0);
        colours[i + colour_step] = Vec3::new(1.0, i as f32 * 4.0 / 255.0, 0.0);
        colours[i + colour_step * 2] = Vec3::new(1.0, 1.0, i as f32 * 4.0 / 255.0);
    }
    colours[NUM_COLOURS - 1] = Vec3::splat(1.0);

    let colour_offset = 0;

    commands.spawn(MaterialMeshBundle {
        mesh: meshes.add(Rectangle::default()),
        transform: Transform::default().with_scale(Vec3::new(4.0 / 3.0, 1.0, 0.0)),
        material: materials.add(Julia {
            colour_map: colours,
            colour_offset,
            mouse_pos: Vec2::new(0.0, 0.0),
        }),
        ..default()
    });

    // camera
    commands.spawn(Camera3dBundle {
        transform: Transform::from_xyz(0.0, 0.0, 1.2).looking_at(Vec3::ZERO, Vec3::Y),
        ..default()
    });

    let colour_data = ColourData {
        colour_map: colours,
        is_cycling: false,
    };
    commands.insert_resource(colour_data);

    let mouse_position = MousePosition { x: 0.0, y: 0.0 };
    commands.insert_resource(mouse_position);
}

fn update_colour_cycling(mut materials: ResMut<Assets<Julia>>, colour_data: Res<ColourData>) {
    if colour_data.is_cycling {
        for (_, julia) in materials.iter_mut() {
            julia.colour_offset = (julia.colour_offset + 1) % julia.colour_map.len() as i32;
        }
    }
}

fn keyboard_event_system(
    key: Res<ButtonInput<KeyCode>>,
    mut exit: EventWriter<AppExit>,
    mut colour_data: ResMut<ColourData>,
) {
    if key.pressed(KeyCode::Escape) {
        exit.send(AppExit::Success);
    }
    if key.pressed(KeyCode::KeyZ) {
        colour_data.is_cycling = true;
    }
    if key.pressed(KeyCode::KeyX) {
        colour_data.is_cycling = false;
    }
}

fn mouse_position_system(
    mut materials: ResMut<Assets<Julia>>,
    q_windows: Query<&Window, With<PrimaryWindow>>,
) {
    // Games typically only have one window (the primary window)
    if let Some(position) = q_windows.single().cursor_position() {
        let half_width = SCREEN_WIDTH as f32 / 2.0;
        let half_height = SCREEN_HEIGHT as f32 / 2.0;
        for (_, julia) in materials.iter_mut() {
            julia.mouse_pos.x = (position.x - half_width) / half_width;
            julia.mouse_pos.y = (position.y - half_height) / half_height;
        }
    }
}
