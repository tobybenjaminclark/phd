use std::collections::HashMap;
use crate::types::{Sec, WakeCategory, AircraftID};
use crate::model::{Instance};
use itertools::Itertools;


/* Function to generate icao separations from two wake categories */
pub fn icao_sep_seconds(leader: WakeCategory, follower: WakeCategory) -> i32 {
    use WakeCategory::*;
    match (leader, follower) {
        (Heavy, Heavy) => 96, (Heavy, Medium) => 96, (Heavy, Light) => 109,
        (Medium, Heavy) => 69, (Medium, Medium) => 69, (Medium, Light) => 82,
        (Light, Heavy) => 60, (Light, Medium) => 60, (Light, Light) => 69,
    }
}



/* Function to generate a time separation matrix between aircraft (based on wake categories */
impl Instance {
    pub fn build_separation_map(&self) -> HashMap<(AircraftID, AircraftID), Sec> {
        self.0
            .iter()
            .cartesian_product(self.0.iter())
            .map(|(a, b)| {
                let sep = if a.id == b.id { Sec(0) }
                else { Sec(icao_sep_seconds(a.wake, b.wake)) };
                ((a.id, b.id), sep)
            })
            .collect()
    }
}
