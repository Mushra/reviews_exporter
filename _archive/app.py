import customtkinter as ctk

from tkinter import filedialog

import threading


from services.game_search import search_games

from services.pipeline_service import execute_pipeline



ctk.set_appearance_mode(
    "dark"
)



class App(
    ctk.CTk
):


    def __init__(
        self
    ):

        super().__init__()



        self.title(
            "Metacritic Review Extractor"
        )


        self.geometry(
            "750x650"
        )



        self.destination = None



        self.build_ui()



    def build_ui(
        self
    ):


        # -------------------------
        # Game
        # -------------------------

        self.game_label = ctk.CTkLabel(

            self,

            text="Game"

        )

        self.game_label.pack(
            pady=5
        )



        self.game_entry = ctk.CTkEntry(

            self,

            width=500

        )


        self.game_entry.pack()



        self.search_button = ctk.CTkButton(

            self,

            text="Search",

            command=self.search

        )


        self.search_button.pack(
            pady=5
        )



        self.results = ctk.CTkComboBox(

            self,

            width=500,

            values=[]

        )


        self.results.pack()



        # -------------------------
        # Platform
        # -------------------------

        self.platform = ctk.CTkComboBox(

            self,

            values=[
                "all platform",
                "pc",
                "ps5",
                "xbox-series-x"
            ]

        )


        self.platform.set(
            "all platform"
        )


        self.platform.pack(
            pady=15
        )



        # -------------------------
        # Options
        # -------------------------

        self.extract_user = ctk.BooleanVar(
            value=True
        )

        self.extract_critic = ctk.BooleanVar(
            value=True
        )

        self.process_user = ctk.BooleanVar(
            value=True
        )

        self.process_critic = ctk.BooleanVar(
            value=True
        )



        for text,var in [

            (
                "Extract User Reviews",
                self.extract_user
            ),

            (
                "Extract Critic Reviews",
                self.extract_critic
            ),

            (
                "Process User Reviews",
                self.process_user
            ),

            (
                "Process Critic Reviews",
                self.process_critic
            )

        ]:


            ctk.CTkCheckBox(

                self,

                text=text,

                variable=var

            ).pack(
                anchor="w",
                padx=100
            )



        # -------------------------
        # Destination
        # -------------------------

        self.destination_button = ctk.CTkButton(

            self,

            text="Set Destination Folder",

            command=self.choose_folder

        )


        self.destination_button.pack(
            pady=20
        )


        self.destination_label = ctk.CTkLabel(

            self,

            text="No destination"

        )


        self.destination_label.pack()



        # -------------------------
        # Progress
        # -------------------------

        self.progress = ctk.CTkProgressBar(

            self,

            width=500

        )


        self.progress.set(
            0
        )


        self.progress.pack(
            pady=20
        )



        self.status = ctk.CTkLabel(

            self,

            text="Ready"

        )


        self.status.pack()



        # -------------------------
        # Actions
        # -------------------------

        self.run_button = ctk.CTkButton(

            self,

            text="PROCESS",

            command=self.run

        )


        self.run_button.pack(
            pady=10
        )



        self.open_button = ctk.CTkButton(

            self,

            text="Open Files",

            command=self.open_files

        )


        self.open_button.pack()



    def search(
        self
    ):


        results = search_games(

            self.game_entry.get()

        )


        values = [

            f"{x['title']} | {x['slug']}"

            for x in results

        ]


        self.results.configure(

            values=values

        )



        if values:

            self.results.set(
                values[0]
            )



    def choose_folder(
        self
    ):

        folder = filedialog.askdirectory()


        if folder:

            self.destination = folder

            self.destination_label.configure(

                text=folder

            )



    def update_progress(

        self,

        percent,

        message

    ):


        self.progress.set(

            percent / 100

        )


        self.status.configure(

            text=message

        )



    def run(
        self
    ):


        selected = self.results.get()


        if "|" not in selected:

            self.status.configure(
                text="Select a game"
            )

            return



        slug = selected.split("|")[1].strip()



        options = {

            "extract_user":
                self.extract_user.get(),

            "extract_critic":
                self.extract_critic.get(),

            "process_user":
                self.process_user.get(),

            "process_critic":
                self.process_critic.get(),

        }



        thread = threading.Thread(

            target=execute_pipeline,

            args=(

                slug,

                self.platform.get(),

                options,

                self.destination,

                self.update_progress

            )

        )


        thread.start()



    def open_files(
        self
    ):

        if self.destination:

            import os

            os.startfile(
                self.destination
            )




def launch_app():

    app = App()

    app.mainloop()