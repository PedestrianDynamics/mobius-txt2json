"""Parser  of trajectory data from a .txt file into a JSON format for Mobius."""
import math
import json
import pandas as pd
import typer

app = typer.Typer()

def parse_txt_with_pandas(file_path):
    fps = 25  # Default FPS
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("#"):
                if "framerate" in line.lower():
                    fps = int(line.split(":")[1].strip().split()[0])

            else:
                break

    df = pd.read_csv(
        file_path,
        sep="\t",
        comment="#",
        names=["id", "frame", "x", "y", "z"])

    return df, fps


def convert_df_to_json_optimized(df, fps, default_mode):
    time_step = 1 / fps

    df["time"] = df["frame"] * time_step

    df["dx"] = df.groupby("id")["x"].diff().fillna(0)
    df["dy"] = df.groupby("id")["y"].diff().fillna(0)
    df["distance"] = (df["dx"] ** 2 + df["dy"] ** 2).pow(0.5)
    df["speed"] = df["distance"] / time_step
    df["rotation"] = df.apply(
        lambda row: math.degrees(math.atan2(row["dy"], row["dx"]))
        if row["distance"] > 0
        else 0.0,
        axis=1,
    )
    max_speeds = df.groupby("id")["speed"].max()
    # Construct entities block
    entities = [
        {
            "id": int(entity_id) - 1,
            "name": f"Agent{int(entity_id)}",
            "simTimeS": "0.0",
            "max_speed": round(max_speed, 3),
            "m_plane": "F#0",
            "map": 0,
        }
        for entity_id, max_speed in max_speeds.items()
    ]

    # Construct simulation block
    simulation = []
    for time, group in df.groupby("time"):
        samples = group.apply(
            lambda row: {
                "entity": int(row["id"]) - 1,
                "position": {"x": row["x"], "y": row["y"], "z": row["z"]},
                "mode": default_mode,
                "rotation": row["rotation"],
                "speed": row["speed"],
            },
            axis=1,
        ).tolist()
        simulation.append({"time": time, "samples": samples})

    # Construct metadata block
    duration = df["time"].max()
    metadata = {
        "duration": duration,
        "used_planes": ["F#0"],
        "distance_maps_used": [
            {
                "index": 0,
                "name": "Default Distance Map",
                "num_users": len(entities),
                "use_ground": 0,
                "ground_elevation": 0.0,
                "people_density_catg_num": 2,
            }
        ],
        "timestamp_geometry": 0,
        "timestamp_people": 0,
        "timestamp_exits_links": 0,
        "model_GUID": "",
        "sampling_rate": round(time_step, 3),
        "max_num_entities": len(entities),
        "isSI": True,
        "isDeg": True,
    }

    return {"entities": entities, "simulation": simulation, "metadata": metadata}

@app.command()
def main(
    file_path: str = typer.Argument(..., help="Path to the trajectory TXT file."),
    default_mode: str = typer.Option("LF#0", help="Default mode for simulation entities."),
    output_file: str = typer.Option("output.json", help="Path to the output JSON file.")
):
    try:
        trajectory_df, fps = parse_txt_with_pandas(file_path)
        json_result = convert_df_to_json_optimized(trajectory_df, fps, default_mode)
        with open(output_file, "w") as outfile:
            json.dump(json_result, outfile, indent=4)
        print(f"JSON file saved to {output_file}")
    except FileNotFoundError:
        print("File not found. Please provide the correct file path.")

if __name__ == "__main__":
    app()
    
