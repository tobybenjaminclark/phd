use phd::generator::generate_feasible_instance;

fn main() {
    println!("Hello, world!");
    let ((inst), secs) = generate_feasible_instance(40, Some(5));
    for (ac) in &inst.0 {
        println!("{:?}", ac);
    }
    inst.visualise("instance.png").unwrap();
}