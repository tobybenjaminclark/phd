use std::ops::{Add, Sub};



/* Define a type to denote seconds, prevents mixing with other numerical quantities */
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Sec(pub i32);

impl Add for Sec { type Output = Sec; fn add(self, rhs: Sec) -> Sec { Sec(self.0 + rhs.0) } }
impl Sub for Sec { type Output = Sec; fn sub(self, rhs: Sec) -> Sec { Sec(self.0 - rhs.0) } }
impl From<i32> for Sec { fn from(s: i32) -> Self { Sec(s) } }



/* Define a type to denote a unique aircraft identifier, prevents mixing with other numerical quantities */
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct AircraftID(pub u32);



/* Define a type to encapsulate an Aircraft, and it's associated ctot/time window constraints */
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Aircraft {
    pub id: AircraftID,
    pub time_window: (Sec, Sec),
    pub ctot_window: (Sec, Sec),
    pub ready_time: Sec,
    pub taxi_delay: Sec,
}



/* Define a type to encapsulate a Problem Instance, it's aircraft and delta values */
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct RSPInstance {
    pub aircraft: Vec<Aircraft>,
    pub δ: HashMap<(AircraftID, AircraftID), f64>,
}