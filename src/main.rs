use phd::generator::generate_feasible_instance;
use z3::{Config, Context, Solver, SatResult, ast::Int, FuncDecl, Sort, ast, Pattern};

fn main() {
    println!("Hello, world!");

    let solver = Solver::new();

    let x = ast::Int::fresh_const("x");
    
    let zero = ast::Int::from_i64(0);
    let formula = (&x * &zero).eq(&zero).not();

    let exists = ast::exists_const(&[&x], &[], &formula);

    solver.assert(&exists);

    match solver.check() {
        SatResult::Unsat => println!("Proved: ∀x. x * 0 = 0 ✅"),
        SatResult::Sat => println!("Counterexample exists ❌"),
        SatResult::Unknown => println!("Z3 gave up 🤷"),
    }


    let ((inst), secs) = generate_feasible_instance(40, Some(5));
    for (ac) in &inst.0 {
        println!("{:?}", ac);
    }
    inst.visualise("instance.png").unwrap();
}