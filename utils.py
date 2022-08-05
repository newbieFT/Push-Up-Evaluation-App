import cv2

STATE_NORMAL, COLOR_NORMAL, FG_NORMAL = 0, (195, 195, 75), (255, 255, 255)
STATE_HOVER, COLOR_HOVER, FG_HOVER = 1, (22, 210, 64), (255, 255, 255)
STATE_CLICKED, COLOR_CLICKED, FG_CLICKED = 2, (48, 153, 70), (255, 255, 255)

FONT_HEIGHT = 22


class Button():

    def __init__(self, text, text_width, start_pos, w_h, fg_scale, fg_strong, func):
        self.text = text
        self.text_width = text_width
        self.x, self.y = start_pos
        self.w , self.h = w_h
        self.fg_scale = fg_scale
        self.fg_strong = fg_strong
        self.func = func
        self.state = STATE_NORMAL

    def place(self, img):
        color = COLOR_NORMAL
        fg_color = FG_NORMAL
        if self.state == STATE_HOVER:
            color = COLOR_HOVER
            fg_color = FG_HOVER
        elif self.state == STATE_CLICKED:
            color = COLOR_CLICKED
            fg_color = FG_CLICKED
        img = cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), color, cv2.FILLED)
        img = cv2.putText(img, self.text, (self.x + (self.w - self.text_width) // 2,
                                           self.y + (self.h + FONT_HEIGHT * self.fg_scale) // 2)
                                            , cv2.FONT_HERSHEY_SIMPLEX, self.fg_scale, fg_color, self.fg_strong)
        return img

    def mouse_focus(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h

    def get_state(self):
        return self.state

    def set_state(self, state_num):
        self.state = state_num

    def call_func(self):
        self.func()


class Label():

    def __init__(self, text, text_width, start_pos, w_h, fg, fg_scale, fg_strong, bg=None):
        self.text = text
        self.text_width = text_width
        self.x, self.y = start_pos
        self.w, self.h = w_h
        self.fg = fg
        self.fg_scale = fg_scale
        self.fg_strong = fg_strong
        self.bg = bg

    def place(self, img):
        if self.bg:
            img = cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), self.bg, cv2.FILLED)
        img = cv2.putText(img, self.text, (self.x + (self.w - self.text_width) // 2,
                                           self.y + (self.h + FONT_HEIGHT * self.fg_scale) // 2)
                                            , cv2.FONT_HERSHEY_SIMPLEX, self.fg_scale, self.fg, self.fg_strong)
        return img

    def set_text(self, new_text):
        self.text = new_text