import customtkinter as ctk

from modules.trainer.GenericTrainer import GenericTrainer
from modules.ui import TrainUI
from modules.util.enum.LearningRateScheduler import LearningRateScheduler
from modules.util.ui import components


class BlockWeightsWindow(ctk.CTkToplevel):
    def __init__(self, parent, train_ui: TrainUI, ui_state, *args, **kwargs):
        ctk.CTkToplevel.__init__(self, parent, *args, **kwargs)

        self.textbox = None
        self.parent = parent
        self.train_ui = train_ui
        self.train_config = train_ui.train_config
        self.ui_state = ui_state

        self.title("Block Weight Settings")
        self.geometry("800x500")
        self.resizable(True, True)
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.frame = ctk.CTkFrame(self)
        self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)
        # self.expand_frame = ctk.CTkFrame(self.frame, bg_color="transparent")
        # self.expand_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.main_frame(self.frame)

    def main_frame(self, master):
        if self.train_config.learning_rate_scheduler is LearningRateScheduler.CUSTOM:
            components.label(master, 0, 0, "Blocks to Use:", tooltip="Denotes which blocks to keep active when training.")
            self.textbox = components.bigtextbox(master, 1, 0, "Big Text Box!")

            components.button(self, 2, 0, "generate default block names (this takes a bit)", command=self.on_load_names)

            components.button(self, 3, 0, "ok", command=self.on_window_close)


        # Any additional parameters, in key-value form.
        # self.params = KvParams(self.expand_frame, self.train_config, self.ui_state)

    def on_window_close(self):
        self.destroy()

    def on_load_names(self):
        print("Loading model layer names...")
        trainer = GenericTrainer(self.train_ui.train_config, self.train_ui.training_callbacks, self.train_ui.training_commands)
        lkeys = trainer.report_keys()
        print("Keys:")
        print(trainer)

        self.textbox.delete("1.0", "end")  # Clear existing text
        self.textbox.insert("1.0", "\n".join(lkeys))  # Insert new text
