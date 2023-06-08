"""
Navbar.py

Configure MarcoNeo's navbar on its shopping menu.
"""

#-------------------------------------------------------------------#

from src.utils.gui_utils import Frame, AppButton

#-------------------------------------------------------------------#

class Navbar(Frame):
    """
    Contains the different toggles of the shopping menu.
    Is used to navigate between the different toggles.
    """
    def __init__(self, left_grid=None):
        super().__init__(left_grid)
        self.manager = left_grid
        self.categories = self.manager.manager.gui.app.config.get_loaded_categories()
        self.current_toggle = self.categories[0]

        self.propagate(False)
        self.configure(bg="black")
        self.setup_buttons()

    def setup_buttons(self) -> bool:
        """
        Defines the buttons used in the menu.
        """
        buttons = []
        print(self.categories)
        for i, menu in enumerate(self.categories):
            button = AppButton(self, text=menu, command=lambda menu=menu: self.toggle(menu))
            setattr(self, f"btn{i}", button)
            button.pack(fill="both", expand=True, side="top", padx=10, pady=10)
            buttons.append(button)
        if buttons:
            buttons[0].configure(bg=AppButton.ACTIVE_TOGGLE)  # set active toggle color
            buttons[-1].config(command=self.manager.manager.refill_security)
        self.back_btn = AppButton(self, text="Back",
                                  command=lambda: self.manager.manager.gui.change_menu(
                                      self.manager.manager.gui.main_menu))
        self.back_btn.pack(fill="both", expand=True, side="top", padx=10, pady=10)
        return True

    def toggle(self, toggle: str) -> None:
        """
        Changes the current toggle of the navbar.
        """
        self.current_toggle = toggle

        # Updates in the bg price modifier
        self.manager.manager.right_grid.price_modifier.display_item_list()

        # Update button's colors
        for i, menu in enumerate(self.categories):
            button = getattr(self, f"btn{i}")
            if menu == self.current_toggle:
                button.configure(bg=AppButton.ACTIVE_TOGGLE)  # set active toggle color
            else:
                button.configure(bg=AppButton.DEFAULT_BG)  # set default color

        self.manager.manager.right_grid.body.update_body(toggle)
        self.manager.manager.right_grid.footer.reset()
