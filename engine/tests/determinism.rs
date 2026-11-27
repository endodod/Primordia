//! Determinism tests. CI runs these on Windows, macOS and Linux; every platform must produce
//! the golden hashes in `tests/fixtures/golden-hashes.txt`.
//!
//! When an intentional outcome change bumps ENGINE_VERSION, regenerate with:
//! `UPDATE_GOLDEN=1 cargo test -p primordia-engine --test determinism`

use engine::World;
use std::path::PathBuf;

const CASES: &[(u64, usize, u64)] = &[(0, 10, 1_000), (42, 100, 5_000), (u64::MAX, 500, 2_000)];

fn golden_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/golden-hashes.txt")
}

fn run(seed: u64, dots: usize, ticks: u64) -> u64 {
    let mut world = World::new(seed, dots);
    world.step_n(ticks);
    world.state_hash()
}

#[test]
fn same_seed_same_result() {
    for &(seed, dots, ticks) in CASES {
        assert_eq!(run(seed, dots, ticks), run(seed, dots, ticks));
    }
}

#[test]
fn different_seed_different_result() {
    assert_ne!(run(1, 50, 100), run(2, 50, 100));
}

#[test]
fn matches_golden_hashes() {
    let actual: Vec<String> = CASES
        .iter()
        .map(|&(seed, dots, ticks)| {
            format!("{seed} {dots} {ticks} {:016x}", run(seed, dots, ticks))
        })
        .collect();

    if std::env::var("UPDATE_GOLDEN").is_ok() {
        std::fs::write(golden_path(), actual.join("\n") + "\n").expect("write golden file");
        return;
    }

    let golden = std::fs::read_to_string(golden_path()).expect("read golden file");
    let expected: Vec<&str> = golden.lines().filter(|l| !l.is_empty()).collect();
    assert_eq!(
        actual, expected,
        "state hashes differ from golden file — determinism broken or ENGINE_VERSION change \
         needs a golden update"
    );
}
