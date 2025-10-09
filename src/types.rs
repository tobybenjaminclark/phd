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



/* Define a type to encapsulate ICAO wake turbulence categories, in real-world these may be more complex */
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum WakeCategory { Heavy, Medium, Light }