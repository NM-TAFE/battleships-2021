from tkinter.font import Font
from breezypythongui import EasyCanvas, EasyFrame


class BattlefieldUI(EasyCanvas):
    def __init__(self, parent, width, height, size, colour='lightblue'):
        width = width if width < height else height

        EasyCanvas.__init__(self, parent, width=width, height=width, background='lightgrey',
                            borderwidth=0, highlightthickness=0)

        # Assume a square grid of size x size
        self.__size = size

        cell_width = width / size
        self.__cells = [[None] * size for _ in range(size)]
        self.__cell_data = [[None] * size for _ in range(size)]
        for row in range(size):
            for col in range(size):
                x = col * cell_width
                y = row * cell_width

                # Draw the cell (just a rectangle)
                rect = self.drawRectangle(x+4, y+4, x+cell_width-4, y+cell_width-4,
                                          fill=colour)
                self.__cells[col][row] = rect

                # The text will indicate the cell's status
                lbl_id = self.drawText('', x+cell_width/2, y+1+cell_width/2,
                                       font=('Helvetica', 28))
                self.__cell_data[col][row] = lbl_id

    def update_at(self, col, row, val, colour='black'):
        """
        Update the text in cell ({col}, {row}) with value {val}.
        """
        lbl_id = self.__cell_data[col][row]
        self.itemconfig(lbl_id, text=val, fill=colour)

    def clear(self):
        """
        Clear the entire UI.
        """
        size = self.__size
        for row in range(size):
            for col in range(size):
                self.update_at(col, row, '')


def main():
    f = EasyFrame()
    battlefield_ui = BattlefieldUI(f, 500, 600, 10)
    f.addCanvas(battlefield_ui)
    f.mainloop()


if __name__ == '__main__':
    main()
