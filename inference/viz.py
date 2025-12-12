from dataclasses import dataclass

from matplotlib import pyplot as plt

from cegis import *



@dataclass(frozen=True)
class PopulationSnapshot:
    round_no: int
    population: list            # list[BooleanExpr]
    fitness: list               # list[(expr, score, t1, t2, t3)]
    avg_score: float
    best_score: float

from matplotlib.widgets import Slider, Button



class PopulationBrowser:
    def __init__(self):
        self.snapshots: list[PopulationSnapshot] = []
        self.current = 0

        self.fig = plt.figure(figsize=(12, 8))

        # layout
        self.ax_table = self.fig.add_axes([0.05, 0.25, 0.6, 0.7])
        self.ax_plot  = self.fig.add_axes([0.7, 0.25, 0.25, 0.7])
        self.ax_slider = self.fig.add_axes([0.1, 0.1, 0.6, 0.05])

        self.slider = Slider(self.ax_slider, "Round", 0, 0, valinit=0, valstep=1)
        self.slider.on_changed(self._on_slider)

    def on_population_snapshot(self, round_no, pop, fitpop, avg_score, best_score):
        snap = PopulationSnapshot(
            round_no=round_no,
            population=pop,
            fitness=fitpop,
            avg_score=avg_score,
            best_score=best_score,
        )
        self.snapshots.append(snap)

        self.slider.valmax = len(self.snapshots) - 1
        self.slider.ax.set_xlim(0, self.slider.valmax)

        self.current = len(self.snapshots) - 1
        self.slider.set_val(self.current)

        self.redraw()

    def redraw_table(self, snap: PopulationSnapshot):
        self.ax_table.clear()
        self.ax_table.axis("off")

        rows = []
        for i, (expr, sc, t1, t2, t3) in enumerate(
            sorted(snap.fitness, key=lambda x: x[1], reverse=True)
        ):
            rows.append([
                i,
                f"{sc:.3f}",
                f"{t1:.2f}",
                f"{t2:.2f}",
                f"{t3:.2f}",
                str(expr)[:60],  # truncate
            ])

        table = self.ax_table.table(
            cellText=rows,
            colLabels=["#", "Score", "CE%", "Size%", "MC%", "Rule"],
            loc="center",
        )
        table.scale(1, 1.3)

    def redraw_plot(self):
        self.ax_plot.clear()
        avgs = [s.avg_score for s in self.snapshots]
        bests = [s.best_score for s in self.snapshots]

        self.ax_plot.plot(avgs, label="avg score")
        self.ax_plot.plot(bests, label="best score")
        self.ax_plot.set_title("Score over CEGIS rounds")
        self.ax_plot.legend()

    def redraw(self):
        snap = self.snapshots[self.current]
        self.redraw_table(snap)
        self.redraw_plot()
        self.fig.canvas.draw_idle()

    def _on_slider(self, val):
        self.current = int(val)
        self.redraw()

if __name__ == "__main__":
    vis = PopulationBrowser()

    cegis = CEGIS(
        form,
        max_rounds=250,
        starting=10,
        generations=25,
        elite=4,
        visualiser=vis,
    )

    cegis.synthesise()
    plt.show()
