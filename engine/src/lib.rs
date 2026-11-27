//! Primordia simulation engine.
//!
//! Pure and deterministic: the same seed and inputs produce a bit-identical world on every
//! platform. No I/O, no rendering, no wall-clock time, no threads inside a run.
//!
//! Phase 0 skeleton: a handful of dots doing a seeded random walk on an integer grid.
//! Integer math only until the numeric strategy is decided (ADR-0002, Phase 1).

use rand_chacha::ChaCha8Rng;
use rand_core::{RngCore, SeedableRng};

/// Bump whenever a change alters simulation outcomes for the same inputs.
pub const ENGINE_VERSION: u32 = 1;

/// Size of the square world in grid units.
pub const WORLD_SIZE: i64 = 1_000;

/// A single agent. Will become a creature with a genome in Phase 1.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Dot {
    pub x: i64,
    pub y: i64,
}

/// The simulation state.
#[derive(Debug, Clone)]
pub struct World {
    rng: ChaCha8Rng,
    tick: u64,
    dots: Vec<Dot>,
}

impl World {
    /// Creates a world with `count` dots placed from the seeded RNG.
    pub fn new(seed: u64, count: usize) -> Self {
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        let dots = (0..count)
            .map(|_| Dot {
                x: i64::from(rng.next_u32()) % WORLD_SIZE,
                y: i64::from(rng.next_u32()) % WORLD_SIZE,
            })
            .collect();
        Self { rng, tick: 0, dots }
    }

    /// Advances the simulation by one fixed tick.
    pub fn step(&mut self) {
        for dot in &mut self.dots {
            let r = self.rng.next_u32();
            let dx = i64::from(r % 3) - 1;
            let dy = i64::from((r / 3) % 3) - 1;
            dot.x = (dot.x + dx).rem_euclid(WORLD_SIZE);
            dot.y = (dot.y + dy).rem_euclid(WORLD_SIZE);
        }
        self.tick += 1;
    }

    /// Advances the simulation by `n` ticks.
    pub fn step_n(&mut self, n: u64) {
        for _ in 0..n {
            self.step();
        }
    }

    /// Number of ticks simulated so far.
    pub fn tick(&self) -> u64 {
        self.tick
    }

    /// Current agents.
    pub fn dots(&self) -> &[Dot] {
        &self.dots
    }

    /// Stable FNV-1a hash of the full simulation state, used by determinism tests.
    pub fn state_hash(&self) -> u64 {
        const OFFSET: u64 = 0xcbf2_9ce4_8422_2325;
        const PRIME: u64 = 0x0000_0100_0000_01b3;
        let mut hash = OFFSET;
        let mut feed = |bytes: &[u8]| {
            for b in bytes {
                hash ^= u64::from(*b);
                hash = hash.wrapping_mul(PRIME);
            }
        };
        feed(&ENGINE_VERSION.to_le_bytes());
        feed(&self.tick.to_le_bytes());
        for dot in &self.dots {
            feed(&dot.x.to_le_bytes());
            feed(&dot.y.to_le_bytes());
        }
        hash
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dots_stay_inside_world() {
        let mut world = World::new(7, 100);
        world.step_n(1_000);
        assert!(world
            .dots()
            .iter()
            .all(|d| (0..WORLD_SIZE).contains(&d.x) && (0..WORLD_SIZE).contains(&d.y)));
    }

    #[test]
    fn tick_counts_up() {
        let mut world = World::new(1, 1);
        world.step_n(5);
        assert_eq!(world.tick(), 5);
    }
}
