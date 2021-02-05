import re
from pathlib import Path

import pandas as pd
import simplekml

import settings
from configs import get_patterns
from extract_and_rename import unzip_files
from header_getter import HeaderResolver

base_path = Path(__file__).parent.resolve(strict=True)


def kml_gen(
    df,
    file_stem,
    conf,
    coordinates,
):
    longitude, latitude = coordinates
    df = df[df[longitude] != 0]
    df = df[df[latitude] != 0]
    to_bin = lambda x: round(x, 4)
    df["lonbin"] = df[longitude].map(to_bin)
    df["latbin"] = df[latitude].map(to_bin)
    df.dropna(subset=[conf.param], inplace=True)
    if conf.channel is not None:
        groups = df.groupby(
            ["lonbin", "latbin", conf.channel, conf.bsic_sc_pci],
            as_index=False,
        )[[conf.param, longitude, latitude]].mean()
        to_kml = groups[
            [longitude, latitude, conf.channel, conf.bsic_sc_pci, conf.param]
        ]
    else:
        groups = df.groupby(
            ["lonbin", "latbin", conf.bsic_sc_pci], as_index=False
        )[[conf.param, longitude, latitude]].mean()
        to_kml = groups[[longitude, latitude, conf.bsic_sc_pci, conf.param]]
    to_kml = to_kml.round({conf.param: 1, longitude: 5, latitude: 5})
    styles = list()
    for legend_style in conf.legend:
        sharedstyle = simplekml.Style()
        sharedstyle.iconstyle.scale = 0.4
        sharedstyle.iconstyle.icon.href = settings.ICON
        sharedstyle.labelstyle.scale = 0.8
        sharedstyle.iconstyle.color = legend_style[1]
        sharedstyle.labelstyle.color = legend_style[1]
        styles.append((legend_style[0], sharedstyle))

    kml = simplekml.Kml()
    for index, row in to_kml.iterrows():
        bsic_sc_pci_val = row[conf.bsic_sc_pci]
        if type(bsic_sc_pci_val) != str:
            cell_ph_id = int(bsic_sc_pci_val)
        else:
            cell_ph_id = bsic_sc_pci_val
        if conf.channel is not None:
            pnt = kml.newpoint(
                name=f"{row[conf.param]:g}",
                coords=[(row[longitude], row[latitude])],
                description=f"{conf.channel}: {int(row[conf.channel])}"
                + f"\n{conf.bsic_sc_pci}: {cell_ph_id}",
            )
        else:
            pnt = kml.newpoint(
                name=f"{row[conf.param]:g}",
                coords=[(row[longitude], row[latitude])],
                description=f"{conf.bsic_sc_pci}: {cell_ph_id}",
            )
        if conf.param in ("RxQual Sub",):
            for style in styles:
                if row[conf.param] >= style[0]:
                    pnt.style = style[1]
                    break
        elif conf.param in ("PCI_PARAM",):
            pnt.style = styles[int(row[conf.param])][1]
        else:
            for style in styles:
                if row[conf.param] < style[0]:
                    pnt.style = style[1]
                    break
    kml.savekmz(
        base_path.joinpath(
            settings.RESULT_FOLDER, f"{file_stem}_{conf.name_suffix}"
        ).with_suffix(".kmz"),
        format=False,
    )


def add_duplicate_column(df, duplicate_pattern_name):
    pattern, new_name = duplicate_pattern_name
    columns = df.columns
    for header in columns:
        if re.search(pattern, header):
            df[new_name] = df[header]
            break
    return df


def from_txt_to_kml(txt_file, duplicate_pattern_name=None):
    file_stem = txt_file.stem
    df = pd.read_table(txt_file).dropna(how="all")
    if duplicate_pattern_name:
        df = add_duplicate_column(df, duplicate_pattern_name)
    patterns = get_patterns()
    resolver = HeaderResolver(df.columns, patterns, duplicate_pattern_name)
    coordinates = resolver.choose_coordinates_headers()
    confs = resolver.fill_confs()
    for conf in confs:
        kml_gen(df, file_stem, conf, coordinates)


if __name__ == "__main__":
    unzip_files()
    duplicate_pattern_name = None  # ("Cell", "PCI_PARAM")
    for file in base_path.joinpath(settings.INPUT_LOGS_FOLDER).iterdir():
        if file.suffix in (".txt", ".TXT"):
            from_txt_to_kml(file, duplicate_pattern_name)
