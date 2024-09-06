mod firework;

use crate::fireworks::firework::FireworkPlugin;
use bevy::prelude::*;

const SCREEN_WIDTH: i16 = 1600;
const SCREEN_HEIGHT: i16 = 1000;
const GRAVITY: Vec2 = Vec2::new(0.0, -0.2);
const NUM_FIREWORKS: usize = 100;

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgba(0.0, 0.0, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Fireworks".into(),
                resolution: (SCREEN_WIDTH, SCREEN_HEIGHT).into(),
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(FireworkPlugin)
        .add_systems(Startup, setup_system)
        .add_systems(Update, keyboard_event_system)
        .run();
}

fn setup_system(mut commands: Commands) {
    // Camera
    commands.spawn(Camera2dBundle::default());
}

fn keyboard_event_system(key: Res<ButtonInput<KeyCode>>, mut exit: EventWriter<AppExit>) {
    if key.pressed(KeyCode::Escape) {
        exit.send(AppExit::Success);
    }
}
