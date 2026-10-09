import tkinter as tk
from tkinter import messagebox
import json
import math
import os
import  random
from datetime import datetime, date, timedelta
# the save file is created in the same folder s this script
SAVE_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"garden.json")
class focus_garden:
    WIDTH=640
    HEIGHT=420
    GROUND_Y=340
    FLOWER_COLORS=["#ff6b81",
                   "#ffa502",
                   "#eccc68",
                   "#a29bfe",
                   "#ff7f50",
                   "#70a1ff"]
    FLOWER_TYPES=["Daisy",
                  "Rose",
                  "Tulip",
                  "Sunflower"]
    def __init__(self,root):
        self.root=root
        self.root.title("Focus Garden")
        self.root.resizable(False,False)
        #Timer state
        self.running=False
        self.paused=False
        self.total_seconds=0
        self.remaining=0
        self.timer_id=None
        self.current_color=random.choice(self.FLOWER_COLORS)
        self.current_type=random.choice(self.FLOWER_TYPES)
        #saved garden data
        self.data=self.load_data()
        #making sure old garden files still work
        if "plants" not in self.data:
             self.data["plants"]=[]
        self.build_ui()
        self.draw_scene()
        #------------SAVING AND LOADING---------
    def load_data(self):
            try:
                with open(SAVE_FILE,"r") as f:
                    data=json.load(f)
                    if isinstance(data,list):
                         return {"plants": data}
                    return data
            except(FileNotFoundError,json.JSONDecodeError):
                return {"plants":[]}
    def save_data(self):
            with open(SAVE_FILE,"w") as f:
                json.dump(self.data,f,indent=4)
        #---------------BUILDING THE WINDOW----------
    def build_ui(self):
            self.canvas=tk.Canvas(self.root,
                                  width=self.WIDTH,
                                  height=self.HEIGHT,
                                  highlightthickness=0)
            self.canvas.pack()
            panel=tk.Frame(self.root,pady=8)
            panel.pack()
            tk.Label(panel,
                     text="Focus minutes:").grid(row=0,column=0,padx=5)
            self.minutes_box=tk.Spinbox(panel,
                                        from_=1,
                                        to=120,
                                        width=5)
            self.minutes_box.delete(0,"end")
            self.minutes_box.insert(0,"25")
            self.minutes_box.grid(row=0,column=1,padx=5)
            self.start_btn=tk.Button(panel,
                                     text="Plant Seed",
                                     width=12,
                                     command=self.start_timer)
            self.start_btn.grid(row=0,
                                column=2,
                                padx=5)
            #Pause button
            self.pause_btn=tk.Button(panel,
                                     text="Pause",
                                     width=10,
                                     command=self.pause_timer,
                                     state="disabled"
                                     )
            self.pause_btn.grid(row=0,column=3,padx=5)
            self.giveup_btn=tk.Button(panel,
                                      text="Give UP",
                                      width=10,
                                      command=self.give_up,
                                      state="disabled")
            self.giveup_btn.grid(row=0,column=3,padx=5)
            self.reset_btn=tk.Button(panel,
                                     text="Reset Garden",
                                     width=12,
                                     command=self.reset_Garden)
            self.reset_btn.grid(row=0,column=4,padx=5)
            #Statistics
            self.stats_label = tk.Label(self.root,
                                        text="",
                                        font=("Arial", 10))
            self.stats_label.pack(pady=(0,3))
            #Achievement Label
            self.achievement_label=tk.Label(
                 self.root,
                 text="",
                 font=("Arial",9)
            )
            self.achievement_label.pack(pady=(0,8))
            self.update_stats()
            #=================================================
            #---------STATISTICS==============================
            #=================================================
    def update_stats(self):
            plants=self.data["plants"]
            total_minutes=sum(p.get("minutes",0) for p in plants)
            total_sessions=len(plants)
            longest_session=max([p.get("minutes",0)for p in plants],default=0)
            streak=self.calculate_streak()

            self.stats_label.config(
                 text=(
                       f"plants:{total_sessions}",
                                    f"Focus:{total_minutes}min",
                                    f"Streak:{streak}day(s)",
                                    f"Longest:{longest_session}min"
                                    )
            )
            achievements=self.get_achievements()
            self.achievement_label.config(text="Achievements:"+"".join(achievements))
    #========================================================
    #================STREAK SYSTEM===========================
    #========================================================
    def calculate_streak(self):
         if not self.data["plants"]:
            return 0
         dates=set()
         for plant in self.data["plants"]:
              if "date" in plant:
                try:
                        d = datetime.strptime( plant["date"],
                                               "%Y-%m-%d" ).date()
                        dates.add(d)
                except ValueError:  
                        pass
         if not dates:
            return 0
         today = date.today()
         #if there was no focus session today,
         #check whether yesterday's session was the latest session
         if today not in dates:
              if (today.day == 1 or today.replace(day=today.day - 1) not in dates):
                return 0
              today = today.replace(day=today.day - 1)
         streak=0
         current_day=today
         while current_day in dates:
              streak+=1
              current_day-=timedelta(days=1)
         return streak 
    #=============================================================
    # ============ACHIEVEMENTS====================================
    # ============================================================
    def get_achievements(self): 
        plants = self.data["plants"]
        total_minutes = sum(
            p.get("minutes", 0)
            for p in plants )  
        achievements=[]
        if len(plants) >= 1: achievements.append("🌱 First Seed")
        if len(plants) >= 10: achievements.append("🌻 Gardener")
        if total_minutes >= 60: achievements.append("⏱ Deep Focus")
        if self.calculate_streak() >= 7: achievements.append("🔥 7 Day Streak")
        if total_minutes >= 1000: achievements.append("🌸 Master Gardener") 
        if not achievements: achievements.append("Start focusing!")
        return achievements
                  
        #------------TIMER LOGIC----------
    def start_timer(self):
            if self.running:
                return
            try:
                minutes=int(self.minutes_box.get())
                if not 1<=minutes<=120:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid Time",
                                       "Enter a number from 1 to 120.")
                return
            self.total_seconds=minutes*60
            self.remaining=self.total_seconds
            self.running=True
            self.paused=False
            self.current_color=random.choice(self.FLOWER_COLORS)
            self.current_flower=random.choice(self.FLOWER_TYPES)
            #Button states
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal",text="Pause")
            self.giveup_btn.config(state="normal")
            self.minutes_box.config(state="disabled")
            self.draw_scene()
            self.timer_id=self.root.after(1000,self.tick)
#===================================================================
# ==============TIMER TICK==========================================
# ==================================================================
    def tick(self):
            if not self.running:
                return
            self.remaining -=1
            self.draw_scene()
            if self.remaining<=0:
                self.finish()
            else:
                self.timer_id=self.root.after(1000,self.tick)
#====================================================================
# ==============PAUSE AND RESUME=====================================
# ===================================================================
    def pause_timer(self):
         if not self.running:
              return
         if not self.paused:
              self.paused = True
              if self.timer_id:
                   self.root.after_cancel( self.timer_id )
                   self.timer_id = None
                   self.pause_btn.config( text="Resume" )  
                   self.draw_scene()
              else:
                   self.paused = False
                   self.pause_btn.config( text="Pause" )
                   self.timer_id = self.root.after( 1000, self.tick )
                   self.draw_scene()                
    def finish(self):
            self.running=False
            self.timer_id=None
            self.paused=False
            new_plant = { "color": self.current_color,
                          "flower": self.current_flower,
                          "minutes": self.total_seconds // 60,
                          }
            self.data["plants"].append(new_plant)
            self.save_data()
            self.reset_button()
            self.update_stats()
            self.draw_scene()
            messagebox.showinfo("Bloomed!","Your flower has grown and joined your garden.")
    def give_up(self):
            if messagebox.askyesno("Give Up?","Your Plant will wither awaY.R u sure?"):
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
                    self.timer_id=None
                    self.running=False
                    self.paused=False
                    self.reset_buttons()
                    self.draw_scene()
    def reset_button(self):
            self.start_btn.config(state="normal")
            self.pause_btn.config( state="disabled", text="Pause")
            self.giveup_btn.config(state="disabled")
            self.minutes_box.config( state="normal")
    def reset_Garden(self):
            if self.running:
                messagebox.showinfo("Busy","Finish or giveup your current plant first.")
                return
            if messagebox.askyesno("Reset","Delete your whole Garden?"):
                self.data={"plants":[]}
                self.save_data()
                self.update_stats()
                self.draw_scene()
        #------------DRAWING----------------------------------------
    def draw_scene(self):
            c=self.canvas
            c.delete("all")
            #sky, sun,and clouds
            #=============================================
            #========SKY====================================
            #===============================================
            c.create_rectangle(0,0,self.WIDTH,self.GROUND_Y,fill="#bfe9ff",outline="")
            #==========SUN===============================
            c.create_oval(540,30,600,90,fill="#ffd93d",outline="")
            #============CLOUDS========================
            for cx,cy in [(120,70),(330,45)]:
              
                c.create_oval(cx,cy,cx+70,cy+30,fill="white",outline="")
                c.create_oval(cx+25,cy-12,cx+85,cy+22,fill="white",outline="")
            # ----------------------------------------------------- # BACKGROUND HILLS # -----------------------------------------------------
            c.create_oval( -150, 250, 250, 450, fill="#8fd694", outline="" )
            c.create_oval( 250, 240, 700, 450, fill="#7bc67e", outline="" )

            #soil and grass
            c.create_rectangle(0,self.GROUND_Y,self.WIDTH,self.HEIGHT,fill="#8b582b",outline="")
            c.create_rectangle(0,self.GROUND_Y,self.WIDTH,self.GROUND_Y+12,fill="#4caf50",outline="")
            # Grass details
            for x in range(10, self.WIDTH, 25):
                c.create_line( x, self.GROUND_Y + 12, x + 4, self.GROUND_Y + 5, fill="#2e8b57" )
            #saved garden(show the latest 12 plants in the soill)
            for i,plant in enumerate(self.data["plants"][-12:]):
                x=40+i*48
                self.draw_plant( x,
                                self.HEIGHT - 20, 1.0, 0.35,
                                 plant.get( "color", "#ff6b81" ),
                                 plant.get( "flower", "Daisy" ) )
            #current plant
            cx=self.WIDTH//2
            if self.running:
                progress=1-self.remaining/self.total_seconds
                self.draw_plant( cx, self.GROUND_Y + 8, progress, 1.0, self.current_color, self.current_flower )
                mins,secs=divmod(self.remaining,60)
                c.create_text( cx, 25, text=f"{mins:02d}:{secs:02d}", font=("Arial", 28, "bold"), fill="#2c3e50" )
                if self.paused: c.create_text( cx, 60, text="⏸ PAUSED", font=("Arial", 12, "bold"), fill="#c0392b" )
            else:
                c.create_text(cx,25,text="Plant a seed and start focussing",font=("Arial",14),fill="#2c3e50")
    def draw_plant(self, x, base_y, progress, s, color, flower_type="Daisy" ):
            c=self.canvas
            # Seed mound
            c.create_oval( x - 8 * s, base_y - 4 * s, x + 8 * s, base_y + 4 * s, fill="#5d3a1a", outline="" )
            if progress <= 0:
                return
            #=====================STEM====================================
            stem_h=130*s*progress
            top_y= base_y-stem_h
            c.create_line( x, base_y, x, top_y, width=max( 2, int(5 * s) ), fill="#2d8f3c" )
            #===================================================================================
            #==================FIRST LEAF======================================================
            if progress > 0.20:
                 ly = ( base_y - stem_h * 0.35 )
                 c.create_oval( x - 34 * s, ly - 9 * s, x, ly + 9 * s, fill="#3fb950", outline="" )
            #===================SECOND LEAF=========================================
            if progress > 0.45:
                ry = ( base_y - stem_h * 0.60)
                c.create_oval( x, ry - 9 * s, x + 34 * s, ry + 9 * s, fill="#3fb950", outline="" )
            #==========================BUD==================================
            if 0.70 < progress < 0.90:
                 c.create_oval( x - 9 * s, top_y - 9 * s, x + 9 * s, top_y + 9 * s, fill="#2d8f3c", outline="" )
            #=====================FLOWER=============================================
            if progress >= 0.90:
                 bloom = min( 1.0, (progress - 0.90) / 0.10 )
                 r = 18 * s * bloom
                 petal_size = 10 * s * bloom
                 # Different flower styles
                 if flower_type == "Sunflower":
                    petal_count = 10
                 elif flower_type == "Tulip":
                    petal_count = 3
                 elif flower_type == "Rose":
                      petal_count = 8
                 else:
                      petal_count = 6
                 for i in range(petal_count):
                      angle = ( i * 2 * math.pi / petal_count )
                      px = ( x + math.cos(angle) * r )
                      py = ( top_y + math.sin(angle) * r )
                      c.create_oval( px - petal_size, py - petal_size, px + petal_size, py + petal_size, fill=color, outline="" )
            # Flower center
            c.create_oval( x - 7 * s, top_y - 7 * s, x + 7 * s, top_y + 7 * s, fill="#ffe066", outline="" )

if __name__=="__main__":
    root=tk.Tk()
    app=focus_garden(root)
    root.mainloop()







