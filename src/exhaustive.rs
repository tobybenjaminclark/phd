use std::cmp::Ordering;
use crate::model::{Aircraft, Instance};
use crate::types::{WakeCategory, Sec, AircraftID};



/* Example ICAO-style wake separations (seconds) */
fn delta(prev: WakeCategory, next: WakeCategory) -> Sec {
    use WakeCategory::*;
    match (prev, next) {
        (Heavy, Heavy) => Sec(96),
        (Heavy, Medium) => Sec(120),
        (Heavy, Light) => Sec(144),
        (Medium, Heavy) => Sec(69),
        (Medium, Medium) => Sec(69),
        (Medium, Light) => Sec(82),
        (Light, Heavy) => Sec(60),
        (Light, Medium) => Sec(60),
        (Light, Light) => Sec(20),
    }
}



pub fn objective_function(seq: &[(Aircraft, Sec)]) -> i64 {
    0
}



fn compute_schedule(seq: &[Aircraft]) -> Option<Vec<(Aircraft, Sec)>> {
    if seq.is_empty() {
        return Some(Vec::new());
    }

    let mut schedule: Vec<(Aircraft, Sec)> = Vec::with_capacity(seq.len());

    let first = seq[0];
    let mut t_first = first.ready_time + first.taxi_delay;
    t_first = t_first.max(first.time_window.0);
    if t_first > first.time_window.1 {
        return None;
    }
    schedule.push((first, t_first));

    for i in 1..seq.len() {
        let ac_i = seq[i];
        let (tw_lo, tw_hi) = ac_i.time_window;
        let ready = ac_i.ready_time + ac_i.taxi_delay;

        let mut sep_term = i64::MIN;
        for (prev_ac, prev_t) in &schedule {
            let s = *prev_t + delta(prev_ac.wake, ac_i.wake);
            if s > Sec(sep_term as i32) {
                sep_term = s.0 as i64;
            }
        }

        let t_i = ready.max(Sec(sep_term as i32)).max(tw_lo);
        if t_i > tw_hi { return None; }
        schedule.push((ac_i, t_i));
    }

    Some(schedule)
}



pub fn exhaustive_search(instance: &Instance) -> Option<(Vec<(Aircraft, Sec)>, i64)> {
    let n = instance.0.len();
    if n == 0 {
        return Some((Vec::new(), 0));
    }

    let mut best_seq: Option<Vec<(Aircraft, Sec)>> = None;
    let mut best_score: i64 = i64::MAX;

    let mut buf = instance.0.clone();
    let mut c = vec![0usize; n];

    let mut evaluate_current = |order: &[Aircraft]| {
        if let Some(seq) = compute_schedule(order) {
            let score = objective_function(&seq);
            let better = match best_seq {
                None => true,
                Some(_) => score.cmp(&best_score) == Ordering::Less,
            };
            if better {
                best_score = score;
                best_seq = Some(seq);
            }
        }
    };

    evaluate_current(&buf);

    // Heap’s algorithm for permutations
    let mut i = 0usize;
    while i < n {
        if c[i] < i {
            if i % 2 == 0 {
                buf.swap(0, i);
            } else {
                buf.swap(c[i], i);
            }
            evaluate_current(&buf);
            c[i] += 1;
            i = 0;
        } else {
            c[i] = 0;
            i += 1;
        }
    }

    best_seq.map(|seq| (seq, best_score))
}



#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tiny_delta_example() {
        let acs = vec![
            Aircraft {
                id: 1,
                time_window: (100, 1000),
                ctot_window: (120, 250),
                ready_time: 80,
                taxi_delay: 10,
                wake: WakeCategory::Heavy,
            },
            Aircraft {
                id: 2,
                time_window: (150, 1200),
                ctot_window: (160, 350),
                ready_time: 90,
                taxi_delay: 20,
                wake: WakeCategory::Light,
            },
        ];
        let inst = Instance(acs);
        let (seq, score) = exhaustive_search(&inst).unwrap();
        println!("Best score {score}, schedule {:?}", seq);
        assert!(seq.len() == 2);
    }
}
