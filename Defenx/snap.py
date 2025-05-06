import difflib

class Snapanalyser:
    def __init__(self):
        pass

    def load_file_content(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def compare_snapshots(self,original_snapshot, current_snapshot):
        diff = difflib.unified_diff(original_snapshot, current_snapshot, lineterm='')
        changes = list(diff)
        return changes
    
# snapanalyser = Snapanalyser()
# original = snapanalyser.load_file_content('original.txt')
# with open('original.txt', 'a', encoding='utf-8') as file:
#         file.write("\n<!-- Unauthorized Change -->\n")
# current = snapanalyser.load_file_content('original.txt')
# differences = snapanalyser.compare_snapshots(original, current)
# for line in differences:
#     print(line)