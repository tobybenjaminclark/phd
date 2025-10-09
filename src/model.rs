use std::error::Error;
use crate::{AircraftID, Sec, WakeCategory};
use plotters::prelude::*;
use plotters::style::text_anchor::{HPos, Pos, VPos};



const PX_PER_ROW: f64 = 50.0;
const PX_PER_SEC: f64 = 0.2;



/* Define a type to encapsulate an Aircraft, and it's associated ctot/time window constraints */
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Aircraft {
    pub id: AircraftID,
    pub time_window: (Sec, Sec),
    pub ctot_window: (Sec, Sec),
    pub ready_time: Sec,
    pub taxi_delay: Sec,
    pub wake: WakeCategory,
}



/* Define a type to encapsulate a full problem instance for the runway-schedulling problem */
pub struct Instance(pub Vec<Aircraft>);



impl Instance {
    pub fn visualise(&self, file: &str) -> Result<(), Box<dyn Error>> {

        let row_assignment = assign_rows_from_schedule(&self.0);
        let num_rows = 1 + *row_assignment.iter().max().unwrap_or(&0);

        let min_t = self.0.iter().map(|a| a.time_window.0 .0).min().unwrap_or(0) as f64;
        let max_t = self.0.iter().map(|a| a.time_window.1 .0).max().unwrap_or(2000) as f64;
        let time_span = (max_t - min_t).max(100.0);

        let (width, height) = (time_span * PX_PER_SEC, num_rows as f64 * PX_PER_ROW);

        let root = BitMapBackend::new(file, (width as u32, height as u32)).into_drawing_area();
        root.fill(&WHITE)?;

        // axis bounds with padding
        let x_min = (min_t - 50.0).max(0.0);
        let x_max = max_t + 100.0;
        let y_max = num_rows as f64 + 1.0;

        /* Create a master 'chart' object */
        let mut chart = ChartBuilder::on(&root)
            .caption("Runway Sequencing Instance", ("sans-serif", 16))
            .margin(20)
            .x_label_area_size(50)
            .y_label_area_size(80)
            .build_cartesian_2d(x_min..x_max, 0f64..y_max)?;

        chart
            .configure_mesh()
            .x_desc("Time (minutes)")
            .axis_desc_style(("sans-serif", 16))
            .label_style(("sans-serif", 14))
            .x_labels((max_t / 180.0) as usize)
            .x_label_formatter(&|x| format!("{:.0}m", (x / 60.0)))
            .y_labels(0)
            .draw()?;

        let base_font = ("sans-serif", 16).into_font().color(&BLACK);

        /* Draw each aircraft on it's assigned row */
        for (idx, ac) in self.0.iter().enumerate() {
            let row = row_assignment[idx] as f64;
            let y_center = y_max - row - 0.5;

            let start = ac.time_window.0 .0 as f64;
            let end = ac.time_window.1 .0 as f64;
            let ctot_start = ac.ctot_window.0 .0 as f64;
            let ctot_end = ac.ctot_window.1 .0 as f64;
            let ready = ac.ready_time.0 as f64;

            /* Draw a grey-bar to represent the hard time window */
            chart.draw_series(std::iter::once(Rectangle::new(
                [(start, y_center - 0.4), (end, y_center + 0.4)],
                RGBColor(219, 228, 238).filled(),
            )))?;

            /* Draw a blue bar to represent the CTOT window */
            if ctot_end > ctot_start {
                chart.draw_series(std::iter::once(Rectangle::new(
                    [(ctot_start, y_center - 0.35), (ctot_end, y_center + 0.35)],
                    RGBColor(129, 164, 205).filled(),
                )))?;
            }

            /* Draw an orange dot, connected to the time window (ready time) */
            chart.draw_series(std::iter::once(PathElement::new(vec![(ready, y_center), (start, y_center)], RGBColor(241, 115, 0))))?;
            chart.draw_series(std::iter::once(Circle::new((ready, y_center), 4, RGBColor(241, 115, 0).filled())))?;


            let (class_char, class_color) = match ac.wake {
                WakeCategory::Heavy => ("HVY", RGBColor(218, 65, 103)),
                WakeCategory::Medium => ("MDM", RGBColor(247, 135, 100)),
                WakeCategory::Light => ("LGT", RGBColor(244, 211, 94)),
            };

            chart.draw_series(std::iter::once(Text::new(
                format!("AC/{}", ac.id.0),
                ((start + end) / 2.0, y_center),
                base_font.pos(Pos::new(HPos::Right, VPos::Center)),
            )))?;

            chart.draw_series(std::iter::once(Text::new(
                format!("[{}]", class_char),
                ((start + end) / 2.0 + 20.0, y_center),
                base_font.color(&class_color).pos(Pos::new(HPos::Left, VPos::Center)),
            )))?;
        }

        root.present()?;
        Ok(())
    }
}



fn assign_rows_from_schedule(aircraft: &[Aircraft]) -> Vec<usize> {
    let mut indices: Vec<usize> = (0..aircraft.len()).collect();
    indices.sort_by(|&i, &j| {
        let a_start = aircraft[i].ready_time.0;
        let b_start = aircraft[j].ready_time.0;
        a_start.cmp(&b_start)
    });

    let mut rows: Vec<f64> = Vec::new();
    let mut result = vec![0; aircraft.len()];

    for &i in &indices {
        let start = aircraft[i].ready_time.0 as f64;
        let end = aircraft[i].time_window.1 .0 as f64;

        /* Find the first row whose last end < this start (non-overlap) */
        let mut placed = false;
        for (r, &row_end) in rows.iter().enumerate() {
            if start >= row_end {
                rows[r] = end;
                result[i] = r;
                placed = true;
                break;
            }
        }
        if !placed {
            rows.push(end);
            result[i] = rows.len() - 1;
        }
    }

    result
}