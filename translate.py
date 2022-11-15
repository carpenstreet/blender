import csv, sys, os


def csv2po(filepath: str, outfile: str):
    count = 0
    csv_dict = {}

    # csv_reader를 enumerate하고나면 csv_reader가 비어버림
    # csv_dict용으로 따로 읽어야함
    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        
        for row in csv_reader:
            if csv_dict.get(row[1]):
                # 번역이 중복이고 값은 다른 경우
                if row[2] != csv_dict.get(row[1])[1]:
                    print(f"csv file의 '{row[1]}'가 중복으로 들어가 있습니다.")
                    count += 1
                # 번역이 중복이고 값도 같은 경우
                else:
                    pass
            else:
                csv_dict[row[1]] = (row[0],row[2])

    with open(outfile, "w") as po_file:
        for i, (key, value) in enumerate(csv_dict.items()):
            if i == 0:
                continue

            # msg도 영어로 들어가 번역이 필요 없는 경우
            if key == value[1]:
                continue
            
            # "툴팁"일 때만 msgctxt "abler" pass
            if value[0] != "툴팁":
                po_file.write(f'msgctxt "abler"\n')
            po_file.write(f'msgid "{key}"\n')
            po_file.write(f'msgstr "{value[1]}"\n\n\n')
        
    print(f"total {count} mismatch")


# ko.po file 검수용
def match_po_with_csv(csvfile: str, pofile: str):
    with open(pofile, "r") as po_file:
        with open(csvfile, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            csv_dict = {row[0]: row[1] for row in csv_reader}
            msg_to_check = None
            err_count = 0

            trans_body_all = []
            trans_body = []
            lst_count = 0
            for line in po_file:
                if line == "\n":
                    lst_count += 1
                else:
                    trans_body.append(line[:-1])
                
                # 띄어쓰기 2번이면 다른 번역 영역으로 간주
                if lst_count == 2:
                    trans_body_all.append(trans_body)
                    lst_count = 0
                    trans_body = []

            for trans_item in trans_body_all:
                if trans_item[0].startswith('msgctxt "abler"'):
                    original_word = trans_item[1]
                    translated_word = trans_item[2]
                else:
                    original_word = trans_item[0]
                    translated_word = trans_item[1]

                if original_word.startswith("msgid"):
                    msgid = original_word.split('"')[1]
                    if msgid in csv_dict:
                        msg_to_check = csv_dict[msgid]
                if translated_word.startswith("msgstr") and msg_to_check:
                    msgstr = translated_word.split('"')[1]
                    if msgstr != msg_to_check:
                        print(f"PO file의 '{msgstr}'가 CSV파일의 '{msg_to_check}'와 일치하지 않습니다.")
                        err_count += 1
                    msg_to_check = None
        
            print(f"total {err_count} mismatch")


def check_file_exist(filepath):
    if not os.path.isfile(filepath):
        print(f"{filepath} 파일이 없습니다.")
        return False
    return True


if __name__ == "__main__":
    if sys.argv[1] == "--generate" and len(sys.argv)>2:
        input_csv = sys.argv[2]
        if check_file_exist(input_csv):
            csv2po(input_csv, "output.po")
    
    elif sys.argv[1] == "--test" and len(sys.argv)>3:
        input_csv = sys.argv[2]
        output_po = sys.argv[3]
        if check_file_exist(input_csv) and check_file_exist(output_po):    
            match_po_with_csv(input_csv, output_po)

    else:
        print("인자 확인")
