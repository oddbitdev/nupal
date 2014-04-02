__author__ = 'aperion'

import random
import pygame

pygame.init()


class Workspace(object):
    def __init__(self, tileList=[], tolerance=3, sheetWidth=3600, sheetHeight=2800):
        self.tolerance = tolerance
        self.sheetWidth = sheetWidth
        self.sheetHeight = sheetHeight
        self.currentSheetId = 0
        self.tileList = tileList
        self.minDim = self.sheetWidth
        self.allowFlipping = False

    def get_random_pool(self):
        tensMult = random.randint(2, 55) * 10
        hundredsMult = random.randint(1, 25) * 100
        thousandsMult = random.randint(1, 2) * 1000
        piecePool = [tensMult, tensMult, tensMult, hundredsMult,
                     hundredsMult, thousandsMult]
        return piecePool

    def generate_random_list(self, randomListLen=180):
        for i in range(randomListLen):
            piecePool = self.get_random_pool()
            width = random.choice(piecePool)
            piecePool = self.get_random_pool()
            height = random.choice(piecePool)
            tile = Tile(width, height)
            self.tileList.append(tile)

    def tile_fits(self, tile, sheet):
        if tile.width <= sheet.width and tile.height <= sheet.height:
            return True
        elif tile.width <= sheet.height and tile.height <= sheet.width:
            if not self.allowFlipping:
                return False
            tile.flip_tile()
            return True
        else:
            return False

    def get_orientation(self, tile, sub_sheet):
        flip_tile = False
        if tile.width > sub_sheet.width:
            flip_tile = True
        return flip_tile

    def create_sub_sheets(self, tile, sheet):
        if sheet.width - tile.width - self.tolerance < self.minDim:
            rightSheet = None
        else:
            rightOffset = [sheet.offset[0] + tile.width + self.tolerance,
                           sheet.offset[1]]
            rightSheet = Sheet(sheet.id, rightOffset,
                               (sheet.width - tile.width - self.tolerance), sheet.height - self.tolerance)
        if sheet.height - tile.height - self.tolerance < self.minDim:
            lowerSheet = None
        else:
            lowerOffset = [sheet.offset[0],
                           sheet.offset[1] + tile.height + self.tolerance]
            lowerSheet = Sheet(sheet.id, lowerOffset, tile.width - self.tolerance,
                               (sheet.height - tile.height - self.tolerance))
        return rightSheet, lowerSheet

    def place_tiles(self, sheet):
        for tile in self.tileList:
            if not tile.placed:
                if self.tile_fits(tile, sheet):
                    tile.place_tile(sheet.id, sheet.offset)
                    rightSheet, lowerSheet = self.create_sub_sheets(tile, sheet)
                    if lowerSheet:
                        self.place_tiles(lowerSheet)
                    if rightSheet:
                        self.place_tiles(rightSheet)
                    return

    def generate_solution(self, useRandom=False, allowFlipping=False):
        self.allowFlipping = allowFlipping
        if useRandom:
            self.generate_random_list()

        self.tileList.sort(key=lambda x: x.get_tile_area(), reverse=True)

        for tile in self.tileList:
            if min(tile.width, tile.height) < self.minDim:
                self.minDim = min(tile.width, tile.height)
        allTilesPlaced = False
        self.sheetList = []
        while not allTilesPlaced:
            for tile in self.tileList:
                allTilesPlaced = True
                if not tile.placed:
                    allTilesPlaced = False
                    break
            currentSheet = Sheet(self.currentSheetId, [0, 0], self.sheetWidth, self.sheetHeight)
            self.place_tiles(currentSheet)
            self.sheetList.append(currentSheet)
            self.currentSheetId += 1
        return self.tileList


class Tile(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.flipped = False
        self.sheetId = None
        self.position = None
        self.placed = False

    def get_tile_area(self):
        return self.width * self.height

    def flip_tile(self):
        self.width, self.height = self.height, self.width
        self.flipped = True

    def place_tile(self, sheetId, position):
        self.sheetId = sheetId
        self.position = position
        self.placed = True

    def reset(self):
        self.placed = False
        self.sheetId = None
        self.position = None

    def __str__(self):
        return (str(self.width) + " " + str(self.height) + " " +
                str(self.position) + " " + str(self.placed))


class Sheet(object):
    def __init__(self, id, offset, width, height):
        self.id = id
        self.width = width
        self.height = height
        self.full = False
        self.tiles = []
        self.offset = offset

    def add_tile(self, tile):
        self.tiles.append(tile)

    def lock_sheet(self):
        self.full = True


def main():
    def drawPage(viewSheet):
        layer.fill((0, 0, 0))
        for tile in tileList:
            if tile.placed and tile.sheetId == viewSheet:
                pygame.draw.rect(layer, (random.randint(15, 255),
                                         random.randint(0, 255), random.randint(0, 255)),
                                 pygame.Rect(tile.position,
                                             (tile.width, tile.height)))

    testSpace = Workspace()
    tileList = testSpace.generate_solution(True, True)

    layer = pygame.Surface([3600, 2800])
    running = True

    viewSheet = 0
    updateScreen = True

    while running:
        if updateScreen:
            drawPage(viewSheet)
            updateScreen = False
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False

            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_LEFT:
                    viewSheet -= 1
                    updateScreen = True
                if evt.key == pygame.K_RIGHT:
                    viewSheet += 1
                    updateScreen = True
                if evt.key == pygame.K_UP:
                    viewSheet = 0
                    testSpace.currentSheetId = 0
                    for tile in testSpace.tileList:
                        if tile.flipped:
                            tile.flip_tile()
                            tile.flipped = False
                        tile.placed = False
                    tileList = testSpace.generate_solution(False, False)
                    updateScreen = True
                if evt.key == pygame.K_DOWN:
                    testSpace.currentSheetId = 0
                    for tile in testSpace.tileList:
                        tile.placed = False
                    viewSheet = 0
                    tileList = testSpace.generate_solution(False, True)
                    updateScreen = True
                if evt.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        pygame.transform.scale(layer, (1600, 1000), screen)
        pygame.display.flip()


if __name__ == '__main__':
    screenMode = (1600, 1000)
    screen = pygame.display.set_mode(screenMode)
    main()