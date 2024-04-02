from PIL import Image, ImageDraw, ImageFont


class OverlayCreator:
    def __init__(
        self,
        game,
        teams_name,
    ):
        self.game = game
        self.teams_name = teams_name
        self.overlay = None
        self.colors = {
            "gold": (168, 129, 2),
            "blue": (33, 25, 82),
            "white": (255, 255, 255),
        }
        self.offset = 15
        self.score_set_box_size = 100
        self.text_box_size = 250
        self.logo_size = self.score_set_box_size * 2 + self.offset
        self.small_radius = 10
        self.big_radius = 20
        self.global_x_offset = 0

    def create_rectangle(
        self, size, radius, color, text="", font_size=70, x_offset=0, serve=False
    ):
        width, height = size
        rectangle = Image.new("RGBA", size, color)
        corner = Image.new("RGBA", (radius, radius), (0, 0, 0, 0))
        draw = ImageDraw.Draw(corner)

        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=color)

        rectangle.paste(corner, (0, 0))
        rectangle.paste(corner.rotate(90), (0, height - radius))
        rectangle.paste(corner.rotate(180), (width - radius, height - radius))
        rectangle.paste(corner.rotate(270), (width - radius, 0))

        if text:
            draw = ImageDraw.Draw(rectangle)
            font = ImageFont.truetype("assets/Anonymous_Pro_B.ttf", font_size)
            text_width, text_height = draw.textsize(text, font=font)
            text_position = (
                (width - text_width) / 2 + font_size / 20 + x_offset,
                (height - text_height) / 2 - font_size / 10 + 1,
            )
            draw.text(text_position, text, fill=(255, 255, 255), font=font)

        if serve:
            circle_radius = 15
            circle_x = text_position[0] - 40
            circle_y = text_position[1] + 36
            draw.ellipse(
                (
                    circle_x - circle_radius,
                    circle_y - circle_radius,
                    circle_x + circle_radius,
                    circle_y + circle_radius,
                ),
                fill=self.colors["white"],
            )

        return rectangle

    def save(self, output_path):
        self.overlay.save(output_path)

    def add_background(self):
        global_width = (
            self.offset
            + self.logo_size
            + self.offset
            + self.text_box_size
            + self.offset
            + (self.score_set_box_size + self.offset) * (len(self.game["sets"]) + 1)
        )
        global_height = self.offset + self.logo_size + self.offset
        global_image = self.create_rectangle(
            (global_width, global_height), self.big_radius, self.colors["white"]
        )

        self.overlay = global_image

        self.global_x_offset += self.offset

    def add_logo(self):
        logo_image = Image.open("assets/logo_RV51.png").resize(
            (self.logo_size, self.logo_size)
        )
        self.overlay.paste(
            logo_image,
            (self.global_x_offset, self.offset),
            logo_image,
        )
        self.global_x_offset += self.logo_size + self.offset

    def add_team_names(self, serve_team_name):
        team_A = self.create_rectangle(
            (self.text_box_size, self.score_set_box_size),
            self.small_radius,
            self.colors["gold"],
            self.teams_name[0],
            x_offset=30,
            serve=serve_team_name == self.teams_name[0],
        )
        self.overlay.paste(team_A, (self.global_x_offset, self.offset), team_A)

        team_B = self.create_rectangle(
            (self.text_box_size, self.score_set_box_size),
            self.small_radius,
            self.colors["gold"],
            self.teams_name[1],
            x_offset=30,
            serve=serve_team_name == self.teams_name[1],
        )
        self.overlay.paste(
            team_B,
            (
                self.global_x_offset,
                self.offset + self.score_set_box_size + self.offset,
            ),
            team_B,
        )

        self.global_x_offset += self.text_box_size + self.offset

    def add_score(self):
        score_A = self.create_rectangle(
            (self.score_set_box_size, self.score_set_box_size),
            self.small_radius,
            self.colors["gold"],
            str(self.game["score"][0]["value"]),
        )
        self.overlay.paste(score_A, (self.global_x_offset, self.offset), score_A)
        score_B = self.create_rectangle(
            (self.score_set_box_size, self.score_set_box_size),
            self.small_radius,
            self.colors["gold"],
            str(self.game["score"][1]["value"]),
        )
        self.overlay.paste(
            score_B,
            (
                self.global_x_offset,
                self.offset + self.score_set_box_size + self.offset,
            ),
            score_B,
        )

        self.global_x_offset += self.score_set_box_size + self.offset

    def add_sets(self):
        for i, single_set in enumerate(self.game["sets"]):
            set_A = self.create_rectangle(
                (self.score_set_box_size, self.score_set_box_size),
                self.small_radius,
                self.colors["blue"],
                str(single_set[1]["value"]),
            )
            self.overlay.paste(
                set_A,
                (
                    self.global_x_offset + (self.score_set_box_size + self.offset) * i,
                    self.offset,
                ),
                set_A,
            )
            set_B = self.create_rectangle(
                (self.score_set_box_size, self.score_set_box_size),
                self.small_radius,
                self.colors["blue"],
                str(single_set[0]["value"]),
            )
            self.overlay.paste(
                set_B,
                (
                    self.global_x_offset + (self.score_set_box_size + self.offset) * i,
                    +self.offset + self.score_set_box_size + self.offset,
                ),
                set_B,
            )

        self.global_x_offset += self.score_set_box_size + self.offset
