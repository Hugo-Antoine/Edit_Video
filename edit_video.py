import json
import os
import subprocess

from OverlayCreator import OverlayCreator


def edit_video(edit_info_path):
    with open(edit_info_path, "r") as file:
        edit_info = json.load(file)

    render_commands = []

    concat_commands = []

    index = 1

    output_folder_path = edit_info["output_folder_path"]
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    our_team = None
    opponent_team = None
    home_team = None
    visitor_team = None

    for team in edit_info["teams"]:
        if team["us"]:
            our_team = team

        if not team["us"]:
            opponent_team = team

        if team["home"]:
            home_team = team

        if not team["home"]:
            visitor_team = team

    new_folder_name = f"{home_team['full_name']} - {visitor_team['full_name']}"

    output_folder_path = os.path.join(output_folder_path, new_folder_name)

    overlay_folder_path = os.path.join(output_folder_path, "overlay")
    if not os.path.exists(overlay_folder_path):
        os.makedirs(overlay_folder_path)

    concat_folder_path = os.path.join(output_folder_path, "concat")
    if not os.path.exists(concat_folder_path):
        os.makedirs(concat_folder_path)

    serve_team_name = None

    game = {
        "score": [
            {"team": our_team["short_name"], "value": 0},
            {"team": opponent_team["short_name"], "value": 0},
        ],
        "sets": [
            [
                {"team": our_team["short_name"], "value": 0},
                {"team": opponent_team["short_name"], "value": 0},
            ]
        ],
    }
    for video in edit_info["videos"]:
        for action in video["actions"]:
            if "set" in action.keys():
                if action["set"] in ["new", "end"]:
                    win_team = max(game["sets"][-1], key=lambda x: x["value"])["team"]
                    for team_score in game["score"]:
                        if team_score["team"] == win_team:
                            team_score["value"] += 1
                            break

                if action["set"] == "new":
                    game["sets"].append(
                        [
                            {"team": our_team["short_name"], "value": 0},
                            {"team": opponent_team["short_name"], "value": 0},
                        ]
                    )

                elif action["set"] == "end":
                    serve_team_name = None

                if "serve" in action.keys():
                    serve_team_name = action["serve"]
            else:
                print(f"Creating overlay and command for action {index}")
                overlay_file_path = os.path.join(
                    overlay_folder_path,
                    f"{index}.png",
                )
                concat_file_path = os.path.join(
                    concat_folder_path,
                    f"{index}.mp4",
                )
                overlay_creator = OverlayCreator(
                    game, [home_team["short_name"], visitor_team["short_name"]]
                )
                overlay_creator.add_background()
                overlay_creator.add_logo()
                overlay_creator.add_team_names(serve_team_name=serve_team_name)
                overlay_creator.add_score()
                overlay_creator.add_sets()
                overlay_creator.save(output_path=overlay_file_path)
                new_render_command = f"ffmpeg -ss {action['begin']} -to {action['end']} -i '{video['file_path']}' -i '{overlay_file_path}' -filter_complex '[0:v][1:v]overlay=50:50' -c:a copy '{concat_file_path}'"
                render_commands.append(new_render_command)
                new_concat_command = f"file '{concat_file_path}'"
                concat_commands.append(new_concat_command)

                if "win" in action.keys():
                    win_team = (
                        our_team["short_name"]
                        if action["win"]
                        else opponent_team["short_name"]
                    )
                    for team in game["sets"][-1]:
                        if team["team"] == win_team:
                            team["value"] += 1
                            break
                    serve_team_name = win_team
                index += 1

    render_path = os.path.join(output_folder_path, "render.sh")

    with open(render_path, "w") as file:
        file.write("\n".join(render_commands))

    concat_path = os.path.join(output_folder_path, "concat.txt")

    with open(concat_path, "w") as file:
        file.write("\n".join(concat_commands))

    render_command = f"bash '{render_path}'"

    subprocess.run(render_command, shell=True, check=True)

    concat_command = f"ffmpeg -f concat -safe 0 -i '{os.path.join(output_folder_path, 'concat.txt')}' -c copy '{os.path.join(output_folder_path, f'{new_folder_name}.mp4')}'"

    subprocess.run(concat_command, shell=True, check=True)


edit_video(
    "/home/hugo/Desktop/video volley/Match Retour | Pont St Maxence 1 - Reims 3/edit_info.json"
)
