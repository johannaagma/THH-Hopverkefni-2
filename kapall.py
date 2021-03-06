import wx, sys, os, pygame, random
import wx.animate
from pygame.locals import*
import theGame, Scores


class SpriteCard(pygame.sprite.Sprite):
    def __init__(self, pos, real_card):
        pygame.sprite.Sprite.__init__(self)

        self.orig_pos = pos
        self.real_card = real_card

        # set sprite image
        if (self.real_card.up):
            self.image = real_card.image
        else:
             self.image = pygame.image.load('card_back.jpg')

        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        mouse_pos = app.frame.ScreenToClient(wx.GetMousePosition())
        
        # if the mouse clicks on the card
        if (app.frame.display.mouse_down and self.rect.collidepoint(mouse_pos)
            and not app.frame.display.card_moving):
            if (self.real_card.up):
                # move the card with the mouse
                self.rect.center = mouse_pos
                app.frame.display.card_moving = True
            else:
                # put front image if card is available
                self.real_card.isAvailable()
                if (self.real_card.up):
                    self.image = self.real_card.image
        else:
            # move the card to it's original position
            self.rect.center = self.orig_pos
        
    
class PygameDisplay(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        self.parent = parent
        self.hwnd = self.GetHandle()
       
        self.size = self.GetSizeTuple()
        self.size_dirty = True

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)

        # a timer to update on each frame
        self.timer = wx.Timer(self)
        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

        # game stuff     
        pygame.init()
        self.screen = pygame.Surface(self.size, 0, 32)      
        
    def start_game(self, game):
        self.game = game
        self.start_time = 0
        self.minutes = 0
        self.mouse_down = False
        self.card_moving = False
        self.white = (255, 255, 255)
        
        # groups for sprites
        self.pyramid_cards = pygame.sprite.OrderedUpdates()
        self.pile_cards = pygame.sprite.Group()

        self.generate_deck()
        self.generate_pyramid()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)

    def generate_deck(self):
         # deck to draw new card
        self.deck_image_file = "card_back.jpg"
        self.deck_image = wx.Image(self.deck_image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.draw_button = wx.BitmapButton(self, id=-1, bitmap=self.deck_image,
            pos=(700, 510), size = (self.deck_image.GetWidth()+5, self.deck_image.GetHeight()+5))
        self.Bind(wx.EVT_BUTTON, self.drawNewCard, self.draw_button)
        
        # make sprite for the top card in trash pile
        self.fake_card = self.game.pyramid[0]
        self.compare_card = SpriteCard([250, 300], self.fake_card)
        self.pile_cards.add(self.compare_card)
        self.draw_card()

    def generate_pyramid(self):
        for i in range(0, len(self.game.pyramid)):
            self.card = self.game.pyramid[i]
            self.pyramid_card = SpriteCard([self.card.x, self.card.y], self.card)
            self.pyramid_cards.add(self.pyramid_card)
        
    def Update(self, event):
        self.card_moving = False

        # update cards
        self.pyramid_cards.update()

        # draw everything on screen
        self.Redraw()
 
    def Redraw(self):
        # to draw the screen again correctly if you resize it
        if self.size_dirty:
            self.screen = pygame.Surface(self.size, 0, 32)
            self.size_dirty = False 

        # set background white
        self.screen.fill(self.white)

        # draw the cards
        # we draw them in seperate groups to make sure that pyramid cards have a higher z-level
        self.pile_cards.draw(self.screen)
        self.pyramid_cards.draw(self.screen)

        self.draw_points()
        self.draw_bonustime()
        self.draw_time()
        
        # stuff to draw everything with wx/pygame combined
        s = pygame.image.tostring(self.screen, 'RGB')  # Convert the surface to an RGB string
        img = wx.ImageFromData(self.size[0], self.size[1], s)  # Load this string into a wx image
        bmp = wx.BitmapFromImage(img)  # Get the image in bitmap form
        dc = wx.ClientDC(self)  # Device context for drawing the bitmap
        dc.DrawBitmap(bmp, 0, 0, False)  # Blit the bitmap image to the display
        del dc
        
        
    def OnPaint(self, event):
        self.Redraw()
        event.Skip()  # Make sure the parent frame gets told to redraw as well
 
    def OnSize(self, event):
        self.size = self.GetSizeTuple()
        self.size_dirty = True
 
    def Kill(self, event):
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        # This may or may not be necessary now that Pygame is just drawing to surfaces
        self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
        self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
        
    def onMouseDown(self, event):
        self.mouse_down = True

    def onMouseUp(self, event):
        self.mouse_down = False

        self.check_card_to_deck()
        
    def check_card_to_deck(self):
        # check if card is moved to deck
        for card in self.pyramid_cards:
            if self.compare_card.rect.colliderect(card.rect): # if colliding
                can_kill = self.game.pick(card.real_card)   # if correct card
                if (can_kill):
                    self.put_card_to_pile(card)

    def put_card_to_pile(self, card):
        # set card to deck
        self.compare_card.kill()
        self.compare_card = SpriteCard([self.last_compare_card.real_card.x, self.last_compare_card.real_card.y], card.real_card)
        self.pile_cards.add(self.compare_card)
        # remove card from pyramid
        card.kill()
        self.game_won()

    def drawNewCard(self, event):        
        self.draw_card()

    def draw_card(self):
        # remove last card
        self.compare_card.kill()

        if (game.deck.isEmpty()):
            # display a joker on the deck if it's empty
            self.deck_image_file = "joker.png"        
            self.deck_image = wx.Image(self.deck_image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.draw_button.SetBitmapLabel(self.deck_image)

            # display last card in pile
            new_card = self.game.flip()
            self.compare_card = self.last_compare_card;
            self.pile_cards.add(self.compare_card)
        else:
            # get new card from deck
            new_card = self.game.flip()
            new_card.up = True
            self.compare_card = SpriteCard([new_card.x, new_card.y], new_card)
            self.pile_cards.add(self.compare_card)
            self.last_compare_card = self.compare_card

    def draw_points(self):
        #self.points = Scores.getCurrentPoints(self.game)
        self.points = self.game.scoreThing.getCurrentPoints()
        black = (0,0,0)
        pos = (70, 600)
        
        # draw points
        self.points_font = pygame.font.SysFont("Arial", 30)
        self.points_image = self.points_font.render(str(self.points), 1, black)
        self.points_rect = self.points_image.get_rect()
        self.points_rect.center = pos
        self.screen.blit(self.points_image, self.points_rect)
	
    def draw_bonustime(self):
        self.bonustime = self.game.scoreThing.getBonusTime()
        black = (0,0,0)
        pos = (780, 50)
        
        # draw points
        self.bonustime_font = pygame.font.SysFont("Arial", 20)
        self.bonustime_image = self.bonustime_font.render(str(self.bonustime), 1, black)
        self.bonustime_rect = self.bonustime_image.get_rect()
        self.bonustime_rect.center = pos
        self.screen.blit(self.bonustime_image, self.bonustime_rect)

    def draw_time(self):
        # get seconds
        self.elapsed_time = int(self.game.getTime()) - self.start_time
        
        # get minutes
        if (self.elapsed_time >= 60):
            self.start_time = int(self.game.getTime())
            self.minutes += 1
            
        # time text
        if (self.elapsed_time < 10 and self.minutes < 10):
            self.time = "Time played: 0" + str(self.minutes) + ":0" + str(self.elapsed_time)
        elif (self.elapsed_time < 10 and self.minutes >= 10):
            self.time = "Time played: " + str(self.minutes) + ":0" + str(self.elapsed_time)
        elif (self.elapsed_time >= 10 and self.minutes < 10):
            self.time = "Time played: 0" + str(self.minutes) + ":" + str(self.elapsed_time)
        elif (self.elapsed_time >= 10 and self.minutes >= 10):
            self.time = "Time played: " + str(self.minutes) + ":" + str(self.elapsed_time)

        # display time
        black = (0,0,0)
        pos = (100, 50)
        
        self.time_font = pygame.font.SysFont("Arial", 20)
        self.time_image = self.time_font.render(str(self.time), 1, black)
        self.time_rect = self.time_image.get_rect()
        self.time_rect.center = pos
        self.screen.blit(self.time_image, self.time_rect)

    def game_won(self):
        if len(self.pyramid_cards.sprites()) == 0:
            total = str(self.game.scoreThing.getScore())
            divided = self.game.scoreThing.getDivided()
            self.post_score_frame = PostHighScoreFrame(parent = None, total = total, divided = divided)
            self.post_score_frame.Show()  
         
class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, size = (900, 700))
        wx.Frame.CenterOnScreen(self)
        self.display = PygameDisplay(self, -1)
       
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)

        # menu bar
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.Kill, m_exit)
        menuBar.Append(menu, "&File")
        m_new_game = menu.Append(wx.ID_ABOUT, "&New Game", "Start a new game.")
        self.Bind(wx.EVT_MENU, self.OnNewGame, m_new_game)
        m_show_highscore = menu.Append(wx.ID_PREVIEW, "&High Score", "See top 5 scores.")
        self.Bind(wx.EVT_MENU, self.getHighScores, m_show_highscore)
        m_help = menu.Append(wx.ID_HELP, "&Help", "Get help.")
        self.Bind(wx.EVT_MENU, self.getHelp, m_help)


        self.SetMenuBar(menuBar)       
        self.SetTitle("Pyramid: Second edition")

        self.Bind(wx.EVT_SIZE, self.OnSize)
       
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.display, 1, flag = wx.EXPAND)
       
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
 
    def Kill(self, event):
        self.display.Kill(event)
        self.Destroy()
 
    def OnSize(self, event):
        self.Layout()

    def OnNewGame(self, event):
        app.level_frame = LevelFrame(parent = None)
        app.level_frame.Show()

    def getHighScores(self, event):
        temp = self.display.game.scoreThing.getHighScoreString()
        self.high_score_frame = HighScoreFrame(parent = None, temp = temp)
        self.high_score_frame.Show()

    def getHelp(self, event):
        temp = self.display.game.scoreThing.getHelp()
        self.help_frame = HelpFrame(parent = None, temp = temp)
        self.help_frame.Show()
    
class LevelFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Choose level')
        wx.Frame.CenterOnScreen(self)
        
        self.grid = wx.GridBagSizer(hgap=3, vgap=3)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.fyrirsogn = wx.StaticText(self, label="Choose a level") #pos = (140,20)
        self.fyrirsognFont = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.fyrirsogn.SetFont(self.fyrirsognFont)
        self.sizer.Add(self.fyrirsogn, flag=wx.ALL|wx.EXPAND, border=20)
        
        self.level1 = wx.RadioButton(self, 1, "Level 1 : 5 rows and color doesn't matter")
        self.grid.Add(self.level1, pos=(0,0), span=(1,2))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level1)
        
        self.level2 = wx.RadioButton(self, 2, "Level 2 : 6 rows and color doesn't matter")
        self.grid.Add(self.level2, pos=(1,0))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level2)
        
        self.level3 = wx.RadioButton(self, 3, "Level 3 : 7 rows and color doesn't matter")
        self.grid.Add(self.level3, pos=(2,0))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level3)
        
        self.level4 = wx.RadioButton(self, 4, "Level 4 : 5 rows and color matters")
        self.grid.Add(self.level4, pos=(0,3))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level4)
        
        self.level5 = wx.RadioButton(self, 5, "Level 5 : 6 rows and color matters")
        self.grid.Add(self.level5, pos=(1,3))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level5)
        
        self.level6 = wx.RadioButton(self, 6, "Level 6 : 7 rows and color matters")
        self.grid.Add(self.level6, pos=(2,3))
        self.Bind(wx.EVT_RADIOBUTTON, self.Levels, self.level6)
        
        self.sizer.Add(self.grid, flag=wx.ALL|wx.EXPAND, border=10)
        
        
        self.start_game_button = wx.Button(self, label="Start game", size= (100, 50))
        self.Bind(wx.EVT_BUTTON, self.start_game, self.start_game_button)
        self.sizer.Add(self.start_game_button, 0, wx.ALIGN_CENTER, 20)

        self.height = 7
        self.sortsOn = True
        
        self.SetSizerAndFit(self.sizer)

    def start_game(self, event):
    	global game
    	game = theGame.theGame(self.height, self.sortsOn)
    	app.frame.display.start_game(game)
    	self.Destroy()
    
    def Levels(self, event):
        if(event.Id == 1):
            self.height = 5
            self.sortsOn = False
        if(event.Id == 2):
            self.height = 6
            self.sortsOn = False
        if(event.Id == 3):
            self.height = 7
            self.sortsOn = False
        if(event.Id == 4):
            self.height = 5
            self.sortsOn = True
        if(event.Id == 5):
            self.height = 6
            self.sortsOn = True
        if(event.Id == 6):
            self.height = 7
            self.sortsOn = True

class HelpFrame(wx.Frame):
    def __init__(self, parent, temp):
        wx.Frame.__init__(self, parent, -1, 'Help', size = (500, 600))
        wx.Frame.CenterOnScreen(self)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetBackgroundColour('#FFFFFF')

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.StaticText(self, -1, temp)
        self.ok_button = wx.Button(self, label="Ok, got it!", pos = (200,500), size= (100, 50))
        self.Bind(wx.EVT_BUTTON, self.okClicked, self.ok_button )
        self.sizer.Add(self.ok_button , 0, wx.ALIGN_BOTTOM, 5)

    def okClicked(self, event):
        self.Destroy()
        
    def OnSize(self, event):
        self.Layout()
        
class HighScoreFrame(wx.Frame):
    def __init__(self, parent, temp):
        wx.Frame.__init__(self, parent, -1, 'High Score', size = (200, 200))
        wx.Frame.CenterOnScreen(self)
        self.SetBackgroundColour('#FFFFFF')

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.head = wx.StaticText(self, -1, '\n    High Score: Top 5 scores \n \n' + temp)
        
    def OnSize(self, event):
        self.Layout()


class PostHighScoreFrame(wx.Frame):
    def __init__(self, parent, total, divided):
        wx.Frame.__init__(self, parent, -1, 'Game over!', size = (500,530))
        wx.Frame.CenterOnScreen(self)
        self.SetBackgroundColour('#FFFFFF')
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.gif_panel = wx.Panel(self, -1, size = (500,530))
        self.score_panel = wx.Panel(self, -1, size = (500,100))
        #self.score_panel.SetBackgroundColour("indigo")
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_sizer.Add(self.score_panel,0, wx.EXPAND)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        # Score part:
        self.text = wx.StaticText(self.score_panel, -1,'\n     You got ' + total + ' points \n Your points divide like this:\n'+ divided)
        self.text.Wrap(1000)
        self.pandaGif()
        self.main_sizer.Add(self.gif_panel,0)
        self.main_sizer.Add(self.bottom_sizer,0)
        self.main_sizer.Fit(self)
    def OnSize(self, event):
        self.Layout()

    def pandaGif(self):
        # Gif part
        gif_file = "panda.gif"
        self.gif = wx.animate.GIFAnimationCtrl(self.gif_panel, -1, gif_file, pos=(2, 200))
        # clears the background
        self.gif.GetPlayer().UseBackgroundColour(True)
        # continuously loop through the frames of the gif file (default)
        self.gif.Play()

class App(wx.App):
    def OnInit(self):
        # game window
        self.frame = Frame(parent = None)
        self.frame.Show()
        self.SetTopWindow(self.frame)

        # level window
        self.level_frame = LevelFrame(parent = None)
        self.level_frame.Show()
       
        return True

    
if __name__ == "__main__":
    game = theGame.theGame(4)  
    app = App()
    app.MainLoop()
