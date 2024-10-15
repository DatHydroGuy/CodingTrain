mod epicycles;

use crate::fourier_series::epicycles::*;
use bevy::prelude::*;
use bevy_vector_shapes::prelude::*;
// https://github.com/james-j-obrien/bevy_vector_shapes/blob/main/examples/gallery_3d.rs

const SCREEN_WIDTH: f32 = 1500.0;
const SCREEN_HEIGHT: f32 = 1000.0;

pub(crate) fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.05, 0.0, 0.1)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Bevy Fourier Transform".into(),
                resolution: (SCREEN_WIDTH, SCREEN_HEIGHT).into(),
                // you can position the window here if you like, as follows:
                position: WindowPosition::At(IVec2::new(200, 50)),
                ..Default::default()
            }),
            ..Default::default()
        }))
        .add_plugins(Shape2dPlugin::default())
        .add_plugins(EpicyclesPlugin)
        .add_systems(Startup, setup_system)
        .run();
}

fn setup_system(mut commands: Commands) {
    // Camera
    commands
        .spawn(Camera2dBundle::default())
        .insert(Epicycle::new(-250.0, 0.0, 150.0));
}
