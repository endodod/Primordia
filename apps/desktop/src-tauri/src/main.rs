// Prevents an extra console window on Windows in release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use engine::World;
use serde::Serialize;
use std::sync::Mutex;
use tauri::State;

/// Phase 0: one shared world. Replaced by proper run management in Phase 1.
struct AppState {
    world: Mutex<World>,
}

#[derive(Serialize)]
struct Snapshot {
    tick: u64,
    hash: String,
    dots: Vec<(i64, i64)>,
}

/// Advances the world by `ticks` and returns a snapshot for rendering.
#[tauri::command]
fn step(state: State<'_, AppState>, ticks: u64) -> Result<Snapshot, String> {
    let mut world = state
        .world
        .lock()
        .map_err(|_| "world lock poisoned".to_string())?;
    world.step_n(ticks.min(10_000));
    Ok(Snapshot {
        tick: world.tick(),
        hash: format!("{:016x}", world.state_hash()),
        dots: world.dots().iter().map(|d| (d.x, d.y)).collect(),
    })
}

fn main() {
    tauri::Builder::default()
        .manage(AppState {
            world: Mutex::new(World::new(42, 50)),
        })
        .invoke_handler(tauri::generate_handler![step])
        .run(tauri::generate_context!())
        .expect("error while running Primordia");
}
