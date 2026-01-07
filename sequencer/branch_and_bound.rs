



// Node is not a full schedule, it is a partial sequence
// Branch off node with all feasible next steps

// You already know delay cost, CTOT violation, runway-hold contribution

// Bound, if I finish perfectly, how cheap could it be?

// Keep track of a complete schedule (the incumbent)
// Compare the lower bound to the total of the complete schedule
// No completion of what I am working on can beat what I have (give up)

// When you reach another full schedule that beats it, that takes priority

const REMAINING: Vec<Aircraft> = vec![];

pub fn bound(partial: [Aircraft]) -> f64 {
    /* Assume all delta */

}

pub fn branch(partial: [Aircraft]) -> Result<[Aircraft]> {
    lb = lower_bound(partial)?;
}