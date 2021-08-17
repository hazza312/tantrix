from PIL import Image, ImageDraw, ImageFont
from math import sqrt, cos, sin, pi

from board import HexagonBoard
from tile import Tile

class HexagonBoardVisualiser:
    HEXAGON_SIZE = 20
    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 1000

    OUTLINE_COLOUR = (255, 255, 255)
    COLOURS = {
        "R": (255, 0, 0),
        "G": (0, 255, 0),
        "Y": (255, 255, 0),
        "B": (0, 0, 255),
    }

    def __init__(self, board: HexagonBoard): 
        self.board = board

    def visualise(self, out_path):
        min_x, min_y, max_x, max_y = self.board.bounds()
        hex_size = 60        

        with Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT)) as im:
            draw = ImageDraw.Draw(im)
            for (x, y), tile in self.board.board.items(): 
                px = hex_size * (1 + x - min_x) * 3 / 2
                py = (sqrt(3) / 2) * hex_size * (1 + y - min_y)
                draw.regular_polygon((px, py, hex_size), 6, outline=self.OUTLINE_COLOUR) 
            

                for i in range(6):
                    ppx = px + 0.75*hex_size * cos(pi/6 + ((i + 4) % 6) * pi / 3) 
                    ppy = py + 0.75*hex_size * sin(pi/6 + ((i + 4) % 6) * pi / 3) 
                    colour = self.COLOURS[tile.get_edge(i)]
                    draw.regular_polygon((ppx, ppy, hex_size/10), 10, fill=colour)
                    
                    paired_edge = tile.paired_edge(i)
                    oppx = px + 0.75*hex_size * cos(pi/6 + ((paired_edge + 4) % 6) * pi / 3) 
                    oppy = py + 0.75*hex_size * sin(pi/6 + ((paired_edge + 4) % 6) * pi / 3) 
                    draw.line([ppx, ppy, oppx, oppy], width=5, fill=colour)
                fnt = ImageFont.truetype("FreeSans.ttf", size=int(hex_size / 1.5))
                draw.text((px, py), str(tile.id), anchor="mm", font=fnt, fill=self.COLOURS[tile.colour])   
                   
                
            im.save(open(out_path, "wb"))
