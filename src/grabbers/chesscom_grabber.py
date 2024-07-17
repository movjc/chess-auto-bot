from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from grabbers.grabber import Grabber


class ChesscomGrabber(Grabber):
    def __init__(self, chrome_url, chrome_session_id):
        super().__init__(chrome_url, chrome_session_id)
        self.moves_list = {}

    def update_board_elem(self):
        try:
            self._board_elem = self.chrome.find_element(By.XPATH, "//*[@id='board-play-computer']")
        except NoSuchElementException:
            try:
                self._board_elem = self.chrome.find_element(By.XPATH, "//*[@id='board-single']")
            except NoSuchElementException:
                self._board_elem = None

    def is_white(self):
        # Find the square names list
        square_names = None
        try:
            coordinates = self.chrome.find_element(By.XPATH, "//*[@id='board-play-computer']//*[name()='svg']")
            square_names = coordinates.find_elements(By.XPATH, ".//*")
        except NoSuchElementException:
            try:
                coordinates = self.chrome.find_elements(By.XPATH, "//*[@id='board-single']//*[name()='svg']")
                coordinates = [x for x in coordinates if x.get_attribute("class") == "coordinates"][0]
                square_names = coordinates.find_elements(By.XPATH, ".//*")
            except NoSuchElementException:
                return None

        # Find the square with the smallest x and biggest y values (bottom left number)
        elem = None
        min_x = None
        max_y = None
        for i in range(len(square_names)):
            name_element = square_names[i]
            x = float(name_element.get_attribute("x"))
            y = float(name_element.get_attribute("y"))

            if i == 0 or (x <= min_x and y >= max_y):
                min_x = x
                max_y = y
                elem = name_element

        # Use this square to determine whether the player is white or black
        num = elem.text
        return num == "1"

    def is_game_over(self):
        try:
            # Find the game over window
            game_over_window = self.chrome.find_element(By.CLASS_NAME, "board-modal-container")
            return game_over_window is not None
        except NoSuchElementException:
            # Return False since the game over window is not found
            return False

    def get_move_list(self):
        # Find the moves list
        try:
            move_list_elem = self.chrome.find_element(By.CLASS_NAME, "play-controller-scrollable")
        except NoSuchElementException:
            try:
                move_list_elem = self.chrome.find_element(By.CLASS_NAME, "move-list-wrapper-component")
            except NoSuchElementException:
                    return None

        # Select all children with class containing "white node" or "black node"
        # Moves that are not pawn moves have a different structure
        # containing children
        if not self.moves_list:
            # If the moves list is empty, find all moves  data-whole-move-number
            #moves = move_list_elem.find_elements(By.CSS_SELECTOR, "div.move [data-ply]")
            moves = move_list_elem.find_elements(By.CSS_SELECTOR, "div.node.main-line-ply")
            #print(moves)
        else:
            # If the moves list is not empty, find only the new moves
            #moves = move_list_elem.find_elements(By.CSS_SELECTOR, "div.move [data-ply]:not([data-processed])")
            ## //*[@id="scroll-container"]/wc-vertical-move-list/div/div[last()]/div[last()]
            moves = move_list_elem.find_elements(By.XPATH, "wc-vertical-move-list/div/div[last()]/div[last()]")

        for move in moves:
            move_class = move.get_attribute("class")

            # Check if it is indeed a move
            if "node white" in move_class or "node black" in move_class:
                # Check if it has a figure
                # print(move_class)
                try:
                    # child = move.find_element(By.XPATH, "./*")
                    child = move.find_element(By.XPATH, "span/span")
                    figure = child.get_attribute("data-figurine")
                except NoSuchElementException:
                    figure = None

                # Check if it was en-passant or figure-move
                if figure is None:
                    # If the moves_list is empty or the last move was not the current move
                    span = move.find_element(By.XPATH,"span")
                    self.moves_list[span.id] = span.text
                    print("move_text",move.text)
                    print(move.get_attribute("data-ply"))
                elif "=" in move.text:
                    m = move.text + figure
                    print("m = ",m)
                    # If the move is a check, add the + in the end
                    if "+" in m:
                        m = m.replace("+", "")
                        m += "+"

                    # If the moves_list is empty or the last move was not the current move
                    self.moves_list[move.get_attribute("data-ply")] = m
                else:
                    # If the moves_list is empty or the last move was not the current move
                    self.moves_list[move.get_attribute("data-ply")] = figure + move.text

                # Mark the move as processed
                self.chrome.execute_script("arguments[0].setAttribute('data-processed', 'true')", move)

        return list(self.moves_list.values())

    def is_game_puzzles(self):
        return False

    def click_puzzle_next(self):
        pass

    def make_mouseless_move(self, move, move_count):
        pass
