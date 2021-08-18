from PIL import Image, ImageDraw, ImageFont
from math import sqrt, cos, sin, pi

from board import HexagonBoard
from tile import Tile

class HexagonBoardVisualiser:
    HEX_SIZE = 60
    BACKGROUND_COLOUR = (255, 255, 255)
    TILE_FILL_COLOUR = (90, 90, 90)
    TILE_OUTLINE_COLOUR = (0, 0, 0)

    COLOURS = {
        "R": (255, 70, 70),
        "G": (70, 255, 70),
        "Y": (255, 255, 70),
        "B": (70, 70, 255),
    }

    def __init__(self, board: HexagonBoard): 
        self.board = board
        self.min_x, self.min_y, self.max_x, self.max_y = board.bounds()
        self.img_width, self.img_height = self.tile_position_to_pixel_centre((self.max_x+1, self.max_y+1.5))

    def tile_position_to_pixel_centre(self, position):
        x, y = position
        px = self.HEX_SIZE * (1 + x - self.min_x) * 3 / 2
        py = (sqrt(3) / 2) * self.HEX_SIZE * (1.5 + y - self.min_y)
        return int(round(px)), int(round(py))

    def tile_edge(self, position, side):
        px, py = self.tile_position_to_pixel_centre(position)
        # need to rotate the edge to match coordinate system
        rotated_edge = ((side + 4) % 6)
        ppx = px + 0.75 * self.HEX_SIZE * cos(pi / 6 + rotated_edge * pi / 3) 
        ppy = py + 0.75 * self.HEX_SIZE * sin(pi / 6 + rotated_edge * pi / 3) 
        return ppx, ppy
        

    def visualise(self, out_path):
        with Image.new("RGBA", (self.img_width, self.img_height)) as im:            
            draw = ImageDraw.Draw(im)
            #draw.rectangle([0, 0, self.img_width, self.img_height], fill=self.BACKGROUND_COLOUR)

            for (x, y), tile in self.board.board.items(): 
                px, py = self.tile_position_to_pixel_centre((x, y))
                draw.regular_polygon((px, py, self.HEX_SIZE), 6, fill=self.TILE_FILL_COLOUR, outline=self.TILE_OUTLINE_COLOUR) 
            
                for i in range(6):
                    ppx, ppy = self.tile_edge((x, y), i)
                    colour = self.COLOURS[tile.get_edge(i)]
                    draw.regular_polygon((ppx, ppy, self.HEX_SIZE/10), 10, fill=colour)
                    
                    paired_edge = tile.paired_edge(i)
                    oppx, oppy = self.tile_edge((x, y), paired_edge)
                    draw.line([ppx, ppy, oppx, oppy], width=5, fill=colour)

                fnt = ImageFont.truetype("FreeSans.ttf", size=int(self.HEX_SIZE / 1.5))
                draw.text((px, py), str(tile.id), anchor="mm", font=fnt, fill=self.COLOURS[tile.colour])   
                   
                
            im.save(open(out_path, "wb"))
