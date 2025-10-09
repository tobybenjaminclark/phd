use z3::{ast::*, SatResult, Solver};



#[test]
fn proof_addition_commutative() {
    let solver = Solver::new();

    let α = Int::fresh_const("α");
    let β = Int::fresh_const("β");

    let formula = (&α + &β).ne(&β + &α);
    let exists = exists_const(&[&α, &β], &[], &formula);

    solver.assert(&exists);
    match solver.check() {
        SatResult::Unsat => println!("Proved: ¬∃ (α, β) | α + β ≠ β + α"),
        _ => assert!(false),
    }
}



#[test]
fn proof_addition_asociative() {
    let solver = Solver::new();

    let α = Int::fresh_const("α");
    let β = Int::fresh_const("β");
    let γ = Int::fresh_const("γ");

    let formula = ((&α + &β) + &γ).ne(&α + (&β + &γ));
    let exists = exists_const(&[&α, &β, &γ], &[], &formula);

    solver.assert(&exists);
    match solver.check() {
        SatResult::Unsat => println!("Proved: ¬∃ (α, β, γ) | (α + β) + γ ≠ α + (β + γ)"),
        _ => assert!(false),
    }
}



#[test]
fn proof_addition_identity() {
    let solver = Solver::new();

    let α = Int::fresh_const("α");
    let zero = Int::from_i64(0);

    let formula = (&α + &zero).ne(&α);
    let exists = exists_const(&[&α], &[], &formula);

    solver.assert(&exists);
    match solver.check() {
        SatResult::Unsat => println!("Proved: ¬∃ α | (α + 0) ≠ 0"),
        _ => assert!(false),
    }
}



#[test]
fn proof_addition_inverse() {
    let solver = Solver::new();

    let α = Int::fresh_const("α");
    let zero = Int::from_i64(0);

    let formula = (&α + (&zero - &α)).ne(&zero);
    let exists = exists_const(&[&α], &[], &formula);

    solver.assert(&exists);
    match solver.check() {
        SatResult::Unsat => println!("Proved: ¬∃ α | (α + -a) ≠ 0"),
        _ => assert!(false),
    }
}



#[test]
fn proof_addition_distributive() {
    let solver = Solver::new();

    let α = Int::fresh_const("α");
    let β = Int::fresh_const("β");
    let γ = Int::fresh_const("γ");

    let formula = (&α * (&β + &γ)).ne((&α * &β) + (&α * &γ));
    let exists = exists_const(&[&α, &β, &γ], &[], &formula);

    solver.assert(&exists);
    match solver.check() {
        SatResult::Unsat => println!("Proved: ¬∃ (α, β, γ) | α * (β + γ) ≠ (α * β) + (α * γ)"),
        _ => assert!(false),
    }
}