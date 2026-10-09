import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
from datetime import date, timedelta


STATS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "pixelpal_stats.json",
)

DEFAULT_STATS = {
    "xp": 0,
    "level": 1,
    "total_sessions": 0,
    "total_minutes": 0,
    "current_streak": 0,
    "last_session_date": None,
    "daily_minutes": {},
}

TIER_COLORS = [
    (1, 2, "#8BC34A"),      # Green Hatchling
    (3, 5, "#42A5F5"),      # Blue Apprentice
    (6, 9, "#AB47BC"),      # Purple Focus Adept
    (10, 999, "#FFC107"),   # Gold Focus Master
]


def body_color_for_level(level: int):
    for lo, hi, color in TIER_COLORS:
        if lo <= level <= hi:
            return color
    return TIER_COLORS[-1][2]


class PixelPalApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.stats = self.load_stats()

        # Timer state
        self.session_minutes = 25
        self.break_minutes = 5
        self.remaining = self.session_minutes * 60
        self.on_break = False
        self.running = False
        self.after_id = None

        # Mood state
        self.mood = "idle"
        self.mood_revert_id = None

        # Window drag state
        self.drag_x = 0
        self.drag_y = 0

        self._check_sleepy_on_start()
        self._build_window()
        self._draw_face()
        self._update_timer_label()

    # -------------------- Data --------------------
    def load_stats(self) -> dict:
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                merged = DEFAULT_STATS.copy()
                merged.update(data)

                # Support an older spelling if an earlier version created it.
                if (
                    merged.get("last_session_date") is None
                    and data.get("last_Session_date") is not None
                ):
                    merged["last_session_date"] = data["last_Session_date"]

                if not isinstance(merged.get("daily_minutes"), dict):
                    merged["daily_minutes"] = {}

                return merged

            except (json.JSONDecodeError, OSError):
                pass

        return DEFAULT_STATS.copy()

    def save_stats(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=4)
        except OSError as exc:
            messagebox.showerror(
                "Save Error",
                f"Could not save statistics:\n{exc}",
            )

    def _check_sleepy_on_start(self):
        last = self.stats.get("last_session_date")

        if last is None:
            self.mood = "sleepy"
            return

        try:
            last_date = date.fromisoformat(last)
        except ValueError:
            self.mood = "sleepy"
            return

        if (date.today() - last_date).days >= 2:
            self.mood = "sleepy"

    # -------------------- Window --------------------
    def _build_window(self):
        root = self.root
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        try:
            root.attributes("-alpha", 0.96)
        except tk.TclError:
            pass

        w, h = 220, 300
        sw = root.winfo_screenwidth()
        root.geometry(f"{w}x{h}+{sw - w - 40}+60")

        self.frame = tk.Frame(root, bg="#1E1E2E", bd=0)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.frame,
            width=200,
            height=170,
            bg="#1E1E2E",
            highlightthickness=0,
        )
        self.canvas.pack(pady=(8, 0))

        self.timer_label = tk.Label(
            self.frame,
            text="25:00",
            font=("Consolas", 20, "bold"),
            bg="#1e1e2e",
            fg="white",
        )
        self.timer_label.pack(pady=(4, 0))

        self.level_label = tk.Label(
            self.frame,
            text=self._level_text(),
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#b0bec5",
        )
        self.level_label.pack()

        btn_row = tk.Frame(self.frame, bg="#1E1e2e")
        btn_row.pack(pady=8)

        self.start_btn = self._make_btn(
            btn_row, "▶", self.toggle_timer
        )
        self._make_btn(btn_row, "↺", self.reset_timer)
        self._make_btn(btn_row, "◌", self.open_settings)
        self._make_btn(btn_row, "📊", self.open_dashboard)
        self._make_btn(btn_row, "X", self.close_app)

        # Context menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(
            label="Dashboard",
            command=self.open_dashboard,
        )
        self.context_menu.add_command(
            label="Settings",
            command=self.open_settings,
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Quit PixelPal",
            command=self.close_app,
        )

        # Dragging the window by clicking anywhere on it
        for widget in (
            self.frame,
            self.canvas,
            self.timer_label,
            self.level_label,
        ):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._do_drag)
            widget.bind("<Button-3>", self._show_context_menu)

    def _make_btn(self, parent, text, cmd):
        button = tk.Button(
            parent,
            text=text,
            command=cmd,
            width=3,
            bg="#2e2e3e",
            fg="white",
            activebackground="#3e3e4e",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10),
        )
        button.pack(side="left", padx=2)
        return button

    def _level_text(self):
        s = self.stats
        return f"Lv.{s['level']} 🔥 {s['current_streak']}d XP:{s['xp']}"

    def _start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def _do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def close_app(self):
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        if self.mood_revert_id is not None:
            try:
                self.root.after_cancel(self.mood_revert_id)
            except tk.TclError:
                pass
            self.mood_revert_id = None

        self.root.destroy()

    # -------------------- Face / Mood --------------------
    def _draw_face(self):
        c = self.canvas
        c.delete("all")

        color = body_color_for_level(self.stats["level"])
        cx, cy, r = 100, 85, 70

        # Body
        c.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            fill=color,
            outline="",
        )

        # Face depends on mood
        if self.mood == "sleepy":
            c.create_line(
                cx - 35, cy - 10,
                cx - 15, cy - 10,
                width=4,
                fill="#1e1e2e",
            )
            c.create_line(
                cx + 15, cy - 10,
                cx + 35, cy - 10,
                width=4,
                fill="#1e1e2e",
            )
            c.create_text(
                cx + 45,
                cy - 45,
                text="z,z",
                font=("Segoe UI", 14, "italic"),
                fill="white",
            )
            c.create_arc(
                cx - 20,
                cy + 5,
                cx + 20,
                cy + 25,
                start=200,
                extent=140.4,
                style="arc",
                width=3,
                outline="#1e1e2e",
            )

        elif self.mood == "focused":
            c.create_oval(
                cx - 32, cy - 15,
                cx - 18, cy - 1,
                fill="#1e1e2e",
                outline="",
            )
            c.create_oval(
                cx + 18, cy - 15,
                cx + 32, cy - 1,
                fill="#1e1e2e",
                outline="",
            )
            c.create_line(
                cx - 15, cy + 25,
                cx + 15, cy + 25,
                width=3,
                fill="#1e1e2e",
            )

        elif self.mood == "excited":
            c.create_oval(
                cx - 34, cy - 18,
                cx - 14, cy + 2,
                fill="#1e1e2e",
                outline="",
            )
            c.create_oval(
                cx + 14, cy - 18,
                cx + 34, cy + 2,
                fill="#1e1e2e",
                outline="",
            )
            c.create_arc(
                cx - 22, cy + 5,
                cx + 22, cy + 35,
                start=200,
                extent=140,
                style="chord",
                fill="#1e1e2e",
                outline="",
            )

            for sx, sy in [
                (cx - 55, cy - 55),
                (cx + 55, cy - 60),
                (cx + 60, cy),
            ]:
                c.create_text(
                    sx,
                    sy,
                    text="✦",
                    font=("Segoe UI", 12),
                    fill="#ffd54f",
                )

        elif self.mood == "happy":
            c.create_oval(
                cx - 32, cy - 16,
                cx - 18, cy - 2,
                fill="#1e1e2e",
                outline="",
            )
            c.create_oval(
                cx + 18, cy - 16,
                cx + 32, cy - 2,
                fill="#1e1e2e",
                outline="",
            )
            c.create_arc(
                cx - 20, cy + 2,
                cx + 20, cy + 28,
                start=200,
                extent=140,
                style="arc",
                width=3,
                outline="#1e1e2e",
            )

        else:
            # Idle / neutral
            c.create_oval(
                cx - 32, cy - 15,
                cx - 18, cy - 1,
                fill="#1e1e2e",
                outline="",
            )
            c.create_oval(
                cx + 18, cy - 15,
                cx + 32, cy - 1,
                fill="#1e1e2e",
                outline="",
            )
            c.create_line(
                cx - 15, cy + 18,
                cx + 15, cy + 18,
                width=2,
                fill="#1e1e2e",
            )

    def _set_mood(
        self,
        mood,
        revert_after_ms=None,
        revert_to="idle",
    ):
        self.mood = mood
        self._draw_face()

        if self.mood_revert_id is not None:
            try:
                self.root.after_cancel(self.mood_revert_id)
            except tk.TclError:
                pass
            self.mood_revert_id = None

        if revert_after_ms is not None:
            self.mood_revert_id = self.root.after(
                revert_after_ms,
                lambda: self._set_mood(revert_to),
            )

    # -------------------- Timer --------------------
    def toggle_timer(self):
        if self.running:
            self.running = False
            self.start_btn.config(text="▶")

            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except tk.TclError:
                    pass
                self.after_id = None

            self._set_mood("idle")
            return

        # If a break is currently displayed, pressing Start starts
        # the break countdown.
        self.running = True
        self.start_btn.config(text="⏸")
        self._set_mood("focused" if not self.on_break else "idle")
        self._tick()

    def reset_timer(self):
        self.running = False
        self.on_break = False
        self.start_btn.config(text="▶")

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        self.remaining = self.session_minutes * 60
        self._set_mood("idle")
        self._update_timer_label()

    def _tick(self):
        if not self.running:
            self.after_id = None
            return

        self.remaining -= 1
        self._update_timer_label()

        if self.remaining <= 0:
            self.after_id = None

            if self.on_break:
                self._end_break()
            else:
                self._complete_focus_session()
        else:
            self.after_id = self.root.after(1000, self._tick)

    def _update_timer_label(self):
        mins, secs = divmod(max(self.remaining, 0), 60)
        prefix = "☕ " if self.on_break else ""
        self.timer_label.config(
            text=f"{prefix}{mins:02d}:{secs:02d}"
        )

    # -------------------- Sessions / Stats --------------------
    def _complete_focus_session(self):
        self.running = False
        self.start_btn.config(text="▶")

        minutes = self.session_minutes
        self._update_stats_after_session(minutes)

        self._set_mood(
            "excited",
            revert_after_ms=3000,
            revert_to="happy",
        )

        self._show_toast(
            f"Session complete! +{minutes * 2} XP"
        )

        # Move into a break.
        self.on_break = True
        self.remaining = self.break_minutes * 60
        self._update_timer_label()

    def _end_break(self):
        self.running = False
        self.on_break = False
        self.start_btn.config(text="▶")
        self.remaining = self.session_minutes * 60
        self._set_mood("idle")
        self._update_timer_label()

    def _update_stats_after_session(self, minutes):
        s = self.stats
        today = date.today()
        today_str = today.isoformat()

        old_level = s["level"]

        s["total_sessions"] += 1
        s["total_minutes"] += minutes

        s["daily_minutes"][today_str] = (
            s["daily_minutes"].get(today_str, 0) + minutes
        )

        last = s.get("last_session_date")

        if last == today_str:
            # Already completed a session today.
            # The streak remains unchanged.
            pass
        elif last == (today - timedelta(days=1)).isoformat():
            s["current_streak"] += 1
        else:
            s["current_streak"] = 1

        s["last_session_date"] = today_str

        # 2 XP per focused minute.
        s["xp"] += minutes * 2
        s["level"] = s["xp"] // 100 + 1

        self.save_stats()
        self.level_label.config(text=self._level_text())
        self._draw_face()

        if s["level"] > old_level:
            self.root.after(
                500,
                lambda: messagebox.showinfo(
                    "Level Up!",
                    f"PixelPal reached Level {s['level']}! 🎉",
                ),
            )

    def _show_toast(self, text):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        x = self.root.winfo_x()
        y = max(0, self.root.winfo_y() - 45)

        toast.geometry(f"200x40+{x}+{y}")

        tk.Label(
            toast,
            text=text,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9, "bold"),
        ).pack(fill="both", expand=True)

        toast.after(2200, toast.destroy)

    # -------------------- Settings --------------------
    def open_settings(self):
        new_len = simpledialog.askinteger(
            "Settings",
            "Focus session length (minutes):",
            initialvalue=self.session_minutes,
            minvalue=1,
            maxvalue=180,
            parent=self.root,
        )

        if new_len is not None:
            self.session_minutes = new_len

            if not self.running and not self.on_break:
                self.remaining = self.session_minutes * 60

            self._update_timer_label()

        new_break = simpledialog.askinteger(
            "Settings",
            "Break length (minutes):",
            initialvalue=self.break_minutes,
            minvalue=1,
            maxvalue=60,
            parent=self.root,
        )

        if new_break is not None:
            self.break_minutes = new_break

            if self.on_break and not self.running:
                self.remaining = self.break_minutes * 60
                self._update_timer_label()

    # -------------------- Dashboard --------------------
    def open_dashboard(self):
        win = tk.Toplevel(self.root)
        win.title("PixelPal Stats")
        win.geometry("340x260")
        win.attributes("-topmost", True)
        win.configure(bg="#1e1e2e")

        s = self.stats

        header = (
            f"Level {s['level']} | "
            f"{s['total_sessions']} sessions | "
            f"{s['total_minutes']} total minutes | "
            f"streak {s['current_streak']}d"
        )

        tk.Label(
            win,
            text=header,
            bg="#1e1e2e",
            fg="white",
            font=("Segoe UI", 9),
            wraplength=320,
        ).pack(pady=(10, 5))

        chart = tk.Canvas(
            win,
            width=320,
            height=180,
            bg="#2a2a3a",
            highlightthickness=0,
        )
        chart.pack(pady=5)

        self._draw_bar_chart(chart)

    def _draw_bar_chart(self, chart: tk.Canvas):
        days = [
            date.today() - timedelta(days=i)
            for i in range(6, -1, -1)
        ]

        values = [
            self.stats["daily_minutes"].get(
                d.isoformat(), 0
            )
            for d in days
        ]

        max_val = max(values) if max(values) > 0 else 1

        chart_w, chart_h = 320, 180
        margin_bottom = 30
        bar_area_h = chart_h - margin_bottom - 10
        bar_w = 30
        gap = (chart_w - bar_w * 7) / 8

        for i, (d, val) in enumerate(zip(days, values)):
            x0 = gap + i * (bar_w + gap)
            bar_h = (val / max_val) * bar_area_h
            y1 = chart_h - margin_bottom
            y0 = y1 - bar_h

            chart.create_rectangle(
                x0,
                y0,
                x0 + bar_w,
                y1,
                fill="#42a5f5",
                outline="",
            )

            chart.create_text(
                x0 + bar_w / 2,
                y1 + 12,
                text=d.strftime("%a"),
                fill="#b0bec5",
                font=("Segoe UI", 8),
            )

            if val:
                chart.create_text(
                    x0 + bar_w / 2,
                    y0 - 8,
                    text=str(val),
                    fill="white",
                    font=("Segoe UI", 8),
                )


def main():
    root = tk.Tk()
    PixelPalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
