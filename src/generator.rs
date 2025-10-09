use rand::{Rng, SeedableRng};
use rand::prelude::IndexedRandom;
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use crate::types::{Sec, AircraftID, WakeCategory};
use crate::model::{Aircraft, Instance};



use WakeCategory::*;
const WAKES: [WakeCategory; 3] = [Heavy, Medium, Light];



pub fn generate_feasible_instance(n: usize, seed: Option<u64>) -> (Instance, Vec<Sec>) {
    let mut rng = StdRng::seed_from_u64(seed.unwrap_or(0));

    /* Spread readiness over the time horizon (prevent bunching to make feasible) */
    let base_step: i32 = rng.random_range(120..=180);
    let global_start: i32 = rng.random_range(300..=600);


    let mut aircraft: Vec<Aircraft> = (0..n)
        .map(|i| {
            let seg_start = global_start + (i as i32) * base_step;
            Aircraft {
                id: AircraftID(i as u32),
                time_window: (Sec(0), Sec(0)),
                ctot_window: (Sec(0), Sec(0)),
                ready_time: Sec(seg_start + rng.random_range(0..=(base_step / 2).max(1))),
                taxi_delay: Sec(rng.random_range(15..=45)),
                wake: *WAKES.choose(&mut rng).unwrap(),
            }
        })
        .collect();

    let δ = Instance(aircraft.clone()).build_separation_map();

    let mut order: Vec<usize> = (0..n).collect();
    order.shuffle(&mut rng);

    /* Schedule some 'feasible' takeoff times, with small stochastic gaps (with separations) */
    let mut times = vec![Sec(0); n];
    let first = order[0];
    let first_release = Sec(aircraft[first].ready_time.0 + aircraft[first].taxi_delay.0);
    let mut current = Sec(first_release.0);

    times[first] = current;

    for w in order.windows(2) {
        let i = w[0];
        let j = w[1];

        let ac_i = &aircraft[i];
        let ac_j = &aircraft[j];

        let sep = *δ.get(&(ac_i.id, ac_j.id)).unwrap();
        let release_j = Sec(ac_j.ready_time.0 + ac_j.taxi_delay.0);

        // Add a small stochastic inter-departure gap to reduce clumping
        let extra_gap = rng.gen_range(30..=120);

        current = Sec(
            current.0
                .max(times[i].0 + sep.0)
                .max(release_j.0)
                + extra_gap,
        );

        times[j] = current;
    }

    /* Assign realistic time windows around scheduled takeoffs */
    for (i, ac) in aircraft.iter_mut().enumerate() {
        let t = times[i].0;

        /* Set the hard time window (25 - 30mins) */
        let time_width = rng.gen_range(1500..=2100);
        let time_half = time_width / 2;
        ac.time_window = (Sec(t - time_half), Sec(t + time_half));

        /* Set the CTOT slot (15 minutes) */
        let ctot_half = 450;
        ac.ctot_window = (Sec(t - ctot_half), Sec(t + ctot_half));

        /* Set the ready time (upto 5 minutes before hard time window */
        let pre = rng.gen_range(0..=300);
        ac.ready_time = Sec(ac.time_window.0 .0 - pre);
    }

    /* Global offset to prevent negative time indicies */
    const MIN_MARGIN: i32 = 60; // want everything ≥ 60s past T0
    let min_ready   = aircraft.iter().map(|a| a.ready_time.0).min().unwrap_or(0);
    let min_tw      = aircraft.iter().map(|a| a.time_window.0 .0).min().unwrap_or(0);
    let min_ctot    = aircraft.iter().map(|a| a.ctot_window.0 .0).min().unwrap_or(0);
    let min_t       = times.iter().map(|t| t.0).min().unwrap_or(0);

    let earliest = *[min_ready, min_tw, min_ctot, min_t].iter().min().unwrap();
    let offset = if earliest < MIN_MARGIN { MIN_MARGIN - earliest } else { 0 };

    if offset > 0 {
        for t in &mut times { t.0 += offset; }

        for a in &mut aircraft {
            a.ready_time.0 += offset;
            a.time_window.0 .0 += offset;
            a.time_window.1 .0 += offset;
            a.ctot_window.0 .0 += offset;
            a.ctot_window.1 .0 += offset;
        }
    }

    (Instance(aircraft), times)
}
