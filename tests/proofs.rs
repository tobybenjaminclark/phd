use itertools::sorted;
use z3::{ast::*, SatResult, Solver, Sort};

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



#[test]
fn proof_list_ordering() {
    let solver = Solver::new();

    let (L, LP) = (
        Array::fresh_const("α", &Sort::int(), &Sort::int()),
        Array::fresh_const("β", &Sort::int(), &Sort::int())
    );

    let (α, β, γ) = (
        Int::fresh_const("α"),
        Int::fresh_const("β"),
        Int::fresh_const("γ"),
    );

    solver.assert(γ.gt(Int::from_i64(0)));

    let list_sorted = |arr: &Array, n: &Int| {
        let ξ = Int::fresh_const("ξ");
        let zero = Int::from_i64(0);
        let one = Int::from_i64(1);

        /* antecedent: 0 ≤ j ∧ j + 1 < n */
        let ante = Bool::and(&[
            ξ.ge(&zero),
            (&ξ + &one).lt(n),
        ]);

        let ξL = arr.select(&ξ).as_int().expect("Not integer!");
        let ξLi = arr.select(&(&ξ + &one)).as_int().expect("Not integer!");
        let conseq = &ξL.le(&ξLi);

        /* ∀ j. (0 ≤ j ∧ j + 1 < len) ⇒ arr[j] ≤ arr[j+1] */
        forall_const(
            &[&ξ],
            &[],
            &ante.implies(conseq)
        )
    };

    solver.assert(forall_const(
        &[&α],
        &[],
        &Bool::implies(
            &α.eq(Int::from_i64(0)),
            L.select(&α).eq(&γ)
        )
    ));

    solver.assert(forall_const(
        &[&α],
        &[],
        &Bool::implies(
            &α.gt(Int::from_i64(0)),
            L.select(&α).eq(LP.select(&(&α + Int::from_i64(1))))
        )
    ));

    let zero = &Int::from_i64(0);
    let goal = Bool::and(&[
        list_sorted(&L, &γ),
        α.lt(L.select(zero).as_int().expect("Not integer!")),
        Bool::not(&list_sorted(&LP, &(&γ + &Int::from_i64(1))))
    ]);

    solver.assert(&goal);
    match solver.check() {
        SatResult::Sat => assert!(true),
        _ => assert!(false),
    }
}
