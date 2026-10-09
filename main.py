"""main.py - Tkinter window. Run this file:  python main.py"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import storage
import analysis
import visuals
import validation


class App:
    def __init__(self, root):
        self.root = root
        root.title("Rainfall Tracker")
        root.geometry("860x620")

        try:
            self.df = storage.load_records()       
        except Exception as error:
            messagebox.showerror("Error", str(error))
            self.df = storage.empty_table()
        self.shown = self.df                         
        self.last_compare = None                     

        self.make_widgets()
        self.refresh_table()

    def make_entry(self, parent, label, col, text="", width=12):
        ttk.Label(parent, text=label).grid(row=0, column=col, padx=4, pady=4)
        entry = ttk.Entry(parent, width=width)
        entry.insert(0, text)
        entry.grid(row=0, column=col + 1, padx=4)
        return entry

    def make_widgets(self):

        box = ttk.LabelFrame(self.root, text="Add observation")
        box.pack(fill="x", padx=8, pady=4)
        self.e_date = self.make_entry(box, "Date", 0, date.today().isoformat())
        self.e_loc = self.make_entry(box, "Location", 2)
        self.e_rain = self.make_entry(box, "Rainfall (mm)", 4)
        ttk.Button(box, text="Add", command=self.add_clicked).grid(row=0, column=6, padx=4)
        ttk.Button(box, text="Delete selected", command=self.delete_clicked).grid(row=0, column=7, padx=4)

        box = ttk.LabelFrame(self.root, text="Search / filter (dates: YYYY-MM-DD)")
        box.pack(fill="x", padx=8, pady=4)
        self.f_loc = self.make_entry(box, "Location", 0)
        self.f_start = self.make_entry(box, "From", 2)
        self.f_end = self.make_entry(box, "To", 4)
        ttk.Button(box, text="Search", command=self.filter_clicked).grid(row=0, column=6, padx=4)
        ttk.Button(box, text="Reset", command=self.reset_clicked).grid(row=0, column=7, padx=4)

        self.tree = ttk.Treeview(self.root, columns=("date", "location", "rain"),
                                 show="headings", height=12)
        self.tree.heading("date", text="Date")
        self.tree.heading("location", text="Location")
        self.tree.heading("rain", text="Rainfall (mm)")
        self.tree.pack(fill="both", expand=True, padx=8, pady=4)

        box = ttk.LabelFrame(self.root, text="Analysis")
        box.pack(fill="x", padx=8, pady=4)
        ttk.Button(box, text="Totals & Averages", command=self.summary_clicked).pack(side="left", padx=4, pady=4)
        ttk.Button(box, text="Highest / Lowest", command=self.extremes_clicked).pack(side="left", padx=4)

        box = ttk.LabelFrame(self.root, text="Compare two periods (YYYY-MM-DD)")
        box.pack(fill="x", padx=8, pady=4)
        self.p1_start = self.make_entry(box, "P1 from", 0)
        self.p1_end = self.make_entry(box, "to", 2)
        self.p2_start = self.make_entry(box, "P2 from", 4)
        self.p2_end = self.make_entry(box, "to", 6)
        ttk.Button(box, text="Compare", command=self.compare_clicked).grid(row=0, column=8, padx=4)

        box = ttk.LabelFrame(self.root, text="Charts")
        box.pack(fill="x", padx=8, pady=4)
        ttk.Button(box, text="Monthly", command=lambda: self.draw(visuals.monthly_chart)).pack(side="left", padx=4, pady=4)
        ttk.Button(box, text="Seasonal", command=lambda: self.draw(visuals.seasonal_chart)).pack(side="left", padx=4)
        ttk.Button(box, text="By location", command=lambda: self.draw(visuals.location_chart)).pack(side="left", padx=4)
        ttk.Button(box, text="Period comparison", command=self.comparison_chart_clicked).pack(side="left", padx=4)

    def get_filtered(self):
        """Read the filter boxes and return the matching records."""
        start = self.f_start.get().strip()
        end = self.f_end.get().strip()
        start = validation.check_date(start) if start else None
        end = validation.check_date(end) if end else None
        if start and end and start > end:
            raise ValueError("'From' date is after 'To' date")
        return analysis.filter_records(self.df, self.f_loc.get(), start, end)

    def refresh_table(self):
        try:
            self.shown = self.get_filtered()
        except ValueError:
            self.shown = self.df
        self.tree.delete(*self.tree.get_children())
        for index, row in self.shown.iterrows():
            self.tree.insert("", "end", iid=str(index),
                             values=(row["date"].date(), row["location"], row["rainfall_mm"]))

    def add_clicked(self):
        try:
            d = validation.check_past_date(self.e_date.get())
            location = validation.check_location(self.e_loc.get())
            rain = validation.check_rainfall(self.e_rain.get())
            new_df = storage.add_record(self.df, d, location, rain)
            storage.save_records(new_df)
        except ValueError as error:
            messagebox.showwarning("Invalid input", str(error))
            return
        except OSError as error:
            messagebox.showerror("Could not save", str(error))
            return
        self.df = new_df
        self.e_rain.delete(0, "end")
        self.refresh_table()

    def delete_clicked(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Please select a record first")
            return
        if not messagebox.askyesno("Confirm", "Delete the selected record?"):
            return
        try:
            new_df = storage.delete_record(self.df, int(selected[0]))
            storage.save_records(new_df)
        except (ValueError, OSError) as error:
            messagebox.showerror("Could not delete", str(error))
            return
        self.df = new_df
        self.refresh_table()

    def filter_clicked(self):
        try:
            self.get_filtered()
        except ValueError as error:
            messagebox.showwarning("Invalid filter", str(error))
            return
        self.refresh_table()

    def reset_clicked(self):
        for box in (self.f_loc, self.f_start, self.f_end):
            box.delete(0, "end")
        self.refresh_table()

    def summary_clicked(self):
        total, average = analysis.total_and_average(self.shown)
        text = (f"Records : {len(self.shown)}\n"
                f"Total   : {total:.1f} mm\n"
                f"Average : {average:.2f} mm")
        messagebox.showinfo("Totals & Averages (current search)", text)

    def extremes_clicked(self):
        high, low = analysis.highest_lowest(self.shown)
        if high is None:
            messagebox.showinfo("Highest / Lowest", "No records to check")
            return
        text = (f"Highest: {high['rainfall_mm']} mm  ({high['location']}, {high['date'].date()})\n"
                f"Lowest : {low['rainfall_mm']} mm  ({low['location']}, {low['date'].date()})")
        messagebox.showinfo("Highest / Lowest (current search)", text)

    def compare_clicked(self):
        try:
            s1 = validation.check_date(self.p1_start.get())
            e1 = validation.check_date(self.p1_end.get())
            s2 = validation.check_date(self.p2_start.get())
            e2 = validation.check_date(self.p2_end.get())
            if s1 > e1 or s2 > e2:
                raise ValueError("Each period must start before it ends")
        except ValueError as error:
            messagebox.showwarning("Invalid period", str(error))
            return
        r = analysis.compare_periods(self.df, s1, e1, s2, e2)
        self.last_compare = r
        percent = "n/a" if r["percent"] is None else f"{r['percent']:+.1f}%"
        text = (f"Period 1: total {r['total1']:.1f} mm, average {r['avg1']:.2f} mm\n"
                f"Period 2: total {r['total2']:.1f} mm, average {r['avg2']:.2f} mm\n"
                f"Difference: {r['difference']:+.1f} mm ({percent})")
        messagebox.showinfo("Period comparison", text)

    def draw(self, chart_function):
        try:
            chart_function(self.shown)
        except ValueError as error:
            messagebox.showwarning("Chart", str(error))

    def comparison_chart_clicked(self):
        if self.last_compare is None:
            messagebox.showinfo("Chart", "Press 'Compare' first")
            return
        visuals.comparison_chart(self.last_compare)


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()
