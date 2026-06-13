import os,csv,json,sys
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# creating all the class
class Content:
    #this is the base class
    def __init__(self,title,genre,rating,image_filename):
        self.title,self.genre,self.rating,self.image_filename=title,genre,rating,image_filename

class Profile:
    #individual user has profile under an account
    def __init__(self,name,age_group):
        self.name,self.age_group=name,age_group
        self.watchlist,self.watch_history=[],[]
    def to_dict(self):
        return {"name":self.name,"age_group":self.age_group,"watchlist":self.watchlist,"watch_history":self.watch_history}
    
class Movie(Content):
    #movie is a subclass of content
    def __init__(self,title,genre,rating,image_filename,duration):
        super().__init__(title,genre,rating,image_filename)
        self.duration=duration
    def play(self,profile):
        if self.title not in profile.watch_history:
            profile.watch_history.append(self.title)
        return f"Streaming Movie: {self.title} ({self.duration})\nEnjoy ur movie!"
    
class Account:
    #bruh composition and encapsultion
    #this class has a profile
    #and the password is kept as an private attribute
    def __init__(self,name,email,password,subscription_plan,payment_info):
        self.name,self.email,self.subscription_plan=name,email,subscription_plan
        self.__password,self.__payment_info=password,payment_info
        self.profiles=[Profile(name,"Adult"),Profile("Kids Zone","Kids")]
    def check_password(self,pw):
        return self.__password==pw

CSV_FILE="accounts.csv"
def load_accounts():
    if not os.path.exists(CSV_FILE):
        messagebox.showerror("Critical Error", f"Cannot find '{CSV_FILE}'.") #customkinkter
        sys.exit()
    accounts={} #storing all the accounts in a map
    with open(CSV_FILE,encoding='utf-8') as f:
        for row in csv.DictReader(f):
            acc=Account(row["name"],row["email"],row["password"],row["subscription_plan"],row["payment_info"])
            for saved,profile in zip(json.loads(row["profiles"]),acc.profiles):
                profile.watchlist=saved["watchlist"]
                profile.watch_history=saved["watch_history"]
            accounts[acc.email]=acc
    return accounts

def save_accounts(accounts):
    #saves any changes in the watch history
    with open(CSV_FILE,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(["name","email","password","subscription_plan","payment_info","profiles"])
        for acc in accounts.values():
            w.writerow([acc.name,acc.email,acc._Account__password,acc.subscription_plan,acc._Account__payment_info,json.dumps([p.to_dict() for p in acc.profiles])])
            

class OrzFlixApp(ctk.CTk):
    #numeric rank for each rating so we can compare them 
    RATINGS={"G":1,"PG":2,"M":3,"MA15+":4}
    
    #static library shared accross all profiles
    LIBRARY=[
        Movie("The Avengers","Action","PG","avergers.jpg","2h 23m"),
        Movie("Farewell My Concubine","Drama","MA15+","farewell.jpg","2h 51m"),
        Movie("Jaws","Thriller","M","jaws.webp","2h 4m"),
        Movie("The Sun Also Rises","Drama","MA15+","sun_rises.jpg","2h 10m"),
        Movie("Your Name","Animation","PG","your_name.jpg","1h 46m"),
    ]
    
    #initialization
    def __init__(self):
        super().__init__()
        self.title("OrzFlix Streaming Service")
        self.geometry("900x700")
        
        #hide the window while loading any startup
        self.withdraw()
        self.accounts=load_accounts()
        self.current_account=self.current_profile=None
        
        #reveal the window once data is safely load
        self.deiconify()
        
        #single root container, i want all the screens rendered in this frame
        self.container=ctk.CTkFrame(self)
        self.container.pack(fill="both",expand=True)
        self.show_login_screen()
    
    def clear(self):
        #destory all widge in the container, ready for the next screen
        for w in self.container.winfo_children():
            w.destroy()
    
    #login screen
    def show_login_screen(self):
        #first feature, entry point show the login form
        self.clear()
        self.current_account=self.current_profile=None
        ctk.CTkLabel(self.container,text="Welcome to OrzFlix", font=("Helvetica",28,"bold")).pack(pady=40)
        
        frame=ctk.CTkFrame(self.container)
        frame.pack(pady=20,padx=50)
        ctk.CTkLabel(frame,text="Email Address:").pack(pady=5)
        email=ctk.CTkEntry(frame,width=300,placeholder_text="Enter Email")
        email.pack(pady=5)
        ctk.CTkLabel(frame,text="Password:").pack(pady=5)
        pw=ctk.CTkEntry(frame,width=300,show="*",placeholder_text="Enter password")
        pw.pack(pady=5)
        
        def login():
            e=email.get().strip()
            #check_password is a private attribute
            if e in self.accounts and self.accounts[e].check_password(pw.get()):
                self.current_account=self.accounts[e]
                self.show_profile_selection()
            else:
                messagebox.showerror("Login Error","Invalid email or password.")
        
        ctk.CTkButton(frame,text="Sign in Securely", command=login).pack(pady=20)
    
    #profile page
    def show_profile_selection(self):
        #second feature let the user pick which profile to watch under, adult or child
        self.clear()
        ctk.CTkLabel(self.container,text="Who is watching Today?",font=("Helvetica",24,"bold")).pack(pady=30)
        frame=ctk.CTkFrame(self.container,fg_color="transparent")
        frame.pack(pady=20)
        
        #two options
        for p in self.current_account.profiles:
            ctk.CTkButton(frame,text=f"\n\n{p.name}\n({p.age_group})",width=160,height=160,font=("Helvetica",14),
                          command=lambda prof=p: self._select_profile(prof)).pack(side="left",padx=20)
        ctk.CTkButton(self.container,text="Log Out",fg_color="red",command=self.show_login_screen).pack(pady=40)
    
    def _select_profile(self,profile):
        #store the chosen profile and advance to the main page
        self.current_profile=profile
        self.show_dashboard()
    
    #DashBoard
    def show_dashboard(self):
        #main navigation hub
        #it has three navigation bar and three feature tabs
        self.clear()
        
        #top navigation bar
        nav=ctk.CTkFrame(self.container,height=50,fg_color="#1f2326")
        nav.pack(fill="x")
        ctk.CTkLabel(nav,text=" OrzFlix",font=("Helvetica",18,"bold"),text_color="#3b8ed0").pack(side="left",padx=20,pady=10)
        ctk.CTkLabel(nav,text=f"Active:{self.current_profile.name}",font=("Helvetica",12)).pack(side="left",padx=20)
        ctk.CTkButton(nav,text="Switch Profile",width=100,command=self.show_profile_selection).pack(side="right",padx=10,pady=10)
        
        #tab view housing all three main features
        self.tabs=ctk.CTkTabview(self.container)
        self.tabs.pack(fill="both",expand=True,padx=10,pady=10)
        for tab in ("Browse Library", "My Watchlist", "Manage Account"):
            self.tabs.add(tab)
        
        #redner all tab contents upfront so switching tabs
        self._render_browse()
        self._render_watchlist()
        self._render_account()

    #content row helper
    def _content_row(self, parent, item):
        """Reusable helper which builds one content row(poster and info and buttons)."""
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=5, padx=5)

        #attempt to load movie poster thumbnail from the images folder
        img_path = os.path.join("images", item.image_filename)
        if os.path.exists(img_path):
            try:
                img = ctk.CTkImage(Image.open(img_path), size=(60, 90))
                ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=10, pady=5)
            except Exception:
                ctk.CTkLabel(row, text="[IMG ERROR]", width=60).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(row, text="[No Poster]", width=60).pack(side="left", padx=10)

        #title, rating, genre, and duration of text block
        ctk.CTkLabel(row, justify="left", font=("Helvetica", 14, "bold"),
                     text=f"{item.title} [{item.rating}] - {item.genre}\n(Movie - {item.duration})"
                     ).pack(side="left", padx=10)

        #play button: calls play() that takes on different forms which also logs to watch history
        ctk.CTkButton(row, text="Play", width=70, 
                      command=lambda c=item: self._play(c)).pack(side="right", padx=10)
        
        #watchlist button:  label, colour and action flip based on current state
        in_wl = item.title in self.current_profile.watchlist
        action = "remove" if in_wl else "add"
        kw = {"fg_color": "gray"} if in_wl else {} #only override colour when already saved
        ctk.CTkButton(row, text="Remove Watchlist" if in_wl else "+ Watchlist", width=120,
                      command=lambda c=item, a=action: self._toggle_watchlist(c, a),
                      **kw).pack(side="right", padx=5)
    
    #browse
    def _render_browse(self):
        """Feature 3: this renders the full library with genre and the age ratings"""
        tab = self.tabs.tab("Browse Library")
        for w in tab.winfo_children():
            w.destroy()

        #filters bar
        sf = ctk.CTkFrame(tab)
        sf.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(sf, text = "Genre:").pack(side="left", padx=5)
        genre_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(sf, values=["All", "Action", "Drama", "Thriller", "Animation"],
                          variable=genre_var).pack(side="left", padx=5)
        ctk.CTkLabel(sf, text="Max Rating: ").pack(side="left", padx=5)
        rating_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(sf, values=["All", "G", "PG", "M", "MA15+"],
                          variable=rating_var).pack(side="left", padx=5)

        results = ctk.CTkScrollableFrame(tab)
        results.pack(fill="both", expand=True, padx=10, pady=10)
        
        def apply():
            """Re renders the result every time that the filters are applied"""
            for w in results.winfo_children():
                w.destroy()
            g, r = genre_var.get(), rating_var.get()
            for item in self.LIBRARY:
                #kids profile is blocked from m and ma15 content
                if self.current_profile.age_group == "Kids" and item.rating in ("M", "MA15+"):
                    continue
                if g != "All" and item.genre != g:
                    continue
                #compare ranks so pg excludes m and ma15
                if r != "All" and self.RATINGS.get(item.rating, 5) > self.RATINGS.get(r, 5):
                    continue
                self._content_row(results, item)
        
        ctk.CTkButton(sf, text="Apply Filters", command=apply).pack(side="left", padx = 15)
        apply() #show all content by default

    #play
    def _play(self, item):
        """feature 4: triggers play(), then put watch history to csv"""
        #play() is overridden per content subtype and builds up to watch history
        messagebox.showinfo(f"Now Playing: {item.title}", item.play(self.current_profile))
        save_accounts(self.accounts)

    #watchlist
    def _toggle_watchlist(self, item, action):
        """Feature 5: adds or removes title from the current profile's watchlist"""
        wl = self.current_profile.watchlist
        if action == "add" and item.title not in wl:
            wl.append(item.title)
        elif action == "remove" and item.title in wl:
            wl.remove(item.title)
        save_accounts(self.accounts)
        #re render tabs so watchlist button state is in sync
        self._render_browse()
        self._render_watchlist()

    def _render_watchlist(self):
        """displays the saved watchlist"""
        tab = self.tabs.tab("My Watchlist")
        for w in tab.winfo_children():
            w.destroy()
        ctk.CTkLabel(tab, text="Your Watchlist", font=("Helvetica", 16, "bold")).pack(pady=10)
        if not self.current_profile.watchlist:
            ctk.CTkLabel(tab, text="Nothing saved yet. Browse the library to add some!").pack(pady=20)
            return

        box = ctk.CTkScrollableFrame(tab)
        box.pack(fill="both", expand=True, padx=10, pady=10)
        for title in self.current_profile.watchlist:
            #looks up the full content object by title so that it can reuse _content_row
            item = next((c for c in self.LIBRARY if c.title == title), None)
            if item:
                self._content_row(box, item)
                
    #account
    def _render_account(self):
        """feature 6: the subscription managment feature 7: viewing report export"""
        tab = self.tabs.tab("Manage Account")
        for w in tab.winfo_children():
            w.destroy()
        acc = self.current_account

        #account info display
        info = ctk.CTkFrame(tab)
        info.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(info, text="Account Settings",
                     font=("Helvetica", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        for i, text in enumerate([f"Account Holder: {acc.name}", f"Billing Email: {acc.email}",
                                   f"Current Plan: {acc.subscription_plan}"], 1):
            ctk.CTkLabel(info, text=text).grid(row=i, column=0, sticky="w", padx=10, pady=3)

        #feature 6: the subscription plan change
        sub = ctk.CTkFrame(tab)
        sub.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(sub, text="Change Subscription Plan").pack(anchor="w", padx=10, pady=5)
        plan_var = ctk.StringVar(value=acc.subscription_plan) #pre select the current plan
        ctk.CTkOptionMenu(sub, values=["Standard Plan", "Premium Plan", "Ultimate Ultra Plan"],
                          variable=plan_var).pack(side="left", padx=10, pady=10)
                          
        def save_plan():
            """Save the new plan to the account and write a .txt invoice file."""
            old, new = acc.subscription_plan, plan_var.get()
            acc.subscription_plan = new
            save_accounts(self.accounts)
            fname = f"invoice_change_{acc.name}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"{'='*46}\n          ORZFLIX SUBSCRIPTION INVOICE\n{'='*46}\n"
                        f"Account: {acc.name}\nEmail: {acc.email}\n"
                        f"Previous Plan: {old}\nNew Plan: {new}\nStatus: Processed\n"
                        f"Thank you for choosing OrzFlix!\n{'='*46}\n")
            messagebox.showinfo("Billing Complete", f"Plan updated to {new}!\nInvoice saved: {fname}")
            self._render_account() #refreshed tab so the new plan displays

        ctk.CTkButton(sub, text="Confirm Plan", command=save_plan).pack(side="left", padx=10, pady=10)

        #feature 8: viewing history report export
        rep = ctk.CTkFrame(tab)
        rep.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(rep, text="Export Viewing Report").pack(anchor="w", padx=10, pady=5)

        def export_report():
            """Write the current profile's watch histroy to a .txt report file."""
            p = self.current_profile
            fname = f"viewing_report_{p.name}.txt"
            #format each watched title as a numbered list
            history = "\n".join(f" {i}. {t}" for i, t in enumerate(p.watch_history, 1)) \
                      or " No history recorded."
            with open(fname, "w", encoding = "utf-8") as f:
                f.write(f"{'='*46}\n          ORZFLIX WATCH HISTORY REPORT\n{'='*46}\n"
                        f"Profile: {p.name}\nAge Group: {p.age_group}\n{'-'*46}\n"
                        f"Watched: \n{history}\n{'='*46}\n")
            messagebox.showinfo("Report Exported", f"Report saved: {fname}")
            
        ctk.CTkButton(rep, text="Export Viewing Report (.txt)",
                      command=export_report).pack(anchor="w", padx=10, pady=10)

    
if __name__=="__main__":
    OrzFlixApp().mainloop()