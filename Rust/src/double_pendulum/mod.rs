mod rod;

use crate::double_pendulum::rod::RodPlugin;
use bevy::prelude::*;

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
        .add_plugins(RodPlugin)
        .add_systems(Startup, setup_system)
        .run();
}

fn setup_system(mut commands: Commands) {
    // Camera
    commands.spawn(Camera2dBundle::default());
}
