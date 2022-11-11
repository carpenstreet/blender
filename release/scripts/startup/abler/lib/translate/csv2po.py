import csv


def csv2po(filepath: str, outfile: str):
    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        with open(outfile, "w") as po_file:
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue
                po_file.write(f'msgctxt "abler"\n')
                po_file.write(f'msgid "{row[0]}"\n')
                po_file.write(f'msgstr "{row[1]}"\n\n\n')


# po file 검수용
def match_po_with_csv(csvfile: str, pofile: str):
    with open(pofile, "r") as po_file:
        with open(csvfile, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_dict = {row[0]: row[1] for row in csv_reader}
            msg_to_check = None
            count = 0
            for line in po_file:
                if line.startswith("msgid"):
                    msgid = line.split('"')[1]
                    if msgid in csv_dict:
                        msg_to_check = csv_dict[msgid]
                elif line.startswith("msgstr") and msg_to_check:
                    msgstr = line.split('"')[1]
                    if msgstr != msg_to_check:
                        print(
                            f"PO file의 '{msgstr}'가 CSV파일의 '{msg_to_check}'와 일치하지 않습니다."
                        )
                        count += 1
                    msg_to_check = None
            print(f"total {count} mismatch")


if __name__ == "__main__":
    # csv2po("test.csv", "output.po")
    match_po_with_csv("test.csv", "output.po")
