import csv


def csv2po(filepath: str, outfile: str):
    count = 0
    csv_dict = {}

    # csv_reader를 enumerate하고나면 csv_reader가 비어버림
    # csv_dict용으로 따로 읽어야함
    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            # 이미 딕셔너리에 값이 있으면 번역이 중복으로 들어간 경우
            if csv_dict.get(row[0]):
                print(f"csv file의 '{row[0]}'가 중복으로 들어가 있습니다.")
                count += 1
            else:
                csv_dict[row[0]] = row[1]

    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        with open(outfile, "w") as po_file:
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue

                # msg도 영어로 들어가 번역이 필요 없는 경우
                if row[0] == row[1]:
                    continue

                po_file.write(f'msgctxt "abler"\n')
                po_file.write(f'msgid "{row[0]}"\n')
                po_file.write(f'msgstr "{row[1]}"\n\n\n')
        
    print(f"total {count} mismatch")


# ko.po file 검수용
def match_po_with_csv(csvfile: str, pofile: str):
    with open(pofile, "r") as po_file:
        with open(csvfile, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_dict = {row[0]: row[1] for row in csv_reader}
            msg_to_check = None
            err_count = 0

            big_list = []
            small_list = []
            lst_count = 0
            for line in po_file:
                if line == "\n":
                    lst_count += 1
                else:
                    small_list.append(line[:-1])
                
                # 띄어쓰기 2번이면 다른 번역 영역으로 간주
                if lst_count == 2:
                    big_list.append(small_list)
                    lst_count = 0
                    small_list = []

            for big_line in big_list:

                # 'msgctxt "abler"'가 아니면 pass
                if not big_line[0].startswith('msgctxt "abler"'):
                    continue

                if big_line[1].startswith("msgid"):
                    msgid = big_line[1].split('"')[1]
                    if msgid in csv_dict:
                        msg_to_check = csv_dict[msgid]
                if big_line[2].startswith("msgstr") and msg_to_check:
                    msgstr = big_line[2].split('"')[1]
                    if msgstr != msg_to_check:
                        print(f"PO file의 '{msgstr}'가 CSV파일의 '{msg_to_check}'와 일치하지 않습니다.")
                        err_count += 1
                    msg_to_check = None
        
            print(f"total {err_count} mismatch")


if __name__ == "__main__":
    # csv2po("test.csv", "output.po")
    match_po_with_csv("test.csv", "output.po")
